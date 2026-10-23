"""Daily delivery (CNC) investing: run a daily strategy from thunderbot.daily on a real or paper account.

Once per trading day, shortly before the close (TB_INVEST_AT, default 15:10 IST), the runner:
1. loads daily history (Yahoo Finance) and appends today's live price as today's bar,
2. asks the strategy for target weights if today is a rebalance day (or the portfolio is empty),
3. sells what is over target, then buys what is under, in whole shares,
4. journals orders, closed trades, an equity point and a heartbeat for the dashboard.

Controls (the same as the intraday engine): it trades only after "Start"; "Hold to stop" sells
everything; "Pause" keeps the holdings and makes no trades. The paper portfolio is kept in the
control table, so it survives restarts.
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
from .clock import MarketClock, now_ist, to_ist
from .store import CompositeStore

log = logging.getLogger(__name__)

STATE_KEY = "invest_portfolio"
SETTINGS_KEY = "invest_settings"


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
        strategy: str = "index_trend",
        params: dict | None = None,
        run_at: dtime = dtime(15, 10),
        history: Callable[[list[str], date, date], daily.Prices] | None = None,
        costs: daily.DeliveryCosts | None = None,
        now_fn: Callable[[], datetime] = now_ist,
        sleep_fn: Callable[[float], None] = time.sleep,
        feed_status: Callable[[], dict] | None = None,
        poll_seconds: float = 30.0,
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
        self._last_px: dict[str, float] = {}
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
            return daily.build_daily(cfg.get("strategy") or self.default_strategy, cfg.get("params") or self.default_params)
        except ValueError:
            return daily.build_daily(self.default_strategy, self.default_params)

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

    def tick(self) -> None:
        now = to_ist(self.now())
        control = self.store.get_control()
        st = self.state()
        strat = self.strategy(control)
        kill = bool(control.get("kill_switch"))
        stopped = kill or not control.get("trading_enabled")
        today = now.date()
        try:
            if self.clock.is_trading_day(today) and self.clock.is_market_open(now):
                if stopped and st["lots"]:
                    self._refresh_prices(list(st["lots"]))
                    self._rebalance(st, {}, now, "stopped" if not kill else "kill_switch")
                    self.store.event("trading_stopped", "stopped: sold all holdings")
                    self.save(st)
                elif not stopped and not control.get("paused") and now.time() >= self.run_at \
                        and st.get("last_run") != today.isoformat():
                    self._daily_run(st, strat, now)
        finally:
            self._heartbeat(st, strat, now, control)

    def _refresh_prices(self, symbols: list[str]) -> dict[str, float]:
        px = self.quotes.ltp(symbols) if symbols else {}
        self._last_px.update(px)
        return px

    def _daily_run(self, st: dict[str, Any], strat: Any, now: datetime) -> None:
        today = now.date()
        nxt = next_trading_day(self.clock, today)
        due = daily.REBALANCE[strat.rebalance](today, nxt) or not st["lots"]
        symbols = list(dict.fromkeys([daily.INDEX, *getattr(strat, "symbols", []), getattr(strat, "asset", daily.BENCHMARK),
                                      *st["lots"]]))
        live = self._refresh_prices([s for s in symbols if not s.startswith("^")] + [daily.INDEX])
        prices = self.history(symbols, today - timedelta(days=420), today - timedelta(days=1))
        hist: dict[str, list[float]] = {}
        for s, series in prices.items():
            closes = [series[d] for d in sorted(series) if d < today]
            if s in live:
                closes.append(live[s])
            hist[s] = closes
        idx = hist.get(daily.INDEX, [])
        avg = daily.sma(idx, getattr(strat, "sma_days", getattr(strat, "trend_sma_days", 200)))
        self._filter = {"index": idx[-1] if idx else None, "sma": avg, "above": bool(avg and idx and idx[-1] > avg)}
        st["last_run"] = today.isoformat()
        if not due:
            self.save(st)
            self._equity(st, now)
            return
        value = self._value(st)
        current = {s: lot["qty"] * self._last_px.get(s, 0) / value for s, lot in st["lots"].items()} if value else {}
        target = strat.target(today, hist, current)
        if target is None:
            self.store.event("invest_skip", "not enough history to decide today")
        else:
            self._refresh_prices(list(target))
            self._rebalance(st, target, now, "rebalance")
            names = ", ".join(sorted(target)) or "cash"
            self.store.event("rebalance", f"{strat.name}: holding {names}", target=target)
        self.save(st)
        self._equity(st, now)

    # Execution

    def _value(self, st: dict[str, Any]) -> float:
        return st["cash"] + sum(lot["qty"] * self._last_px.get(s, lot["cost"] / max(lot["qty"], 1))
                                for s, lot in st["lots"].items())

    def _rebalance(self, st: dict[str, Any], target: dict[str, float], now: datetime, reason: str) -> None:
        value = self._value(st)
        want = {s: w * value for s, w in target.items() if self._last_px.get(s)}
        for s in list(st["lots"]):  # sells first
            lot, px = st["lots"][s], self._last_px.get(s)
            if not px:
                continue
            keep_qty = math.floor(want.get(s, 0.0) / px)
            sell_qty = lot["qty"] - keep_qty
            if sell_qty <= 0 or (keep_qty and sell_qty * px < 1_000):
                continue
            fill = self._fill(s, "SELL", sell_qty, px, now, reason)
            if fill is None:
                continue
            gross = sell_qty * fill
            c = self.costs.order(gross, buy=False, symbol=s)
            basis = lot["cost"] * sell_qty / lot["qty"]
            net = gross - c - basis
            st["cash"] += gross - c
            st["realized"] = round(st.get("realized", 0.0) + net, 2)
            self.store.insert("trades", {
                "symbol": s, "side": "BUY", "product": "CNC", "qty": sell_qty,
                "entry_price": round(basis / sell_qty, 2), "exit_price": round(fill, 2), "opened_at": lot["since"],
                "closed_at": now.isoformat(), "exit_reason": reason, "gross_pnl": round(gross - basis, 2),
                "costs": round(c, 2), "net_pnl": round(net, 2), "strategy": "invest", "mode": self.mode,
            })
            lot["qty"] -= sell_qty
            lot["cost"] -= basis
            if lot["qty"] <= 0:
                del st["lots"][s]
        for s, val in want.items():  # then buys
            px = self._last_px[s]
            have = st["lots"].get(s, {}).get("qty", 0)
            qty = math.floor(min(val - have * px, st["cash"] / 1.004) / px)
            if qty <= 0 or qty * px < 1_000:
                continue
            fill = self._fill(s, "BUY", qty, px, now, reason)
            if fill is None:
                continue
            c = self.costs.order(qty * fill, buy=True, symbol=s)
            st["cash"] -= qty * fill + c
            lot = st["lots"].setdefault(s, {"qty": 0, "cost": 0.0, "since": now.isoformat()})
            lot["qty"] += qty
            lot["cost"] += qty * fill + c
        st["cash"] = round(st["cash"], 2)

    def _fill(self, symbol: str, side: str, qty: int, px: float, now: datetime, reason: str) -> float | None:
        if self.broker is None:
            slip = self.costs.slippage_pct
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
        while not daily.REBALANCE[strat.rebalance](nxt, next_trading_day(self.clock, nxt)):
            nxt = next_trading_day(self.clock, nxt)
        running = not control.get("kill_switch") and bool(control.get("trading_enabled"))
        self.store.set_control("heartbeat", {
            "at": now.isoformat(), "wall_at": now_ist().isoformat(), "mode": self.mode, "style": "invest",
            "strategy": strat.name, "open_positions": len(holdings), "positions": [],
            "realized_pnl": round(value - st["capital"], 2), "unrealized_pnl": 0.0, "trades_today": 0,
            "halted": False, "market_open": self.clock.is_market_open(now), "capital": st["capital"],
            "trading": "running" if running else "stopped", "feed": self.feed_status() if self.feed_status else None,
            "portfolio": {"value": round(value, 2), "cash": round(st["cash"], 2), "capital": st["capital"],
                          "invested_pct": round((value - st["cash"]) / value * 100, 1) if value else 0,
                          "holdings": holdings, "next_rebalance": nxt.isoformat(), "last_run": st.get("last_run"),
                          "run_at": self.run_at.strftime("%H:%M"), "rebalance": strat.rebalance, "filter": self._filter,
                          "realized": st.get("realized", 0.0)},
        })
