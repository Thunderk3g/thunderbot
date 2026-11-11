"""Daily delivery (CNC) investing: run a daily strategy from thunderbot.daily on a paper or real account.

Once per trading day, shortly before the close (TB_INVEST_AT, default 15:10 IST), the runner:
1. loads daily history (Yahoo Finance) and appends today's live price as today's bar,
2. asks the strategy for target weights if today is a rebalance day (or nothing was ever decided),
3. checks the prices it is about to trade on (stale, missing or jumping prices stop the run),
4. optionally lets a reviewer veto the plan for a day (it can delay, never change, the trades),
5. sells what is over target, then buys what is under, in whole shares,
6. journals orders, closed trades, the plan, an equity point and a heartbeat for the dashboard.

It can be driven two ways. ``run_forever`` is the long-running worker (a laptop or a server).
``tick`` alone is one pass, for schedulers that wake the code every few minutes and keep no process
alive (a serverless function called by a cron job). Either way all state lives in the control table.

Controls (the same as the intraday engine): it trades only after "Start"; "Hold to stop" sells
everything; "Pause" keeps the holdings and makes no trades.

Timing rules. A paper run that starts late (the scheduler was delayed, the laptop was asleep) still
runs the same evening on closing prices and says so. A live run never trades after ``cutoff``
(15:25): it is marked missed, an alert goes out, and the decision is made afresh on the next
trading day. Month-end rules tolerate a day's delay; trading in a closed market does not work.
"""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable
from datetime import date, datetime, timedelta
from datetime import time as dtime
from typing import Any

from . import daily
from .clock import MARKET_CLOSE, MARKET_OPEN, MarketClock, now_ist, to_ist
from .store import CompositeStore

log = logging.getLogger(__name__)

STATE_KEY = "invest_portfolio"
SETTINGS_KEY = "invest_settings"
MAX_PRICE_JUMP = 0.15  # a live price this far from the last close is treated as a data error, not a signal
MAX_HISTORY_AGE_DAYS = 7
MAX_REVIEW_DELAYS = 2  # the reviewer may postpone a rebalance this many sessions, then the rule runs


def next_trading_day(clock: MarketClock, d: date) -> date:
    n = d + timedelta(days=1)
    while not clock.is_trading_day(n):
        n += timedelta(days=1)
    return n


class InvestRunner:
    def __init__(
        self,
        store: CompositeStore,
        quotes: Any,
        clock: MarketClock,
        capital: float,
        mode: str = "paper",
        broker: Any = None,
        strategy: str = "core_mix",
        params: dict | None = None,
        run_at: dtime = dtime(15, 10),
        history: Callable[[list[str], date, date], daily.Prices] | None = None,
        costs: daily.DeliveryCosts | None = None,
        now_fn: Callable[[], datetime] = now_ist,
        sleep_fn: Callable[[float], None] = time.sleep,
        feed_status: Callable[[], dict] | None = None,
        poll_seconds: float = 30.0,
        liquid_symbol: str = "LIQUIDCASE",
        cutoff: dtime = dtime(15, 25),
        reviewer: Any = None,
        notify: Callable[[str], None] | None = None,
        scheduler: str = "worker",
        tick_minutes: float = 0.0,
    ) -> None:
        self.store = store
        self.quotes = quotes
        self.clock = clock
        self.capital = capital
        self.mode = mode
        self.broker = broker  # None = paper fills at the live price
        self.default_strategy = strategy
        self.default_params = params or {}
        self.run_at = run_at
        self.history = history or self._yahoo_history
        self.costs = costs or daily.DeliveryCosts()
        self.now = now_fn
        self.sleep = sleep_fn
        self.feed_status = feed_status
        self.poll = poll_seconds
        self.liquid_symbol = liquid_symbol
        self.cutoff = cutoff
        self.reviewer = reviewer
        self.notify = notify
        self.scheduler = scheduler  # "worker" (always on) or "serverless" (woken every tick_minutes)
        self.tick_minutes = tick_minutes
        self._last_px: dict[str, float] = {}
        self._fresh = False  # prices were fetched during this pass
        self._filter: dict[str, Any] | None = None

    # State

    def state(self) -> dict[str, Any]:
        st = self.store.get_control().get(STATE_KEY)
        if not st:
            st = {"cash": self.capital, "capital": self.capital, "lots": {}, "last_run": None, "realized": 0.0}
        return st

    def save(self, st: dict[str, Any]) -> None:
        self.store.set_control(STATE_KEY, st)

    def strategy(self, control: dict) -> Any:
        cfg = control.get(SETTINGS_KEY) or {}
        try:
            return daily.build_daily(cfg.get("strategy") or self.default_strategy, cfg.get("params") or self.default_params,
                                     cash_asset=self.liquid_symbol)
        except ValueError:
            return daily.build_daily(self.default_strategy, self.default_params, cash_asset=self.liquid_symbol)

    @staticmethod
    def _yahoo_history(symbols: list[str], start: date, end: date) -> daily.Prices:
        return daily.load_prices(symbols, start, end)

    # Loop

    def run_forever(self) -> None:
        self.store.event("engine_start", f"daily investing started in {self.mode} mode")
        while True:
            try:
                self.tick()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                log.exception("invest tick failed")
                self.store.event("error", f"invest tick failed: {e}")
            self.sleep(self.poll)

    def tick(self) -> dict[str, Any]:
        """One pass. Returns a short summary of what it did (for logs and the serverless response)."""
        now = to_ist(self.now())
        control = self.store.get_control()
        st = self.state()
        strat = self.strategy(control)
        kill = bool(control.get("kill_switch"))
        stopped = kill or not control.get("trading_enabled")
        today = now.date()
        did = "idle"
        try:
            self._last_px = {**(st.get("marks") or {}).get("px", {}), **self._last_px}
            if not self.clock.is_trading_day(today):
                did = "market closed today"
            elif stopped:
                if st["lots"] and self._can_trade(now):
                    self._refresh_prices(list(st["lots"]))
                    self._rebalance(st, {}, now, "stopped" if not kill else "kill_switch")
                    self.store.event("trading_stopped", "stopped: sold all holdings")
                    self.save(st)
                    did = "sold everything (stopped)"
                else:
                    did = "stopped"
            elif control.get("paused"):
                did = "paused"
            elif now.time() >= self.run_at and st.get("last_run") != today.isoformat():
                did = self._guarded_run(st, strat, now)
            self._update_marks(st, now)
        finally:
            self._heartbeat(st, strat, now, control)
        return {"at": now.isoformat(), "did": did, "mode": self.mode, "strategy": strat.name}

    def _update_marks(self, st: dict[str, Any], now: datetime) -> None:
        """Keep a recent price for each holding in the saved state, so a worker that was just woken can
        still show today's value. Refreshed every 15 minutes while the market is open and once after
        each close; a failed refresh keeps the old marks."""
        if not st["lots"]:
            return
        marks = st.get("marks") or {}
        at = to_ist(datetime.fromisoformat(marks["at"])) if marks.get("at") else None
        day = now.date() if self.clock.is_trading_day(now.date()) and now.time() >= MARKET_CLOSE else None
        if day is None:
            day = now.date() - timedelta(days=1)
            while not self.clock.is_trading_day(day):
                day -= timedelta(days=1)
        last_close = datetime.combine(day, MARKET_CLOSE, tzinfo=now.tzinfo)
        stale = at is None or (now - at).total_seconds() > 900
        if self._fresh or (stale and (self.clock.is_market_open(now) or at is None or at < last_close)):
            if not self._fresh:
                try:
                    self._refresh_prices(list(st["lots"]))
                except Exception as e:
                    log.warning("could not refresh holding prices: %s", e)
                    return
            px = {s: self._last_px[s] for s in st["lots"] if s in self._last_px}
            if px:
                st["marks"] = {"at": now.isoformat(), "px": px}
                self.save(st)
            self._fresh = False

    def _can_trade(self, now: datetime) -> bool:
        """Paper fills need only a price; real orders need an open market and time to fill."""
        if self.broker is None:
            return now.time() >= MARKET_OPEN
        return self.clock.is_market_open(now) and now.time() <= self.cutoff

    def _guarded_run(self, st: dict[str, Any], strat: Any, now: datetime) -> str:
        """Run today's decision once, even if two schedulers call at the same moment."""
        today = now.date().isoformat()
        if self.broker is not None and not self._can_trade(now):
            if st.get("missed") != today:
                st["missed"], st["pending"] = today, True
                self.save(st)
                self._alert("invest_missed", f"{today}: the daily run started after {self.cutoff:%H:%M} IST, too late to trade. "
                                             "It will decide again on the next trading day.")
            return "missed (too late to trade)"
        claim = getattr(self.store, "claim", None)
        claim_id = claim("invest", today) if claim else None
        if claim and claim_id is None:
            return "another run holds today's lock"
        try:
            did = self._daily_run(st, strat, now)
        except Exception:
            if claim_id:
                self.store.release(claim_id)
            raise
        if claim_id:
            self.store.finish(claim_id, "done", {"did": did})
        return did

    def _refresh_prices(self, symbols: list[str]) -> dict[str, float]:
        px = self.quotes.ltp(symbols) if symbols else {}
        self._last_px.update(px)
        self._fresh = self._fresh or bool(px)
        return px

    def _daily_run(self, st: dict[str, Any], strat: Any, now: datetime) -> str:
        today = now.date()
        plan_name = daily.PLAN_NAMES.get(strat.name, strat.name)
        late = now.time() >= MARKET_CLOSE
        nxt = next_trading_day(self.clock, today)
        due = daily.REBALANCE[strat.rebalance](today, nxt) or not st.get("decided") or bool(st.get("pending"))
        symbols = list(dict.fromkeys([*strat.universe(), daily.BENCHMARK, *st["lots"]]))
        live = self._refresh_prices(symbols)
        traded_at = getattr(self.quotes, "as_of", {}).get(daily.BENCHMARK)
        if traded_at is not None and to_ist(traded_at).date() < today:
            # The calendar says it is a trading day but nothing has traded: an unlisted holiday.
            st["last_run"] = today.isoformat()
            self.save(st)
            self.store.event("invest_skip", f"the market looks closed today (last trade {to_ist(traded_at):%d %b %H:%M}); "
                                            "add the date to the holiday list")
            return "skipped: market looks closed"
        prices = self.history(symbols, today - timedelta(days=460), today - timedelta(days=1))
        hist: dict[str, list[float]] = {}
        last_close: dict[str, tuple[date, float]] = {}
        for s, series in prices.items():
            days = [d for d in sorted(series) if d < today]
            closes = [series[d] for d in days]
            if days:
                last_close[s] = (days[-1], closes[-1])
            if s in live:
                closes.append(live[s])
            hist[s] = closes
        idx = hist.get(daily.INDEX, [])
        avg = daily.sma(idx, getattr(strat, "sma_days", getattr(strat, "trend_sma_days", 200)))
        self._filter = {"index": idx[-1] if idx else None, "sma": avg, "above": bool(avg and idx and idx[-1] > avg)}
        # Where each ETF stands against its own 200-day average: shown on the dashboard as the reason for the holdings.
        watched = getattr(strat, "assets", None) or list(getattr(strat, "weights", {})) or [getattr(strat, "asset", daily.BENCHMARK)]
        st["signals"] = {s: {"price": round(hist[s][-1], 2), "avg": round(daily.sma(hist[s], 200), 2),
                             "above": hist[s][-1] > daily.sma(hist[s], 200)}
                         for s in watched if len(hist.get(s, [])) >= 200}
        st["last_run"] = today.isoformat()
        if not due:
            self.save(st)
            self._equity(st, now)
            return "checked: not a rebalance day"
        value = self._value(st)
        current = {s: lot["qty"] * self._last_px.get(s, 0) / value for s, lot in st["lots"].items()} if value else {}
        target = strat.target(today, hist, current)
        if target is None:
            st["pending"] = True
            self.save(st)
            self.store.event("invest_skip", "not enough price history to decide today; will try again next session")
            return "skipped: not enough history"
        st["decided"] = True
        if target == daily.KEEP:
            st["pending"] = False
            self.save(st)
            self._equity(st, now)
            self.store.event("rebalance", f"{plan_name}: holdings are on target, nothing to trade")
            return "checked: holdings on target"
        traded = sorted(set(target) | set(st["lots"]))
        problems = self._price_problems(traded, live, last_close, today)
        if problems:
            st["pending"] = True
            self.save(st)
            self._alert("invest_blocked", "rebalance postponed, prices look wrong: " + "; ".join(problems))
            return "postponed: bad prices"
        plan = self._plan(st, target)
        verdict = self._review(st, strat, target, plan, hist, now)
        if verdict is not None and not verdict.approve and st.get("review_delays", 0) < MAX_REVIEW_DELAYS:
            st["review_delays"] = st.get("review_delays", 0) + 1
            st["pending"] = True
            self.save(st)
            self._alert("invest_review", f"reviewer postponed the rebalance ({st['review_delays']}/{MAX_REVIEW_DELAYS}): {verdict.rationale}")
            return "postponed by the reviewer"
        st["review_delays"] = 0
        plan = self._rebalance(st, target, now, "rebalance")
        st["pending"] = False
        st["last_rebalance"] = today.isoformat()
        st["last_plan"] = {"at": now.isoformat(), "late": late, "target": {s: round(w, 4) for s, w in target.items()},
                           "orders": plan, "strategy": strat.name}
        names = ", ".join(f"{s} {w * 100:.0f}%" for s, w in sorted(target.items(), key=lambda kv: -kv[1])) or "cash"
        self.store.event("rebalance", f"{plan_name}: now holding {names}" + (" (late run on closing prices)" if late else ""),
                         target=target, orders=plan)
        self.save(st)
        self._equity(st, now)
        if self.notify and plan:
            lines = [f"{o['side']} {o['qty']} {o['symbol']} near {o['price']}" for o in plan]
            self._notify(f"Thunderbot ({self.mode}) rebalanced to {names}.\n" + "\n".join(lines))
        return f"rebalanced: {names}"

    # Checks

    def _price_problems(self, symbols: list[str], live: dict[str, float], last_close: dict[str, tuple[date, float]],
                        today: date) -> list[str]:
        """Reasons not to trade on these prices. Rules, not judgement: they run before any reviewer."""
        problems = []
        for s in symbols:
            if s not in live:
                problems.append(f"{s} has no live price")
                continue
            if s not in last_close:
                problems.append(f"{s} has no price history")
                continue
            day, close = last_close[s]
            if (today - day).days > MAX_HISTORY_AGE_DAYS:
                problems.append(f"{s} history ends {day}")
            elif abs(live[s] / close - 1) > MAX_PRICE_JUMP:
                problems.append(f"{s} is {live[s]:.2f} against a last close of {close:.2f} (possible split or bad tick)")
        return problems

    def _review(self, st: dict[str, Any], strat: Any, target: dict[str, float], plan: list[dict[str, Any]],
                hist: dict[str, list[float]], now: datetime) -> Any:
        if self.reviewer is None or not plan:
            return None
        from .llm.rebalance import RebalanceContext

        facts = {}
        for s in sorted(set(target) | set(st["lots"])):
            px = hist.get(s, [])
            if len(px) > 1:
                facts[s] = {"price": round(px[-1], 2), "change_1d_pct": round((px[-1] / px[-2] - 1) * 100, 2),
                            "change_1m_pct": round((px[-1] / px[-22] - 1) * 100, 2) if len(px) > 22 else None,
                            "change_12m_pct": round((px[-1] / px[-253] - 1) * 100, 2) if len(px) > 253 else None,
                            "vs_200d_avg_pct": round((px[-1] / daily.sma(px, 200) - 1) * 100, 2) if len(px) >= 200 else None}
        ctx = RebalanceContext(strategy=strat.name, mode=self.mode, as_of=now.isoformat(), target=target, orders=plan,
                               facts=facts, portfolio_value=round(self._value(st), 2),
                               delays_used=st.get("review_delays", 0), max_delays=MAX_REVIEW_DELAYS)
        try:
            verdict = self.reviewer.review(ctx)
        except Exception as e:  # a broken reviewer must never block the rule
            self.store.event("review_error", f"rebalance reviewer failed, continuing without it: {e}")
            return None
        self.store.insert("llm_decisions", {
            "symbol": "PORTFOLIO", "approve": verdict.approve, "size_multiplier": 1.0 if verdict.approve else 0.0,
            "confidence": verdict.confidence, "rationale": verdict.rationale, "risk_flags": verdict.risk_flags,
            "model": verdict.model, "latency_ms": verdict.latency_ms, "input_tokens": verdict.input_tokens,
            "output_tokens": verdict.output_tokens, "error": verdict.error, "prompt": verdict.prompt,
        })
        return verdict

    def _alert(self, kind: str, message: str) -> None:
        self.store.event(kind, message)
        self._notify(f"Thunderbot: {message}")

    def _notify(self, text: str) -> None:
        if self.notify:
            try:
                self.notify(text)
            except Exception as e:
                log.warning("notification failed: %s", e)

    # Execution

    def _value(self, st: dict[str, Any]) -> float:
        return st["cash"] + sum(lot["qty"] * self._last_px.get(s, lot["cost"] / max(lot["qty"], 1))
                                for s, lot in st["lots"].items())

    def _plan(self, st: dict[str, Any], target: dict[str, float]) -> list[dict[str, Any]]:
        """The whole-share orders a rebalance to ``target`` needs, sells first. Nothing is traded here."""
        value = self._value(st)
        want = {s: w * value for s, w in target.items() if self._last_px.get(s)}
        orders, cash = [], st["cash"]
        for s, lot in st["lots"].items():
            px = self._last_px.get(s)
            if not px:
                continue
            keep_qty = math.floor(want.get(s, 0.0) / px)
            sell_qty = lot["qty"] - keep_qty
            if sell_qty <= 0 or (keep_qty and sell_qty * px < 1_000):
                continue
            orders.append({"symbol": s, "side": "SELL", "qty": int(sell_qty), "price": round(px, 2), "value": round(sell_qty * px, 2)})
            cash += sell_qty * px * (1 - self._slip(s)) - self.costs.order(sell_qty * px, buy=False, symbol=s)
        for s, val in want.items():
            px = self._last_px[s]
            have = st["lots"].get(s, {}).get("qty", 0) - next((o["qty"] for o in orders if o["symbol"] == s), 0)
            qty = math.floor(min(val - have * px, cash / 1.004) / px)
            if qty <= 0 or qty * px < 1_000:
                continue
            orders.append({"symbol": s, "side": "BUY", "qty": int(qty), "price": round(px, 2), "value": round(qty * px, 2)})
            cash -= qty * px * (1 + self._slip(s)) + self.costs.order(qty * px, buy=True, symbol=s)
        return orders

    def _rebalance(self, st: dict[str, Any], target: dict[str, float], now: datetime, reason: str) -> list[dict[str, Any]]:
        """Place the planned orders, sells first. Returns the orders that filled, at their fill prices."""
        filled = []
        for o in self._plan(st, target):
            s, qty, px = o["symbol"], o["qty"], self._last_px[o["symbol"]]
            if o["side"] == "SELL":
                lot = st["lots"][s]
                fill = self._fill(s, "SELL", qty, px, now, reason)
                if fill is None:
                    continue
                gross = qty * fill
                c = self.costs.order(gross, buy=False, symbol=s)
                basis = lot["cost"] * qty / lot["qty"]
                net = gross - c - basis
                st["cash"] += gross - c
                st["realized"] = round(st.get("realized", 0.0) + net, 2)
                self.store.insert("trades", {
                    "symbol": s, "side": "BUY", "product": "CNC", "qty": qty,
                    "entry_price": round(basis / qty, 2), "exit_price": round(fill, 2), "opened_at": lot["since"],
                    "closed_at": now.isoformat(), "exit_reason": reason, "gross_pnl": round(gross - basis, 2),
                    "costs": round(c, 2), "net_pnl": round(net, 2), "strategy": "invest", "mode": self.mode,
                })
                lot["qty"] -= qty
                lot["cost"] -= basis
                if lot["qty"] <= 0:
                    del st["lots"][s]
            else:
                qty = min(qty, math.floor(st["cash"] / 1.004 / px))  # an earlier sell may not have filled
                if qty <= 0:
                    continue
                fill = self._fill(s, "BUY", qty, px, now, reason)
                if fill is None:
                    continue
                c = self.costs.order(qty * fill, buy=True, symbol=s)
                st["cash"] -= qty * fill + c
                lot = st["lots"].setdefault(s, {"qty": 0, "cost": 0.0, "since": now.isoformat()})
                lot["qty"] += qty
                lot["cost"] += qty * fill + c
            filled.append({"symbol": s, "side": o["side"], "qty": int(qty), "price": round(fill, 2), "value": round(qty * fill, 2)})
        st["cash"] = round(st["cash"], 2)
        return filled

    def _slip(self, symbol: str) -> float:
        return self.costs.liquid_slippage_pct if daily.asset_class(symbol) == "debt_etf" else self.costs.slippage_pct

    def _fill(self, symbol: str, side: str, qty: int, px: float, now: datetime, reason: str) -> float | None:
        if self.broker is None:
            slip = self._slip(symbol)
            fill = px * (1 + slip) if side == "BUY" else px * (1 - slip)
            self.store.insert("orders", {
                "order_id": f"PAPER-{symbol}-{now:%Y%m%d%H%M%S}-{side}", "purpose": f"invest:{reason}", "symbol": symbol,
                "side": side, "product": "CNC", "order_type": "LIMIT", "qty": qty, "price": round(px, 2),
                "status": "FILLED", "filled_qty": qty, "avg_price": round(fill, 2), "broker": "paper", "mode": self.mode,
            })
            return fill
        return self._live_fill(symbol, side, qty, px, now, reason)

    def _live_fill(self, symbol: str, side: str, qty: int, px: float, now: datetime, reason: str) -> float | None:
        from .broker.base import BrokerError
        from .engine import round_tick
        from .models import OrderRequest, OrderStatus, OrderType, Product, Side

        buy = side == "BUY"
        # Always a limit order: exchanges do not accept market orders from API (algo) clients.
        limit = round_tick(px * (1.005 if buy else 0.995), up=buy)
        req = OrderRequest(symbol, Side.BUY if buy else Side.SELL, qty, Product.CNC, OrderType.LIMIT, price=limit,
                           reference_id=f"TBI{now:%m%d%H%M%S}{symbol[:6]}")
        try:
            order = self.broker.place_order(req)
            for _ in range(30):
                if order.status.is_terminal:
                    break
                self.sleep(1.0)
                order = self.broker.order_status(order.order_id)
        except BrokerError as e:
            self.store.event("order_error", f"invest {side} {qty} {symbol}: {e}")
            return None
        self.store.insert("orders", {
            "order_id": order.order_id, "purpose": f"invest:{reason}", "symbol": symbol, "side": side, "product": "CNC",
            "order_type": "LIMIT", "qty": qty, "price": limit, "status": order.status, "filled_qty": order.filled_qty,
            "avg_price": order.avg_price, "broker": self.broker.name, "mode": self.mode,
        })
        if order.status is not OrderStatus.FILLED:
            if not order.status.is_terminal:
                try:
                    self.broker.cancel_order(order.order_id)
                except BrokerError:
                    pass
            self.store.event("order_rejected", f"invest {side} {qty} {symbol} not filled ({order.status.value})")
            return None
        return order.avg_price or limit

    # Reporting

    def _equity(self, st: dict[str, Any], now: datetime) -> None:
        value = self._value(st)
        self.store.insert("equity", {"at": now.isoformat(), "mode": self.mode,
                                     "realized_pnl": round(value - st["capital"], 2), "unrealized_pnl": 0.0,
                                     "open_positions": len(st["lots"])})

    def _next_tick_by(self, now: datetime) -> datetime:
        """When the dashboard should next expect a heartbeat; later than that, the scheduler is not calling."""
        if self.scheduler != "serverless":
            return now + timedelta(seconds=max(self.poll * 3, 45))
        step = timedelta(minutes=max(self.tick_minutes, 1) * 2 + 2)
        if self.clock.is_market_open(now) and (now + step).time() < MARKET_CLOSE:
            return now + step
        d = now.date() if now.time() < MARKET_OPEN and self.clock.is_trading_day(now.date()) else next_trading_day(self.clock, now.date())
        return datetime.combine(d, MARKET_OPEN, tzinfo=now.tzinfo) + step

    def _heartbeat(self, st: dict[str, Any], strat: Any, now: datetime, control: dict) -> None:
        value = self._value(st)
        holdings = []
        for s, lot in sorted(st["lots"].items()):
            px = self._last_px.get(s, lot["cost"] / max(lot["qty"], 1))
            holdings.append({"symbol": s, "qty": lot["qty"], "avg_price": round(lot["cost"] / lot["qty"], 2),
                             "ltp": round(px, 2), "value": round(lot["qty"] * px, 2),
                             "weight": round(lot["qty"] * px / value * 100, 1) if value else 0,
                             "pnl": round(lot["qty"] * px - lot["cost"], 2), "since": lot["since"]})
        today = now.date()
        nxt = today if self.clock.is_trading_day(today) and now.time() < self.run_at else next_trading_day(self.clock, today)
        if not st.get("pending"):
            while not daily.REBALANCE[strat.rebalance](nxt, next_trading_day(self.clock, nxt)):
                nxt = next_trading_day(self.clock, nxt)
        running = not control.get("kill_switch") and bool(control.get("trading_enabled"))
        self.store.set_control("heartbeat", {
            "at": now.isoformat(), "wall_at": now_ist().isoformat(), "mode": self.mode, "style": "invest",
            "strategy": strat.name, "open_positions": len(holdings), "positions": [],
            "realized_pnl": round(value - st["capital"], 2), "unrealized_pnl": 0.0, "trades_today": 0,
            "halted": False, "market_open": self.clock.is_market_open(now), "capital": st["capital"],
            "trading": "running" if running else "stopped", "feed": self.feed_status() if self.feed_status else None,
            "scheduler": self.scheduler, "next_tick_by": self._next_tick_by(now).isoformat(),
            "portfolio": {"value": round(value, 2), "cash": round(st["cash"], 2), "capital": st["capital"],
                          "invested_pct": round((value - st["cash"]) / value * 100, 1) if value else 0,
                          "holdings": holdings, "next_rebalance": nxt.isoformat(), "last_run": st.get("last_run"),
                          "run_at": self.run_at.strftime("%H:%M"), "rebalance": strat.rebalance, "filter": self._filter,
                          "realized": st.get("realized", 0.0), "pending": bool(st.get("pending")),
                          "missed": st.get("missed"), "last_plan": st.get("last_plan"),
                          "liquid_symbol": self.liquid_symbol, "signals": st.get("signals"),
                          "target": getattr(strat, "weights", None) or (st.get("last_plan") or {}).get("target")},
        })
