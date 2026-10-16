"""Live / paper trading loop.

One ``tick`` per poll interval:
1. Read dashboard controls (kill switch, pause) and publish a heartbeat.
2. Pull LTPs; let the paper broker trigger resting stops.
3. Manage open positions: broker-side stop filled? target reached? software stop?
4. Enforce the daily loss limit, kill switch and 3:05 PM flatten.
5. On each newly completed bar: strategy -> LLM review -> risk -> entry order
   -> protective stop order at the broker.

Every step is journaled. Exits never go through the LLM.
"""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Protocol

from .broker.base import Broker, BrokerError
from .broker.paper import PaperBroker
from .clock import MarketClock, now_ist, to_ist
from .compliance import OrderRefGenerator
from .config import Settings
from .costs import CostModel
from .data import MarketData
from .llm.filter import SignalFilter
from .llm.types import LLMDecision, ReviewContext
from .models import (
    ClosedTrade,
    ManagedPosition,
    Order,
    OrderRequest,
    OrderStatus,
    OrderType,
    Side,
    Signal,
)
from .risk import RiskManager
from .store import CompositeStore, new_id
from .strategy import build_strategy, catalog
from .strategy.base import Strategy

log = logging.getLogger(__name__)

TICK = 0.05  # multiples of 0.05 are valid on every NSE equity tick-size band


def round_tick(price: float, up: bool) -> float:
    n = price / TICK
    n = math.ceil(n - 1e-9) if up else math.floor(n + 1e-9)
    return round(n * TICK, 2)


class Quotes(Protocol):
    def ltp(self, symbols: list[str]) -> dict[str, float]: ...


@dataclass
class EngineState:
    day: date | None = None
    last_bar: datetime | None = None
    kill_handled: bool = False
    login_wait_logged: bool = False
    consecutive_errors: int = 0


class TradingEngine:
    MAX_CONSECUTIVE_ERRORS = 5

    def __init__(
        self,
        settings: Settings,
        broker: Broker,
        quotes: Quotes,
        data: MarketData,
        strategy: Strategy,
        signal_filter: SignalFilter,
        store: CompositeStore,
        mode: str,
        clock: MarketClock | None = None,
        costs: CostModel | None = None,
        now_fn: Callable[[], datetime] = now_ist,
        sleep_fn: Callable[[float], None] = time.sleep,
        before_market_tick: Callable[[datetime], None] | None = None,
        require_login_confirmation: bool = False,
        filter_factory: Callable[[Settings], SignalFilter] | None = None,
        equity_interval_seconds: float = 60.0,
    ) -> None:
        self.base_settings = settings  # env-loaded; dashboard overrides are always applied on top of this
        self.s = settings
        self.broker = broker
        self.quotes = quotes
        self.data = data
        self.strategy = strategy
        self.filter = signal_filter
        self.store = store
        self.mode = mode
        self.clock = clock or settings.clock()
        self.costs = costs or CostModel()
        self.now = now_fn
        self.sleep = sleep_fn
        # Called on every market-hours tick, e.g. to swap in a fresh broker token after the 6 AM expiry.
        self.before_market_tick = before_market_tick
        # Daily 2FA policy: no new entries until an operator confirms today's login.
        self.require_login_confirmation = require_login_confirmation
        self.risk = RiskManager(settings, self.clock)
        self.refs = OrderRefGenerator()
        self.positions: dict[str, ManagedPosition] = {}
        self.state = EngineState()
        self._prior_bars: dict[str, list] = {}
        self._last_prices: dict[str, float] = {}
        self.filter_factory = filter_factory
        self._applied_overrides: dict | None = None
        # Every signal is tracked virtually to its stop/target/EOD so the journal holds an outcome for
        # signals that were vetoed or never filled too. That is what measures whether the LLM adds value.
        self._shadows: dict[str, dict] = {}
        self.equity_interval = timedelta(seconds=equity_interval_seconds)
        self._last_equity_at: datetime | None = None

    def publish_static(self) -> None:
        self.store.set_control("strategy_catalog", catalog())
        self.store.set_control("effective_settings", {**self.s.public_view(), "rejected": {}})

    # Main loop

    def run_forever(self) -> None:
        self.store.event("engine_start", f"engine started in {self.mode} mode", symbols=self.s.symbols)
        self.publish_static()
        self.reconcile()
        while True:
            try:
                self.tick()
                self.state.consecutive_errors = 0
            except KeyboardInterrupt:
                self.store.event("engine_stop", "interrupted by operator")
                raise
            except Exception as e:  # keep running, but fail safe after repeated errors
                self.state.consecutive_errors += 1
                log.exception("tick failed")
                self.store.event("error", f"tick failed: {e}", count=self.state.consecutive_errors)
                if self.state.consecutive_errors >= self.MAX_CONSECUTIVE_ERRORS:
                    self.store.set_control("kill_switch", True)
                    self.store.event("kill_switch", "engaged after repeated errors")
                    try:
                        self.flatten_all("error_kill_switch")
                    except Exception:
                        log.exception("flatten after errors failed - MANUAL INTERVENTION REQUIRED")
            self.sleep(self.s.poll_seconds)

    def reconcile(self) -> None:
        """Report broker positions the engine does not manage (e.g. manual trades). Never touches them."""
        try:
            for p in self.broker.positions():
                if p.symbol not in self.positions:
                    self.store.event("unmanaged_position", f"{p.symbol} {p.product.value} qty={p.qty} is not managed by the engine",
                                     symbol=p.symbol, qty=p.qty, product=p.product.value)
        except BrokerError as e:
            self.store.event("error", f"reconcile failed: {e}")

    def tick(self) -> None:
        now = to_ist(self.now())
        self._roll_day(now)
        control = self.store.get_control()
        self._apply_overrides(control.get("settings_overrides") or {})
        try:
            self._tick(now, control)
        finally:
            self._publish_heartbeat(now, control)

    def _unrealized(self) -> float:
        return sum(p.unrealized(self._last_prices.get(s, p.entry_price)) for s, p in self.positions.items())

    def _publish_heartbeat(self, now: datetime, control: dict) -> None:
        positions = []
        for sym, p in self.positions.items():
            ltp = self._last_prices.get(sym, p.entry_price)
            positions.append({
                "symbol": sym, "side": p.side.value, "qty": p.qty, "entry": p.entry_price, "stop": p.stop,
                "target": p.target, "ltp": ltp, "unrealized": round(p.unrealized(ltp), 2),
                "opened_at": p.opened_at.isoformat(), "product": p.product.value,
            })
        unrealized = self._unrealized()
        self.store.set_control("heartbeat", {
            "at": now.isoformat(), "wall_at": now_ist().isoformat(), "mode": self.mode, "strategy": self.s.strategy,
            "open_positions": len(self.positions), "positions": positions,
            "realized_pnl": round(self.risk.state.realized_pnl, 2), "unrealized_pnl": round(unrealized, 2),
            "trades_today": self.risk.state.trades_opened, "halted": self.risk.state.halted,
            "halt_reason": self.risk.state.halt_reason, "market_open": self.clock.is_market_open(now),
            "capital": self.s.capital, "llm_enabled": self.filter.enabled,
            "reviewer": getattr(self.filter, "label", "none"),
        })
        if self.clock.is_market_open(now) and (
            self._last_equity_at is None or now - self._last_equity_at >= self.equity_interval
        ):
            self._last_equity_at = now
            self.store.insert("equity", {
                "at": now.isoformat(), "mode": self.mode, "realized_pnl": round(self.risk.state.realized_pnl, 2),
                "unrealized_pnl": round(unrealized, 2), "open_positions": len(self.positions),
            })

    def _apply_overrides(self, overrides: dict) -> None:
        if overrides == self._applied_overrides:
            return
        first = self._applied_overrides is None
        self._applied_overrides = overrides
        new, rejected = self.base_settings.with_overrides(overrides)
        old = self.s
        self.s = new
        self.risk.s = new
        self.clock = new.clock()
        self.risk.clock = self.clock
        if (new.strategy, new.strategy_params, new.allow_short) != (old.strategy, old.strategy_params, old.allow_short):
            fired = getattr(self.strategy, "_fired", set())
            self.strategy = build_strategy(new.strategy, new.strategy_params, new.allow_short)
            # Keep "one signal per symbol per day" across a mid-day strategy switch.
            if hasattr(self.strategy, "_fired"):
                self.strategy._fired = set(fired)
        if self.filter_factory is not None and new.llm_enabled != old.llm_enabled:
            self.filter = self.filter_factory(new)
        elif hasattr(self.filter, "s"):
            self.filter.s = new
        self.store.set_control("effective_settings", {**new.public_view(), "rejected": rejected})
        if overrides or not first:
            self.store.event("settings_applied", "dashboard settings applied" + (f"; rejected: {rejected}" if rejected else ""),
                             overrides=overrides, rejected=rejected)

    def _tick(self, now: datetime, control: dict) -> None:
        kill = bool(control.get("kill_switch"))
        paused = bool(control.get("paused"))
        if not self.clock.is_market_open(now):
            return
        if self.before_market_tick is not None:
            self.before_market_tick(now)

        symbols = sorted(set(self.s.symbols) | set(self.positions))
        prices = self.quotes.ltp(symbols)
        self._last_prices.update(prices)
        if isinstance(self.broker, PaperBroker):
            for sym, px in prices.items():
                self.broker.update_price(sym, px)

        self._manage_positions(now)
        self._update_shadows(now)

        unrealized = self._unrealized()
        was_halted = self.risk.state.halted
        if self.risk.check_daily_loss(unrealized) and not was_halted:
            self.store.event("halt", self.risk.state.halt_reason)

        if kill and not self.state.kill_handled:
            self.store.event("kill_switch", "kill switch engaged from control plane; flattening")
            self.state.kill_handled = True
        elif not kill:
            self.state.kill_handled = False

        # Flatten conditions are re-checked every tick, so a failed exit is retried until the book is flat.
        eod = self.clock.should_flatten(now)
        reason = "eod_flatten" if eod else "kill_switch" if kill else "daily_loss_halt" if self.risk.state.halted else None
        if reason and self.positions:
            self.flatten_all(reason)
        if eod:
            self._close_all_shadows(now, "eod")
            return

        bar_start = self.clock.last_completed_bar_start(now, self.s.interval_minutes)
        if bar_start is None or bar_start == self.state.last_bar:
            return
        self.state.last_bar = bar_start
        if kill or paused or self.risk.state.halted:
            return
        if self.require_login_confirmation and control.get("login_confirmed_for") != now.date().isoformat():
            if not self.state.login_wait_logged:
                self.store.event("login_confirmation_required",
                                 f"no new entries until today's login ({now.date()}) is confirmed")
                self.state.login_wait_logged = True
            return
        self._scan_for_entries(now, bar_start)

    def _roll_day(self, now: datetime) -> None:
        if self.state.day != now.date():
            if self._shadows:
                self._close_all_shadows(now, "eod")
            self.state = EngineState(day=now.date())
            self.risk.roll_day(now)
            self.strategy.reset_day()
            self._prior_bars.clear()

    # Entries

    def _session_bars(self, symbol: str, now: datetime, bar_start: datetime):
        open_dt = self.clock.session_open(now.date())
        end = bar_start + timedelta(minutes=self.s.interval_minutes)
        bars = self.data.candles(symbol, self.s.interval_minutes, open_dt, end)
        return [b for b in bars if b.ts <= bar_start]  # completed bars only

    def _prior(self, symbol: str, now: datetime):
        if symbol not in self._prior_bars:
            end = self.clock.session_open(now.date())
            try:
                bars = self.data.candles(symbol, self.s.interval_minutes, end - timedelta(days=8), end)
            except Exception as e:
                log.warning("prior bars for %s unavailable: %s", symbol, e)
                bars = []
            self._prior_bars[symbol] = bars[-400:]
        return self._prior_bars[symbol]

    def _scan_for_entries(self, now: datetime, bar_start: datetime) -> None:
        for symbol in self.s.symbols:
            if symbol in self.positions:
                continue
            bars = self._session_bars(symbol, now, bar_start)
            if not bars or bars[-1].ts != bar_start:
                continue  # data not caught up yet; strategy only fires on the fresh bar
            signal = self.strategy.on_bar(symbol, bars, self._prior(symbol, now))
            if signal is None:
                continue
            self._handle_signal(signal, bars, now)

    def _handle_signal(self, signal: Signal, bars: list, now: datetime) -> None:
        signal_id = new_id()
        self.store.insert("signals", {
            "id": signal_id, "symbol": signal.symbol, "side": signal.side, "product": signal.product,
            "strategy": signal.strategy, "signal_ts": signal.ts, "entry": signal.entry, "stop": signal.stop,
            "target": signal.target, "reason": signal.reason, "features": signal.features, "mode": self.mode,
        })

        decision: LLMDecision | None = None
        if self.filter.enabled:
            ctx = ReviewContext(
                signal=signal,
                recent_bars=bars[-12:],
                open_positions=[
                    {"symbol": p.symbol, "side": p.side.value, "qty": p.qty, "entry": p.entry_price}
                    for p in self.positions.values()
                ],
                day_realized_pnl=self.risk.state.realized_pnl,
                trades_today=self.risk.state.trades_opened,
            )
            decision = self.filter.review(ctx)
            self.store.insert("llm_decisions", {
                "signal_id": signal_id, "symbol": signal.symbol, "approve": decision.approve,
                "size_multiplier": decision.size_multiplier, "confidence": decision.confidence,
                "rationale": decision.rationale, "risk_flags": decision.risk_flags, "model": decision.model,
                "latency_ms": decision.latency_ms, "input_tokens": decision.input_tokens,
                "output_tokens": decision.output_tokens, "error": decision.error,
                "request_id": decision.request_id, "prompt": decision.prompt,
            })

        verdict = self.risk.evaluate(
            signal, decision, self.positions, now,
            kill_switch=bool(self.store.get_control().get("kill_switch")),
            available_cash=self.broker.available_cash(),
        )
        self.store.insert("events", {
            "kind": "risk_verdict", "message": "approved" if verdict.approved else "; ".join(verdict.reasons),
            "data": {"signal_id": signal_id, "qty": verdict.qty, "size_multiplier": verdict.size_multiplier},
        })
        self._shadows[signal_id] = {
            "signal_id": signal_id, "symbol": signal.symbol, "strategy": signal.strategy, "side": signal.side.value,
            "entry": signal.entry, "stop": signal.stop, "target": signal.target, "signal_ts": signal.ts.isoformat(),
            "llm_decision": "none" if decision is None else ("approve" if decision.approve else "reject"),
            "llm_size_multiplier": None if decision is None else decision.size_multiplier,
            "risk_approved": verdict.approved,
        }
        if verdict.approved:
            self._enter(signal, verdict.qty, signal_id, now)

    def _enter(self, signal: Signal, qty: int, signal_id: str, now: datetime) -> None:
        ltp = self._last_prices.get(signal.symbol, signal.entry)
        buy = signal.side is Side.BUY
        if (buy and not (signal.stop < ltp < signal.target)) or (not buy and not (signal.target < ltp < signal.stop)):
            self.store.event("entry_skipped", f"{signal.symbol}: LTP {ltp} already outside stop/target", signal_id=signal_id)
            return
        band = self.s.price_protection_pct / 100
        limit = round_tick(ltp * (1 + band), up=True) if buy else round_tick(ltp * (1 - band), up=False)
        req = OrderRequest(signal.symbol, signal.side, qty, signal.product, OrderType.LIMIT, price=limit,
                           reference_id=self.refs.next(now), exchange=self.s.exchange)
        order = self._submit(req, signal_id, "entry")
        if order is None:
            return
        order = self._await_fill(order)
        if order.status is not OrderStatus.FILLED and order.filled_qty == 0:
            self._cancel(order, signal_id)
            self.store.event("entry_unfilled", f"{signal.symbol}: entry not filled in time; cancelled", signal_id=signal_id)
            return
        if order.status is OrderStatus.PARTIAL:
            self._cancel(order, signal_id)
        filled_qty = order.filled_qty or qty
        entry_price = order.avg_price or limit
        pos = ManagedPosition(
            symbol=signal.symbol, side=signal.side, product=signal.product, qty=filled_qty,
            entry_price=entry_price, stop=signal.stop, target=signal.target, opened_at=now,
            entry_order_id=order.order_id, signal_id=signal_id,
            entry_costs=self.costs.leg(signal.side, filled_qty, entry_price, signal.product),
        )
        self.positions[signal.symbol] = pos
        self.risk.record_open()
        self.store.event("position_opened", f"{signal.side.value} {filled_qty} {signal.symbol} @ {entry_price}",
                         signal_id=signal_id, symbol=signal.symbol)

        # Protective stop at the broker, so the position stays protected if this process dies.
        exit_side = signal.side.opposite()
        buffer = self.s.stop_limit_buffer_pct / 100
        trigger = round_tick(signal.stop, up=not buy)
        stop_limit = round_tick(trigger * (1 - buffer), up=False) if buy else round_tick(trigger * (1 + buffer), up=True)
        stop_req = OrderRequest(signal.symbol, exit_side, filled_qty, signal.product, OrderType.SL, price=stop_limit,
                                trigger_price=trigger, reference_id=self.refs.next(now), exchange=self.s.exchange)
        stop_order = self._submit(stop_req, signal_id, "stop")
        if stop_order is None or stop_order.status is OrderStatus.REJECTED:
            self.store.event("stop_failed", f"{signal.symbol}: protective stop could not be placed; exiting", signal_id=signal_id)
            self._exit(pos, "stop_placement_failed", now)
            return
        pos.stop_order_id = stop_order.order_id

    # Position management

    def _manage_positions(self, now: datetime) -> None:
        for symbol, pos in list(self.positions.items()):
            if pos.stop_order_id:
                try:
                    st = self.broker.order_status(pos.stop_order_id)
                except BrokerError as e:
                    self.store.event("error", f"stop status for {symbol} failed: {e}")
                    st = None
                if st is not None and st.status is OrderStatus.FILLED:
                    self._log_order(st, pos.signal_id, "stop")
                    self._record_close(pos, st.avg_price or pos.stop, "stop", now)
                    continue
            ltp = self._last_prices.get(symbol)
            if ltp is None:
                continue
            long = pos.side is Side.BUY
            if (long and ltp >= pos.target) or (not long and ltp <= pos.target):
                self._exit(pos, "target", now)
            elif (long and ltp <= pos.stop) or (not long and ltp >= pos.stop):
                # Broker stop should have fired; SL-limit can be skipped on a fast move.
                self._exit(pos, "stop_soft", now)

    def _update_shadows(self, now: datetime) -> None:
        for sid, sh in list(self._shadows.items()):
            ltp = self._last_prices.get(sh["symbol"])
            if ltp is None:
                continue
            long = sh["side"] == "BUY"
            if (long and ltp <= sh["stop"]) or (not long and ltp >= sh["stop"]):
                self._close_shadow(sid, sh["stop"], "stop", now)
            elif (long and ltp >= sh["target"]) or (not long and ltp <= sh["target"]):
                self._close_shadow(sid, sh["target"], "target", now)

    def _close_all_shadows(self, now: datetime, outcome: str) -> None:
        for sid, sh in list(self._shadows.items()):
            self._close_shadow(sid, self._last_prices.get(sh["symbol"], sh["entry"]), outcome, now)

    def _close_shadow(self, sid: str, exit_price: float, outcome: str, now: datetime) -> None:
        sh = self._shadows.pop(sid)
        risk = abs(sh["entry"] - sh["stop"]) or 1e-9
        sign = 1 if sh["side"] == "BUY" else -1
        self.store.insert("signal_outcomes", {
            **sh, "exit_price": round(exit_price, 2), "outcome": outcome, "closed_at": now.isoformat(),
            "r_multiple": round((exit_price - sh["entry"]) * sign / risk, 3), "mode": self.mode,
        })

    def flatten_all(self, reason: str) -> None:
        now = to_ist(self.now())
        for pos in list(self.positions.values()):
            self._exit(pos, reason, now)

    def _exit(self, pos: ManagedPosition, reason: str, now: datetime) -> None:
        if pos.stop_order_id:
            try:
                st = self.broker.order_status(pos.stop_order_id)
                if st.status is OrderStatus.FILLED:
                    self._record_close(pos, st.avg_price or pos.stop, "stop", now)
                    return
                if not st.status.is_terminal:
                    self._cancel(self.broker.cancel_order(pos.stop_order_id), pos.signal_id, already=True)
                    st = self.broker.order_status(pos.stop_order_id)
                    if st.status is OrderStatus.FILLED:  # filled while cancelling
                        self._record_close(pos, st.avg_price or pos.stop, "stop", now)
                        return
            except BrokerError as e:
                self.store.event("error", f"{pos.symbol}: stop cancel failed: {e}")

        side = pos.side.opposite()
        buy = side is Side.BUY
        for attempt, band_mult in enumerate((1, 2, 4), start=1):
            ltp = self._last_prices.get(pos.symbol, pos.entry_price)
            try:
                ltp = self.quotes.ltp([pos.symbol]).get(pos.symbol, ltp)
            except Exception:
                pass
            band = self.s.price_protection_pct / 100 * band_mult
            limit = round_tick(ltp * (1 + band), up=True) if buy else round_tick(ltp * (1 - band), up=False)
            req = OrderRequest(pos.symbol, side, pos.qty, pos.product, OrderType.LIMIT, price=limit,
                               reference_id=self.refs.next(now), exchange=self.s.exchange)
            order = self._submit(req, pos.signal_id, f"exit:{reason}")
            if order is None:
                continue
            order = self._await_fill(order)
            if order.status is OrderStatus.FILLED:
                self._record_close(pos, order.avg_price or limit, reason, now)
                return
            self._cancel(order, pos.signal_id)
            self.store.event("exit_retry", f"{pos.symbol}: exit attempt {attempt} unfilled", symbol=pos.symbol)
        self.store.event("exit_failed", f"{pos.symbol}: EXIT FAILED after retries - MANUAL INTERVENTION REQUIRED",
                         symbol=pos.symbol, qty=pos.qty)

    def _record_close(self, pos: ManagedPosition, price: float, reason: str, now: datetime) -> None:
        self.positions.pop(pos.symbol, None)
        costs = self.costs.round_trip(pos.side, pos.qty, pos.entry_price, price, pos.product)
        trade = ClosedTrade(pos.symbol, pos.side, pos.product, pos.qty, pos.entry_price, price,
                            pos.opened_at, now, reason, costs, self.strategy.name, pos.signal_id)
        self.risk.record_close(trade.net_pnl)
        self.store.insert("trades", {
            "signal_id": pos.signal_id, "symbol": trade.symbol, "side": trade.side, "product": trade.product,
            "qty": trade.qty, "entry_price": trade.entry_price, "exit_price": trade.exit_price,
            "opened_at": trade.opened_at, "closed_at": trade.closed_at, "exit_reason": reason,
            "gross_pnl": round(trade.gross_pnl, 2), "costs": costs, "net_pnl": round(trade.net_pnl, 2),
            "strategy": trade.strategy, "mode": self.mode,
        })
        self.store.event("position_closed", f"{pos.symbol} closed ({reason}) net {trade.net_pnl:.2f}", symbol=pos.symbol)

    # Order plumbing

    def _submit(self, req: OrderRequest, signal_id: str | None, purpose: str) -> Order | None:
        try:
            order = self.broker.place_order(req)
        except BrokerError as e:
            self.store.event("order_error", f"{purpose} {req.symbol}: {e}", signal_id=signal_id)
            return None
        self._log_order(order, signal_id, purpose)
        if order.status is OrderStatus.REJECTED:
            self.store.event("order_rejected", f"{purpose} {req.symbol}: {order.message}", signal_id=signal_id)
        return order

    def _await_fill(self, order: Order) -> Order:
        for _ in range(max(1, int(self.s.fill_timeout_seconds))):
            if order.status.is_terminal:
                break
            self.sleep(1.0)
            try:
                order = self.broker.order_status(order.order_id)
            except BrokerError as e:
                log.warning("order status failed: %s", e)
        return order

    def _cancel(self, order: Order, signal_id: str | None, already: bool = False) -> None:
        if not already and not order.status.is_terminal:
            try:
                order = self.broker.cancel_order(order.order_id)
            except BrokerError as e:
                self.store.event("error", f"cancel {order.order_id} failed: {e}")
                return
        self._log_order(order, signal_id, "cancel")

    def _log_order(self, order: Order, signal_id: str | None, purpose: str) -> None:
        r = order.request
        self.store.insert("orders", {
            "order_id": order.order_id, "reference_id": r.reference_id, "signal_id": signal_id, "purpose": purpose,
            "symbol": r.symbol, "side": r.side, "product": r.product, "order_type": r.order_type, "qty": r.qty,
            "price": r.price, "trigger_price": r.trigger_price, "status": order.status, "filled_qty": order.filled_qty,
            "avg_price": order.avg_price, "message": order.message, "broker": self.broker.name, "mode": self.mode,
        })


def describe(engine: TradingEngine) -> dict[str, Any]:
    return {
        "mode": engine.mode,
        "positions": {s: {"side": p.side.value, "qty": p.qty, "entry": p.entry_price, "stop": p.stop, "target": p.target}
                      for s, p in engine.positions.items()},
        "realized_pnl": engine.risk.state.realized_pnl,
        "halted": engine.risk.state.halted,
    }
