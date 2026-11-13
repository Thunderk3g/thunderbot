"""Daily delivery (CNC) investing: run a daily strategy from thunderbot.daily on a paper or real account.

Once per trading day, shortly before the close (TB_INVEST_AT, default 15:10 IST), the runner:
1. loads daily history (Yahoo Finance) and appends today's live price as today's bar,
2. asks the strategy for target weights if today is a rebalance day (or nothing was ever decided),
3. checks the prices it is about to trade on (stale, missing or jumping prices stop the run),
4. optionally lets a reviewer veto the plan for a day (it can delay, never change, the trades),
5. sells what is over target, then buys what is under, in whole shares,
6. journals orders, closed trades, the plan, an equity point and a heartbeat for the dashboard.

On a day with no rebalance it still does one thing: money the owner has deposited is spent on whatever
is furthest below its target, in whole shares, selling nothing.

It can be driven two ways. ``run_forever`` is the long-running worker (a laptop or a server).
``tick`` alone is one pass, for schedulers that wake the code every few minutes and keep no process
alive (a serverless function called by a cron job). Either way all state lives in the control table.

Controls. It trades only after "Start". "Stop" and the kill switch mean no new trades: the holdings
stay. Selling everything is its own command (``sell_all``) and is never a side effect of stopping.
"Pause" also keeps the holdings and makes no trades.

How orders are carried out (control row ``invest_mode``):
- ``paper``: fills are simulated at the live price with charges taken off. The default.
- ``guided``: the first real-money tier. The orders are worked out and published as a basket for the
  owner to place by hand; nothing is sent to the broker. The portfolio is the one the owner really
  holds (read from Groww, or typed in), and later passes check the holdings against the basket.
- ``auto``: orders go to the broker. Honoured only on a worker that was started for live trading, which
  takes switches in its own environment; on any other worker it behaves as ``guided`` and says why.

Timing rules. A paper run that starts late (the scheduler was delayed, the laptop was asleep) still
runs the same evening on closing prices and says so. An automatic run never trades after ``cutoff``
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
from .broker.refs import delivery_ref
from .clock import MARKET_CLOSE, MARKET_OPEN, MarketClock, now_ist, to_ist
from .store import CompositeStore, new_id

log = logging.getLogger(__name__)

STATE_KEY = "invest_portfolio"
SETTINGS_KEY = "invest_settings"
MODE_KEY = "invest_mode"  # paper | guided | auto, written by the dashboard
COMMANDS_KEY = "invest_commands"  # {"items": [{"id": n, "cmd": ..., ...}]}, appended by the dashboard
EXEC_MODES = ("paper", "guided", "auto")
MAX_PRICE_JUMP = 0.15  # a live price this far from the last close is treated as a data error, not a signal
MAX_HISTORY_AGE_DAYS = 7
MAX_REVIEW_DELAYS = 2  # the reviewer may postpone a rebalance this many sessions, then the rule runs
SYNC_EVERY_S = 6 * 3600  # how often actual holdings are re-read when nothing is waiting on them
BASKET_EXPIRES_DAYS = 7
LIMIT_OFFSET = 0.005  # limit orders sit this far through the last price
MIN_ORDER = 1_000.0  # a rebalance does not bother with an order smaller than this
MIN_DEPOSIT_ORDER = 500.0
TAX_NOTE = ("A proposal, not advice. A same-day sale and repurchase of one ticker is netted as an intraday trade and "
            "books no gain, so the buy-back is a day later or into a twin fund. Confirm the tax treatment with a "
            "chartered accountant before acting: it has not been checked against primary sources.")


def queue_command(store: Any, cmd: str, **fields: Any) -> int:
    """Add a command for the investing worker's next pass (what the dashboard's control API does).
    Commands: deposit {amount}, sell_all, harvest {confirm: true}, import_holdings {rows}, clear_holdings,
    sync_holdings, basket_done {basket}. Returns the command's number."""
    items = [c for c in ((store.get_control().get(COMMANDS_KEY) or {}).get("items") or []) if isinstance(c, dict)]
    number = max([int(time.time() * 1000), *(int(c.get("id") or 0) + 1 for c in items)])
    store.set_control(COMMANDS_KEY, {"items": [*items, {"id": number, "at": now_ist().isoformat(), "cmd": cmd, **fields}][-20:]})
    return number


def next_trading_day(clock: MarketClock, d: date) -> date:
    n = d + timedelta(days=1)
    while not clock.is_trading_day(n):
        n += timedelta(days=1)
    return n


def _tranches(lot: dict[str, Any]) -> list[dict[str, Any]]:
    """A holding's purchases, oldest first. Older state has one figure per holding: that is one purchase."""
    if not lot.get("tranches"):
        lot["tranches"] = [{"qty": lot["qty"], "cost": lot["cost"], "since": lot.get("since")}]
    return lot["tranches"]


def _held_days(since: Any, today: date) -> int | None:
    """Days a purchase has been held, or None when its date is not known (holdings read from a broker)."""
    if not since:
        return None
    try:
        return (today - date.fromisoformat(str(since)[:10])).days
    except ValueError:
        return None


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
        holdings_source: Callable[[], list[dict[str, Any]]] | None = None,
        band_abs_pct: float = daily.BAND_ABS_PCT,
        band_rel_pct: float = daily.BAND_REL_PCT,
        harvest_via: str = "t_plus_1",
        tax: daily.CapitalGainsTax | None = None,
    ) -> None:
        self.store = store
        self.quotes = quotes
        self.clock = clock
        self.capital = capital
        self.mode = mode  # how the worker was started: "paper", or "live" (its environment allows real orders)
        self.broker = broker  # None = this worker cannot place an order
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
        self.holdings_source = holdings_source  # reads the real demat holdings; never trades
        self.band_abs_pct = band_abs_pct
        self.band_rel_pct = band_rel_pct
        self.harvest_via = harvest_via if harvest_via in ("t_plus_1", "twin") else "t_plus_1"
        self.tax = tax or daily.CapitalGainsTax()
        self._last_px: dict[str, float] = {}
        self._fresh = False  # prices were fetched during this pass
        self._filter: dict[str, Any] | None = None
        self._exec = "auto" if self.live_allowed else "paper"
        self._exec_note = ""
        self._aliases: dict[str, str] = {}
        self._decision = ""
        self._ref_n = 0

    @property
    def live_allowed(self) -> bool:
        """Real orders need a worker started for them (switches in its own environment) and a broker."""
        return self.mode == "live" and self.broker is not None

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

    def _exec_mode(self, control: dict) -> tuple[str, str]:
        """How orders are carried out this pass, and a sentence when that differs from what was asked."""
        want = control.get(MODE_KEY)
        if want not in EXEC_MODES:
            want = "auto" if self.live_allowed else "paper"
        if want == "auto" and not self.live_allowed:
            return "guided", ("Automatic orders are switched on only where the worker runs, on a machine whose static IP is "
                              "registered with the broker. This worker is not one, so the orders are listed for you to place by hand.")
        return want, ""

    def _row_mode(self) -> str:
        """What the journal calls this money: simulated, or real (whether placed by hand or by the broker API)."""
        return "paper" if self._exec == "paper" else "live"

    def _book(self, st: dict[str, Any], strat: Any) -> dict[str, Any]:
        """The cash and holdings this pass works on. Paper and automatic runs keep their own book in the
        state. A guided run works on what the owner really holds, rebuilt from the latest holdings."""
        if self._exec != "guided":
            return st
        g = st.setdefault("guided", {"cash": 0.0, "capital": None, "lots": {}, "realized": 0.0})
        actual = st.get("actual") or {}
        plan = self._plan_symbols(strat, st)
        lots: dict[str, Any] = {}
        for r in actual.get("rows") or []:
            if r["symbol"] not in plan or r["qty"] <= 0:
                continue
            cost = r["qty"] * r.get("avg_price", 0.0)
            lots[r["symbol"]] = {"qty": r["qty"], "cost": cost, "since": r.get("since") or actual.get("synced_at"),
                                 "tranches": r.get("tranches") or [{"qty": r["qty"], "cost": cost, "since": r.get("since")}]}
        g["lots"] = lots
        return g

    def _plan_symbols(self, strat: Any, st: dict[str, Any]) -> set[str]:
        """Everything the plan may hold: its own tickers, the liquid ETF, and twins held after a harvest."""
        own = {s for s in strat.universe() if s != daily.INDEX} | {self.liquid_symbol}
        return own | {t for t, k in (st.get("aliases") or {}).items() if k in own}

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
        self._exec, self._exec_note = self._exec_mode(control)
        self._aliases = dict(st.get("aliases") or {})
        kill = bool(control.get("kill_switch"))
        stopped = kill or not control.get("trading_enabled")
        today = now.date()
        did = "idle"
        book = st
        try:
            self._last_px = {**(st.get("marks") or {}).get("px", {}), **self._last_px}
            dirty = self._drain_commands(st, control, now)
            dirty = self._sync_actual(st, strat, now) or dirty
            book = self._book(st, strat)
            if dirty:
                self.save(st)
            if not self.clock.is_trading_day(today):
                did = "market closed today"
            else:
                if self._exec == "guided" and self._reconcile(st, book, strat, now):
                    book = self._book(st, strat)
                    self.save(st)
                if st.get("sell_all"):
                    did = self._sell_all(st, book, now)
                elif stopped:
                    did = "stopped (holdings kept)"
                    if not kill:
                        did = self._harvest_step(st, book, now, allow_new=False) or did
                elif control.get("paused"):
                    did = self._harvest_step(st, book, now, allow_new=False) or "paused"
                else:
                    step = self._harvest_step(st, book, now, allow_new=True)
                    if now.time() >= self.run_at and st.get("last_run") != today.isoformat():
                        did = self._guarded_run(st, strat, now)
                    elif step:
                        did = step
            self._update_marks(st, book, now)
        finally:
            self._heartbeat(st, book, strat, now, control)
        return {"at": now.isoformat(), "did": did, "mode": self._row_mode(), "exec": self._exec, "strategy": strat.name}

    def _update_marks(self, st: dict[str, Any], book: dict[str, Any], now: datetime) -> None:
        """Keep a recent price for each holding in the saved state, so a worker that was just woken can
        still show today's value. Refreshed every 15 minutes while the market is open and once after
        each close; a failed refresh keeps the old marks."""
        if not book["lots"]:
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
                    self._refresh_prices(list(book["lots"]))
                except Exception as e:
                    log.warning("could not refresh holding prices: %s", e)
                    return
            px = {s: self._last_px[s] for s in book["lots"] if s in self._last_px}
            if px:
                st["marks"] = {"at": now.isoformat(), "px": px}
                self.save(st)
            self._fresh = False

    def _can_trade(self, now: datetime) -> bool:
        """Paper fills and hand-placed baskets need only a price; broker orders need an open market and time to fill."""
        if self._exec != "auto":
            return now.time() >= MARKET_OPEN
        return self.clock.is_market_open(now) and now.time() <= self.cutoff

    def _guarded_run(self, st: dict[str, Any], strat: Any, now: datetime) -> str:
        """Run today's decision once, even if two schedulers call at the same moment."""
        today = now.date().isoformat()
        if st.get("harvest_day") == today:
            # A harvest traded today. Trading the same ticker the other way today would be netted as an
            # intraday trade and undo it, so today's decision moves to the next session.
            st["last_run"], st["pending"] = today, True
            self.save(st)
            self.store.event("invest_skip", "a harvest order was booked today, so today's check moves to the next session")
            return "postponed: a harvest order was booked today"
        if self._exec == "auto" and not self._can_trade(now):
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

    # Commands from the dashboard

    def _drain_commands(self, st: dict[str, Any], control: dict, now: datetime) -> bool:
        """Carry out what the owner asked for since the last pass. Commands are numbered; the state keeps
        the last number handled, so one is never run twice and the row never has to be cleared."""
        items = (control.get(COMMANDS_KEY) or {}).get("items") or []
        seen = int(st.get("cmd_seq") or 0)
        fresh = sorted((c for c in items if isinstance(c, dict) and int(c.get("id") or 0) > seen), key=lambda c: int(c["id"]))
        for c in fresh:
            try:
                self._command(st, c, now)
            except Exception as e:
                self.store.event("error", f"could not carry out '{c.get('cmd')}': {type(e).__name__}: {e}")
            st["cmd_seq"] = int(c["id"])
        return bool(fresh)

    def _command(self, st: dict[str, Any], c: dict[str, Any], now: datetime) -> None:
        cmd = c.get("cmd")
        if cmd == "deposit":
            amount = float(c.get("amount") or 0)
            if not 0 < amount <= 1e10:
                raise ValueError("a deposit must be a positive amount")
            book = st.setdefault("guided", {"cash": 0.0, "capital": None, "lots": {}, "realized": 0.0}) if self._exec == "guided" else st
            book["cash"] = round(book.get("cash", 0.0) + amount, 2)
            if book.get("capital") is not None:
                book["capital"] = round(book["capital"] + amount, 2)
            book["deposit_pending"] = round(book.get("deposit_pending", 0.0) + amount, 2)
            self.store.event("deposit", f"Rs {amount:,.0f} added. It is invested at the next daily check, in whatever is furthest "
                                        "below its share; nothing is sold.", amount=amount)
        elif cmd == "sell_all":
            st["sell_all"] = True
            self.store.event("sell_all", "you asked to sell every holding; it happens on the next pass in market hours")
        elif cmd == "harvest":
            if c.get("confirm") is not True:
                raise ValueError("a harvest needs confirm: true")
            st["harvest_request"] = True
        elif cmd == "import_holdings":
            rows = self._clean_rows(c.get("rows"))
            st["actual"] = {"source": "manual", "synced_at": now.isoformat(), "rows": rows}
            st["actual_pin"] = "manual"
            if st.get("guided"):
                st["guided"]["capital"] = None  # start the "since you started" figure from these holdings
            self.store.event("holdings", f"{len(rows)} holdings entered by hand")
        elif cmd == "clear_holdings":
            st.pop("actual", None)
            st.pop("actual_pin", None)
            self.store.event("holdings", "the list of holdings was cleared")
        elif cmd == "sync_holdings":
            st["sync_now"] = True
            st.pop("actual_pin", None)
        elif cmd == "basket_done":
            b = st.get("basket")
            if b and b.get("status") == "open" and b.get("id") == c.get("basket"):
                b["placed_at"] = now.isoformat()
                st["sync_now"] = True
                self.store.event("basket", "you marked the basket as placed; the holdings are checked against it next")
        else:
            raise ValueError(f"unknown command {cmd!r}")

    @staticmethod
    def _clean_rows(rows: Any) -> list[dict[str, Any]]:
        out: dict[str, dict[str, Any]] = {}
        for r in rows or []:
            if not isinstance(r, dict):
                continue
            symbol = str(r.get("symbol") or "").strip().upper()
            try:
                qty, avg = float(r.get("qty") or 0), float(r.get("avg_price") or 0)
            except (TypeError, ValueError):
                continue
            if not symbol or qty <= 0 or avg < 0 or len(symbol) > 24:
                continue
            row: dict[str, Any] = {"symbol": symbol, "qty": int(qty) if qty == int(qty) else qty, "avg_price": round(avg, 4)}
            if _held_days(r.get("since"), date.max) is not None:
                row["since"] = str(r["since"])[:10]
            out[symbol] = row
        return list(out.values())[:200]

    # What the owner really holds

    def _sync_actual(self, st: dict[str, Any], strat: Any, now: datetime) -> bool:
        """Read the demat holdings when a broker key is present. Read-only; a failure is journalled once a day."""
        want_now = bool(st.pop("sync_now", False))
        if self.holdings_source is None or ((st.get("actual_pin") == "manual" or st.get("sync_off")) and not want_now):
            return want_now
        actual = st.get("actual") or {}
        last = to_ist(datetime.fromisoformat(actual["synced_at"])) if actual.get("source") == "groww" and actual.get("synced_at") else None
        waiting = (st.get("basket") or {}).get("status") == "open" and (st.get("basket") or {}).get("placed_at")
        if not want_now and last is not None:
            # Already read once. Read again in market hours when it has gone stale, or sooner while a basket waits.
            age = (now - last).total_seconds()
            in_hours = self.clock.is_trading_day(now.date()) and now.time() >= MARKET_OPEN
            if not in_hours or (age <= SYNC_EVERY_S and not (waiting and age > 600)):
                return False
        try:
            rows = self._clean_rows(self.holdings_source())
        except Exception as e:
            if st.get("sync_error") == now.date().isoformat():
                return want_now
            st["sync_error"] = now.date().isoformat()
            if "not installed" in str(e):
                st["sync_off"] = True  # this worker cannot read holdings at all; try again only when asked
            self.store.event("holdings_sync_failed", f"could not read your holdings from Groww: {e}")
            return True
        px: dict[str, float] = {}
        outside = [r["symbol"] for r in rows if r["symbol"] not in self._plan_symbols(strat, st)]
        if outside:
            try:
                px = {s: round(v, 2) for s, v in self.quotes.ltp(outside).items()}
            except Exception as e:  # prices for what the plan does not hold are a nicety
                log.warning("no prices for holdings outside the plan: %s", e)
        st["actual"] = {"source": "groww", "synced_at": now.isoformat(), "rows": rows, "px": px}
        st.pop("sync_error", None)
        st.pop("sync_off", None)
        return True

    def _reconcile(self, st: dict[str, Any], book: dict[str, Any], strat: Any, now: datetime) -> bool:
        """Has the basket been placed? With holdings read from the broker, compare them with what the basket
        should have done. With holdings typed in, the owner's word is taken and the list is updated."""
        b = st.get("basket")
        if not b or b.get("status") != "open":
            return False
        actual = st.get("actual") or {}
        if actual.get("source") == "groww":
            if not actual.get("synced_at") or actual["synced_at"] <= b["at"]:
                return False
            have = {r["symbol"]: r["qty"] for r in actual.get("rows") or []}
            wrong = []
            for o in b["orders"]:
                got = have.get(o["symbol"], 0) - o.get("before", 0)
                if o["side"] == "BUY" and got < o["qty"]:
                    wrong.append(f"{o['symbol']}: {o['qty']} to buy, holdings show {max(got, 0):g} more")
                elif o["side"] == "SELL" and -got < o["qty"]:
                    wrong.append(f"{o['symbol']}: {o['qty']} to sell, holdings show {max(-got, 0):g} fewer")
            if not wrong:
                self._settle_basket(st, book, b, strat, now, update_rows=False)
                return True
            if b.get("placed_at") and b.get("mismatch") != wrong:
                b["mismatch"] = wrong
                return True
        elif b.get("placed_at"):
            self._settle_basket(st, book, b, strat, now, update_rows=True)
            return True
        if (now - to_ist(datetime.fromisoformat(b["at"]))).days >= BASKET_EXPIRES_DAYS:
            b["status"] = "expired"
            self.store.event("basket", "the basket was not placed within a week and has lapsed")
            return True
        return False

    def _settle_basket(self, st: dict[str, Any], book: dict[str, Any], b: dict[str, Any], strat: Any, now: datetime,
                       update_rows: bool) -> None:
        """Book a hand-placed basket: gains on what was sold, cash, the journal, and (for typed-in holdings) the list."""
        filled = []
        for o in b["orders"]:
            s, qty, px = o["symbol"], o["qty"], o["limit"]
            c = self.costs.order(qty * px, buy=o["side"] == "BUY", symbol=s)
            if o["side"] == "SELL":
                if update_rows:
                    if s not in book["lots"] or book["lots"][s]["qty"] < qty:
                        continue  # the list no longer has these shares; nothing to book
                    self._book_sell(book, s, qty, px, c, now, f"guided:{b['reason']}")
                else:
                    # Read from the broker: the shares have already left the holdings, and purchase dates are not
                    # known, so the gain is taken from the average cost and counted as short-term.
                    basis = qty * o.get("avg_price", px)
                    self._journal_sale(book, s, qty, px, c, basis, None, now, f"guided:{b['reason']}", None)
                book["cash"] = round(book.get("cash", 0.0) + qty * px - c, 2)
            else:
                short = qty * px + c - book.get("cash", 0.0)
                if short > 0 and book.get("capital") is not None:
                    book["capital"] = round(book["capital"] + short, 2)  # paid for with money the bot was not told about
                book["cash"] = round(max(book.get("cash", 0.0) - qty * px - c, 0.0), 2)
                if update_rows:
                    self._book_buy(book, s, qty, px, c, now)
            self.store.insert("orders", {
                "order_id": f"HAND-{b['id']}-{s}-{o['side']}", "purpose": f"invest:{b['reason']}", "symbol": s, "side": o["side"],
                "product": "CNC", "order_type": "LIMIT", "qty": qty, "price": px, "status": "FILLED", "filled_qty": qty,
                "avg_price": px, "broker": "manual", "mode": "live",
            })
            filled.append({"symbol": s, "side": o["side"], "qty": qty, "price": px, "value": round(qty * px, 2)})
        if update_rows:
            actual = st.setdefault("actual", {"source": "manual", "synced_at": now.isoformat(), "rows": []})
            keep = [r for r in actual.get("rows") or [] if r["symbol"] not in book["lots"] and r["symbol"] not in {o["symbol"] for o in b["orders"]}]
            for s, lot in book["lots"].items():
                keep.append({"symbol": s, "qty": lot["qty"], "avg_price": round(lot["cost"] / lot["qty"], 4) if lot["qty"] else 0.0,
                             "since": lot.get("since"), "tranches": lot.get("tranches")})
            actual.update(rows=keep, synced_at=now.isoformat(), source=actual.get("source") or "manual")
        b.update(status="reconciled", reconciled_at=now.isoformat())
        b.pop("mismatch", None)
        book["deposit_pending"] = 0.0
        st["pending"] = False
        if b["reason"] == "rebalance":
            st["last_rebalance"] = now.date().isoformat()
        st["last_plan"] = {"at": now.isoformat(), "late": False, "target": b.get("target") or st.get("target") or {},
                           "orders": filled, "strategy": strat.name}
        self.store.event("basket", f"basket reconciled: {len(filled)} orders booked", orders=filled)

    # The daily decision

    def _daily_run(self, st: dict[str, Any], strat: Any, now: datetime) -> str:
        today = now.date()
        book = self._book(st, strat)
        plan_name = daily.PLAN_NAMES.get(strat.name, strat.name)
        late = now.time() >= MARKET_CLOSE
        nxt = next_trading_day(self.clock, today)
        due = daily.REBALANCE[strat.rebalance](today, nxt) or not st.get("decided") or bool(st.get("pending"))
        symbols = list(dict.fromkeys([*strat.universe(), daily.BENCHMARK, *book["lots"]]))
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
        target: Any = daily.KEEP
        if due:
            first = not st.get("decided")
            target = strat.target(today, hist, self._weights(book))
            if target is None:
                st["pending"] = True
                self.save(st)
                self.store.event("invest_skip", "not enough price history to decide today; will try again next session")
                return "skipped: not enough history"
            st["decided"] = True
            if first and book["lots"] and target != daily.KEEP and not st.get("pending"):
                # The owner arrived with holdings of their own. Selling them on day one to hit the target would
                # book tax nobody asked for, so the first step only records the target and spends new money
                # on whatever is short. Sales wait for the plan's own schedule (or its drift band).
                st["target"] = {s: round(w, 4) for s, w in target.items()}
                self.store.event("rebalance", f"{plan_name}: starting from what you already hold. Nothing is sold now; "
                                              "new money goes to whatever is below its target, and the plan's own "
                                              "schedule decides the first sale")
                target = daily.KEEP
        if target == daily.KEEP:
            # No rebalance today. Still spend a deposit, and re-price a basket that is waiting to be placed.
            if due:
                st["pending"] = False
            did = self._cash_flow(st, book, strat, hist, live, last_close, now)
            self.save(st)
            self._equity(book, now)
            if did:
                return did
            if due:
                self.store.event("rebalance", f"{plan_name}: holdings are on target, nothing to trade")
                return "checked: holdings on target"
            return "checked: not a rebalance day"
        st["target"] = {s: round(w, 4) for s, w in target.items()}
        traded = sorted(set(target) | set(book["lots"]))
        problems = self._price_problems(traded, live, last_close, today)
        if problems:
            st["pending"] = True
            self.save(st)
            self._alert("invest_blocked", "rebalance postponed, prices look wrong: " + "; ".join(problems))
            return "postponed: bad prices"
        plan = self._plan(book, target, strat)
        verdict = self._review(st, book, strat, target, plan, hist, now)
        if verdict is not None and not verdict.approve and st.get("review_delays", 0) < MAX_REVIEW_DELAYS:
            st["review_delays"] = st.get("review_delays", 0) + 1
            st["pending"] = True
            self.save(st)
            self._alert("invest_review", f"reviewer postponed the rebalance ({st['review_delays']}/{MAX_REVIEW_DELAYS}): {verdict.rationale}")
            return "postponed by the reviewer"
        st["review_delays"] = 0
        names = ", ".join(f"{s} {w * 100:.0f}%" for s, w in sorted(target.items(), key=lambda kv: -kv[1])) or "cash"
        if self._exec == "guided":
            st["pending"] = False
            if not plan:
                self.save(st)
                self._equity(book, now)
                self.store.event("rebalance", f"{plan_name}: what you hold already matches {names}; nothing to place")
                return "checked: holdings on target"
            self._publish_basket(st, book, plan, "rebalance", now, target=st["target"])
            book["deposit_pending"] = 0.0  # the rebalance spends the cash too
            self.save(st)
            self._equity(book, now)
            return f"basket published: {len(plan)} orders to place by hand"
        self._decision = f"{today.isoformat()}:rebalance"
        plan = self._execute(st, book, plan, now, "rebalance")
        st["pending"] = False
        book["deposit_pending"] = 0.0
        st["last_rebalance"] = today.isoformat()
        st["last_plan"] = {"at": now.isoformat(), "late": late, "target": {s: round(w, 4) for s, w in target.items()},
                           "orders": plan, "strategy": strat.name}
        self.store.event("rebalance", f"{plan_name}: now holding {names}" + (" (late run on closing prices)" if late else ""),
                         target=target, orders=plan)
        self.save(st)
        self._equity(book, now)
        if self.notify and plan:
            lines = [f"{o['side']} {o['qty']} {o['symbol']} near {o['price']}" for o in plan]
            self._notify(f"Thunderbot ({self._row_mode()}) rebalanced to {names}.\n" + "\n".join(lines))
        return f"rebalanced: {names}"

    def _cash_flow(self, st: dict[str, Any], book: dict[str, Any], strat: Any, hist: dict[str, list[float]],
                   live: dict[str, float], last_close: dict[str, tuple[date, float]], now: datetime) -> str | None:
        """On a day with no rebalance: re-price a basket still waiting to be placed, or spend a deposit on
        whatever is furthest below its share. Buys only; nothing is ever sold here."""
        today = now.date()
        b = st.get("basket")
        if (self._exec == "guided" and b and b.get("status") == "open" and b.get("reason") == "rebalance"
                and not b.get("placed_at") and b["at"][:10] < today.isoformat()):
            # Yesterday's limits are stale. (A basket the owner says is placed is left alone until the holdings confirm it.)
            plan = self._plan(book, b.get("target") or {}, strat)
            if not plan:
                b.update(status="reconciled", reconciled_at=now.isoformat())
                self.store.event("basket", "what you hold now matches the plan; the basket is closed")
                return "basket closed: holdings match the plan"
            self._publish_basket(st, book, plan, "rebalance", now, target=b.get("target"))
            return "basket re-priced"
        if book.get("deposit_pending", 0.0) <= 0:
            return None
        if self._exec == "guided" and b and b.get("status") == "open":
            return None  # one basket at a time: the deposit waits until the open one is placed
        weights = self._target_weights(st, strat, hist)
        if not weights:
            return None
        problems = self._price_problems(sorted(weights), live, last_close, today)
        if problems:
            self._alert("invest_blocked", "the deposit waits, prices look wrong: " + "; ".join(problems))
            return "deposit waits: bad prices"
        buys = self._route(book, weights)
        if not buys:
            book["deposit_pending"] = 0.0
            self.store.event("deposit", "the deposit stays as cash for now: nothing is a whole share short of its target")
            return "deposit kept as cash"
        if self._exec == "guided":
            self._publish_basket(st, book, buys, "deposit", now, target=weights)
            book["deposit_pending"] = 0.0
            return f"basket published: {len(buys)} buys for your deposit"
        self._decision = f"{today.isoformat()}:deposit"
        filled = self._execute(st, book, buys, now, "deposit")
        book["deposit_pending"] = 0.0
        if filled:
            names = ", ".join(f"{o['qty']} {o['symbol']}" for o in filled)
            st["last_plan"] = {"at": now.isoformat(), "late": now.time() >= MARKET_CLOSE, "target": weights, "orders": filled,
                               "strategy": strat.name}
            self.store.event("deposit", f"deposit invested with no sales: bought {names}", orders=filled)
            return f"deposit invested: {names}"
        return "deposit not invested: no order filled"

    def _target_weights(self, st: dict[str, Any], strat: Any, hist: dict[str, list[float]] | None = None) -> dict[str, float]:
        """The shares the plan is aiming at right now, as fractions that sum to one (or less, when part waits in cash)."""
        fixed = getattr(strat, "weights", None)
        if fixed:
            total = sum(fixed.values()) or 1.0
            return {s: w / total for s, w in fixed.items()}
        wanted = getattr(strat, "wanted", None)
        if wanted is not None and hist is not None:
            got = wanted(hist)
            if got:
                return got
        return dict(st.get("target") or (st.get("last_plan") or {}).get("target") or {})

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

    def _review(self, st: dict[str, Any], book: dict[str, Any], strat: Any, target: dict[str, float], plan: list[dict[str, Any]],
                hist: dict[str, list[float]], now: datetime) -> Any:
        if self.reviewer is None or not plan:
            return None
        from .llm.rebalance import RebalanceContext

        facts = {}
        for s in sorted(set(target) | set(book["lots"])):
            px = hist.get(s, [])
            if len(px) > 1:
                facts[s] = {"price": round(px[-1], 2), "change_1d_pct": round((px[-1] / px[-2] - 1) * 100, 2),
                            "change_1m_pct": round((px[-1] / px[-22] - 1) * 100, 2) if len(px) > 22 else None,
                            "change_12m_pct": round((px[-1] / px[-253] - 1) * 100, 2) if len(px) > 253 else None,
                            "vs_200d_avg_pct": round((px[-1] / daily.sma(px, 200) - 1) * 100, 2) if len(px) >= 200 else None}
        ctx = RebalanceContext(strategy=strat.name, mode=self._row_mode(), as_of=now.isoformat(), target=target, orders=plan,
                               facts=facts, portfolio_value=round(self._value(book), 2),
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
            # Which harness and role answered, and what the call cost; a database without these columns drops them.
            "role": "rebalance_reviewer", "stage": "active", "harness_id": getattr(verdict, "harness_id", None),
            "cost_inr": getattr(verdict, "cost_inr", 0.0),
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

    # The book: value, weights, plans

    def _px(self, book: dict[str, Any], s: str) -> float:
        lot = book["lots"].get(s)
        return self._last_px.get(s) or (lot["cost"] / max(lot["qty"], 1) if lot else 0.0)

    def _value(self, book: dict[str, Any]) -> float:
        return book.get("cash", 0.0) + sum(lot["qty"] * self._px(book, s) for s, lot in book["lots"].items())

    def _sleeves(self, book: dict[str, Any]) -> dict[str, float]:
        """Rupees held per plan ticker. A twin bought in a harvest counts toward the ticker it stands in for."""
        out: dict[str, float] = {}
        for s, lot in book["lots"].items():
            k = self._aliases.get(s, s)
            out[k] = out.get(k, 0.0) + lot["qty"] * self._px(book, s)
        return out

    def _weights(self, book: dict[str, Any]) -> dict[str, float]:
        value = self._value(book)
        return {s: v / value for s, v in self._sleeves(book).items()} if value else {}

    def _plan(self, book: dict[str, Any], target: dict[str, float], strat: Any = None) -> list[dict[str, Any]]:
        """The whole-share orders a rebalance to ``target`` needs, sells first. Nothing is traded here."""
        value = self._value(book)
        lots = book["lots"]
        want: dict[str, float] = {}
        for k, w in target.items():
            if not self._last_px.get(k):
                continue
            share = w * value
            # A twin held after a harvest is part of this share. Keep the plan's own ticker; the twin is sold first.
            own = lots[k]["qty"] * self._last_px[k] if k in lots else 0.0
            room = max(share - own, 0.0)
            for t in [s for s in lots if self._aliases.get(s) == k and self._last_px.get(s)]:
                want[t] = min(lots[t]["qty"] * self._last_px[t], room)
                room -= want[t]
                share -= want[t]
            want[k] = share
        sells = not getattr(strat, "deposits_only", False)
        orders, cash = [], book.get("cash", 0.0)
        for s, lot in lots.items():
            px = self._last_px.get(s)
            if not px or not sells:
                continue
            keep_qty = math.floor(want.get(s, 0.0) / px)
            sell_qty = lot["qty"] - keep_qty
            if sell_qty <= 0 or (keep_qty and sell_qty * px < MIN_ORDER):
                continue
            orders.append({"symbol": s, "side": "SELL", "qty": int(sell_qty), "price": round(px, 2), "value": round(sell_qty * px, 2)})
            cash += sell_qty * px * (1 - self._slip(s)) - self.costs.order(sell_qty * px, buy=False, symbol=s)
        for s, val in want.items():
            if s not in target:
                continue  # twins are never bought by the plan
            px = self._last_px[s]
            have = lots.get(s, {}).get("qty", 0) - next((o["qty"] for o in orders if o["symbol"] == s), 0)
            qty = math.floor(min(val - have * px, cash / 1.004) / px)
            if qty <= 0 or qty * px < MIN_ORDER:
                continue
            orders.append({"symbol": s, "side": "BUY", "qty": int(qty), "price": round(px, 2), "value": round(qty * px, 2)})
            cash -= qty * px * (1 + self._slip(s)) + self.costs.order(qty * px, buy=True, symbol=s)
        return orders

    def _route(self, book: dict[str, Any], weights: dict[str, float]) -> list[dict[str, Any]]:
        """Whole-share buys for the cash on hand: furthest below target first. No sells."""
        prices = {s: self._last_px[s] for s in weights if self._last_px.get(s)}
        # Budget for the worst case: every order filling at its limit (0.5% through the price) plus charges,
        # so a basket never asks for more cash than is there.
        buys = daily.route_cash(book.get("cash", 0.0), self._sleeves(book), weights, prices, self._value(book),
                                min_order=MIN_DEPOSIT_ORDER, buffer=0.007)
        return [{"symbol": s, "side": "BUY", "qty": int(q), "price": round(prices[s], 2), "value": round(q * prices[s], 2)}
                for s, q in buys]

    def _drift(self, book: dict[str, Any], weights: dict[str, float]) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
        """Each target holding against its corridor, and where the next deposited rupee would go."""
        value = self._value(book)
        if not weights or value <= 0:
            return [], None
        sleeves = self._sleeves(book)
        rows, worst = [], None
        ordered = sorted(enumerate(weights.items()), key=lambda it: (-round(it[1][1], 6), it[0]))  # largest share first
        for _, (s, t) in ordered:
            lo, hi = daily.corridor(t, self.band_abs_pct, self.band_rel_pct)
            v = sleeves.get(s, 0.0)
            w = v / value
            rows.append({"symbol": s, "weight": round(w * 100, 2), "target": round(t * 100, 2), "lo": round(lo * 100, 2),
                         "hi": round(hi * 100, 2), "out": bool(w <= lo + 1e-9 or w >= hi - 1e-9), "value": round(v, 2)})
            if t - w > 1e-6 and (worst is None or t - w > worst[1]):
                worst = (s, t - w)
        nxt = None if worst is None else {"symbol": worst[0], "short_inr": round(worst[1] * value, 2), "short_pct": round(worst[1] * 100, 2)}
        return rows, nxt

    # Execution

    def _book_buy(self, book: dict[str, Any], s: str, qty: float, fill: float, charges: float, now: datetime) -> None:
        lot = book["lots"].get(s)
        if lot is None:
            lot = book["lots"][s] = {"qty": 0, "cost": 0.0, "since": now.isoformat(), "tranches": []}
        else:
            _tranches(lot)
        lot["qty"] += qty
        lot["cost"] += qty * fill + charges
        lot["tranches"].append({"qty": qty, "cost": qty * fill + charges, "since": now.isoformat()})

    def _book_sell(self, book: dict[str, Any], s: str, qty: float, fill: float, charges: float, now: datetime, reason: str) -> float:
        """Take ``qty`` out of a holding, oldest purchase first (as a demat account is taxed), record the gain by
        the kind of tax it attracts, and journal the closed trade. Returns the net result."""
        lot = book["lots"][s]
        left, basis, parts = qty, 0.0, []
        for tr in list(_tranches(lot)):
            take = min(tr["qty"], left)
            if take <= 0:
                break
            part = tr["cost"] * take / tr["qty"]
            parts.append((take, part, _held_days(tr.get("since"), now.date())))
            tr["qty"] -= take
            tr["cost"] -= part
            basis += part
            left -= take
            if tr["qty"] <= 0:
                lot["tranches"].remove(tr)
        net = 0.0
        for take, part, held in parts:
            net += self._journal_sale(book, s, take, fill, charges * take / qty, part, held, now, reason, lot.get("since"), trade=False)
        self.store.insert("trades", {
            "symbol": s, "side": "BUY", "product": "CNC", "qty": qty,
            "entry_price": round(basis / qty, 2), "exit_price": round(fill, 2), "opened_at": lot.get("since") or now.isoformat(),
            "closed_at": now.isoformat(), "exit_reason": reason, "gross_pnl": round(qty * fill - basis, 2),
            "costs": round(charges, 2), "net_pnl": round(net, 2), "strategy": "invest", "mode": self._row_mode(),
        })
        lot["qty"] -= qty
        lot["cost"] -= basis
        if lot["qty"] <= 0:
            del book["lots"][s]
        return net

    def _journal_sale(self, book: dict[str, Any], s: str, qty: float, fill: float, charges: float, basis: float,
                      held_days: int | None, now: datetime, reason: str, opened_at: Any, trade: bool = True) -> float:
        """Record one sale's gain under the kind of tax it attracts. A purchase whose date is not known is
        treated as short-term, the costlier assumption."""
        fy = str(daily.financial_year(now.date()))
        gains = book.setdefault("fy_gains", {}).setdefault(fy, dict.fromkeys(daily.TAX_BUCKETS, 0.0))
        net = qty * fill - charges - basis
        bucket = daily.tax_bucket(s, held_days if held_days is not None else 0)
        gains[bucket] = round(gains[bucket] + net, 2)
        book["realized"] = round(book.get("realized", 0.0) + net, 2)
        if trade:
            self.store.insert("trades", {
                "symbol": s, "side": "BUY", "product": "CNC", "qty": qty,
                "entry_price": round(basis / qty, 2), "exit_price": round(fill, 2), "opened_at": opened_at or now.isoformat(),
                "closed_at": now.isoformat(), "exit_reason": reason, "gross_pnl": round(qty * fill - basis, 2),
                "costs": round(charges, 2), "net_pnl": round(net, 2), "strategy": "invest", "mode": self._row_mode(),
            })
        return net

    def _execute(self, st: dict[str, Any], book: dict[str, Any], orders: list[dict[str, Any]], now: datetime, reason: str) -> list[dict[str, Any]]:
        """Place the orders in the order given (sells first). Returns what filled, at the fill prices.
        A part-filled order is booked for the part that filled."""
        filled = []
        for o in orders:
            s, qty = o["symbol"], o["qty"]
            px = self._last_px.get(s) or o["price"]
            if o["side"] == "SELL":
                if s not in book["lots"]:
                    continue
                qty = min(qty, book["lots"][s]["qty"])
                got = self._fill(s, "SELL", qty, px, now, reason)
                if got is None:
                    continue
                qty, fill = got
                c = self.costs.order(qty * fill, buy=False, symbol=s)
                self._book_sell(book, s, qty, fill, c, now, reason)
                book["cash"] += qty * fill - c
            else:
                qty = min(qty, math.floor(book["cash"] / 1.004 / px))  # an earlier sell may not have filled
                if qty <= 0:
                    continue
                got = self._fill(s, "BUY", qty, px, now, reason)
                if got is None:
                    continue
                qty, fill = got
                c = self.costs.order(qty * fill, buy=True, symbol=s)
                book["cash"] -= qty * fill + c
                self._book_buy(book, s, qty, fill, c, now)
            filled.append({"symbol": s, "side": o["side"], "qty": int(qty), "price": round(fill, 2), "value": round(qty * fill, 2)})
        book["cash"] = round(book["cash"], 2)
        return filled

    def _slip(self, symbol: str) -> float:
        return self.costs.liquid_slippage_pct if daily.asset_class(symbol) == "debt_etf" else self.costs.slippage_pct

    def _fill(self, symbol: str, side: str, qty: int, px: float, now: datetime, reason: str) -> tuple[int, float] | None:
        """(quantity filled, average price), or None when nothing filled."""
        if self._exec != "auto":
            slip = self._slip(symbol)
            fill = px * (1 + slip) if side == "BUY" else px * (1 - slip)
            self.store.insert("orders", {
                "order_id": f"PAPER-{symbol}-{now:%Y%m%d%H%M%S}-{side}", "purpose": f"invest:{reason}", "symbol": symbol,
                "side": side, "product": "CNC", "order_type": "LIMIT", "qty": qty, "price": round(px, 2),
                "status": "FILLED", "filled_qty": qty, "avg_price": round(fill, 2), "broker": "paper", "mode": "paper",
            })
            return qty, fill
        return self._live_fill(symbol, side, qty, px, now, reason)

    def _live_fill(self, symbol: str, side: str, qty: int, px: float, now: datetime, reason: str) -> tuple[int, float] | None:
        from .broker.base import BrokerError
        from .engine import round_tick
        from .models import OrderRequest, OrderStatus, OrderType, Product, Side

        buy = side == "BUY"
        # Always a limit order: exchanges do not accept market orders from API (algo) clients.
        limit = round_tick(px * (1 + LIMIT_OFFSET if buy else 1 - LIMIT_OFFSET), up=buy)
        self._ref_n += 1
        ref = delivery_ref(now.date(), self._decision or f"{now.date().isoformat()}:{reason}", symbol, side, self._ref_n)
        req = OrderRequest(symbol, Side.BUY if buy else Side.SELL, qty, Product.CNC, OrderType.LIMIT, price=limit, reference_id=ref)
        try:
            order = self.broker.place_order(req)
            for _ in range(30):
                if order.status.is_terminal:
                    break
                self.sleep(1.0)
                order = self.broker.order_status(order.order_id)
            if not order.status.is_terminal:
                # Out of time. Cancel what is left; whatever filled before the cancel still counts.
                try:
                    order = self.broker.cancel_order(order.order_id)
                except BrokerError as e:
                    self.store.event("order_error", f"invest {side} {symbol}: could not cancel the unfilled part: {e}")
                    order = self.broker.order_status(order.order_id)
        except BrokerError as e:
            self.store.event("order_error", f"invest {side} {qty} {symbol}: {e}")
            return None
        got = min(int(order.filled_qty or 0), qty)
        if order.status is OrderStatus.FILLED and got == 0:
            got = qty  # a filled order that did not report its quantity
        self.store.insert("orders", {
            "order_id": order.order_id, "reference_id": ref, "purpose": f"invest:{reason}", "symbol": symbol, "side": side,
            "product": "CNC", "order_type": "LIMIT", "qty": qty, "price": limit, "status": order.status, "filled_qty": got,
            "avg_price": order.avg_price, "broker": self.broker.name, "mode": "live",
        })
        if got <= 0:
            self.store.event("order_rejected", f"invest {side} {qty} {symbol} not filled ({order.status.value})")
            return None
        if got < qty:
            self.store.event("partial_fill", f"invest {side} {symbol}: {got} of {qty} filled; the rest was cancelled and "
                                             f"only the {got} are booked", symbol=symbol, filled=got, asked=qty)
        return got, float(order.avg_price or limit)

    # Baskets: orders for the owner to place by hand

    def _publish_basket(self, st: dict[str, Any], book: dict[str, Any], orders: list[dict[str, Any]], reason: str, now: datetime,
                        target: dict[str, float] | None = None) -> dict[str, Any]:
        from .engine import round_tick

        old = st.get("basket")
        if old and old.get("status") == "open":
            old["status"] = "expired"
        value = self._value(book)
        weights = self._weights(book)
        items = []
        for o in orders:
            s, buy = o["symbol"], o["side"] == "BUY"
            px = self._last_px.get(s) or o["price"]
            limit = round_tick(px * (1 + LIMIT_OFFSET if buy else 1 - LIMIT_OFFSET), up=buy)
            k = self._aliases.get(s, s)
            w, t = weights.get(k, 0.0) * 100, (target or {}).get(k)
            why = o.get("why") or (f"{w:.1f}% of the portfolio" + (f" against a target of {t * 100:.1f}%" if t is not None else ", not in the plan"))
            lot = book["lots"].get(s) or {}
            items.append({"symbol": s, "side": o["side"], "qty": int(o["qty"]), "limit": limit, "value": round(o["qty"] * limit, 2),
                          "why": why, "before": lot.get("qty", 0),
                          "avg_price": round(lot["cost"] / lot["qty"], 4) if lot.get("qty") else limit})
        basket = {"id": new_id()[:12], "at": now.isoformat(), "reason": reason, "orders": items, "status": "open",
                  "target": target, "value": round(value, 2)}
        st["basket"] = basket
        self.store.event("basket", f"{len(items)} orders for you to place by hand ({reason.replace('_', ' ')})", orders=[
            {k: o[k] for k in ("symbol", "side", "qty", "limit")} for o in items])
        if self.notify:
            lines = [f"{o['side']} {o['qty']} {o['symbol']} at a limit of {o['limit']}" for o in items]
            self._notify("Thunderbot has orders for you to place by hand, sells first:\n" + "\n".join(lines))
        return basket

    def _sell_all(self, st: dict[str, Any], book: dict[str, Any], now: datetime) -> str:
        """Sell every holding the plan manages, because the owner asked. Never a side effect of stopping."""
        if not book["lots"]:
            st.pop("sell_all", None)
            self.save(st)
            return "nothing to sell"
        if not self._can_trade(now):
            return "sell-all waits for the market"
        self._refresh_prices(list(book["lots"]))
        orders = [{"symbol": s, "side": "SELL", "qty": int(lot["qty"]), "price": round(self._px(book, s), 2),
                   "value": round(lot["qty"] * self._px(book, s), 2), "why": "you asked to sell everything"}
                  for s, lot in book["lots"].items()]
        if self._exec == "guided":
            self._publish_basket(st, book, orders, "sell_all", now, target={})
            st.pop("sell_all", None)
            self.save(st)
            return f"basket published: {len(orders)} sells to place by hand"
        self._decision = f"{now.date().isoformat()}:sell_all"
        filled = self._execute(st, book, orders, now, "sell_all")
        if not book["lots"]:
            st.pop("sell_all", None)
        self.store.event("sold_all", "sold every holding at your request", orders=filled)
        self.save(st)
        return "sold everything (at your request)"

    # The tax year

    def _tax_year(self, book: dict[str, Any], now: datetime) -> dict[str, Any]:
        """Where this financial year's tax-free long-term equity gain stands, and what could still be booked."""
        today = now.date()
        fy = daily.financial_year(today)
        g = (book.get("fy_gains") or {}).get(str(fy), {})
        realized = float(g.get("ltcg", 0.0))
        other = sum(float(g.get(k, 0.0)) for k in daily.TAX_BUCKETS if k != "ltcg")
        exempt = self.tax.ltcg_exempt
        remaining = max(exempt - max(realized, 0.0), 0.0)
        harvestable, lots, room, charges = 0.0, [], remaining, 0.0
        candidates = []
        for s, lot in book["lots"].items():
            px = self._last_px.get(s)
            if not px or daily.asset_class(s) not in ("stock", "equity_etf"):
                continue
            aged = []  # the purchases held over a year, oldest first; a sale takes them in this order
            for tr in _tranches(lot):
                held = _held_days(tr.get("since"), today)
                if held is None or held <= 365 or tr["qty"] <= 0:
                    break
                aged.append((tr["qty"], px - tr["cost"] / tr["qty"], held))
            gain = sum(q * per for q, per, _ in aged)
            if gain > 0:
                harvestable += gain
                candidates.append((gain / sum(q for q, _, _ in aged) / px, s, px, aged))
        for _, s, px, aged in sorted(candidates, reverse=True):  # most gain per rupee sold first: least trading
            qty, gain, days = 0, 0.0, None
            for q, per, held in aged:
                take = q if per <= 0 or q * per <= room - gain else math.floor(max(room - gain, 0.0) / per)
                if take <= 0:
                    break
                qty += int(take)
                gain += take * per
                days = held if days is None else min(days, held)
                if take < q:
                    break
            if qty < 1 or gain <= 0:
                continue
            twin = daily.HARVEST_TWINS.get(s) if self.harvest_via == "twin" else None
            lots.append({"symbol": s, "qty": qty, "gain": round(gain, 2), "held_days": days,
                         "via": "twin" if twin else "t_plus_1", **({"twin": twin} if twin else {})})
            room -= gain
            charges += self.costs.order(qty * px, buy=False, symbol=s) + self.costs.order(qty * px, buy=True, symbol=twin or s)
        note = TAX_NOTE
        if lots:
            note = f"Booking these costs about Rs {charges:,.0f} in charges for the sale and the buy-back. " + note
        return {"fy": f"{fy}-{(fy + 1) % 100:02d}", "exempt": exempt, "realized_ltcg": round(realized, 2),
                "realized_other": round(other, 2), "remaining": round(remaining, 2), "harvestable_gain": round(harvestable, 2),
                "lots": lots, "days_left": max((date(fy + 1, 3, 31) - today).days, 0), "note": note}

    def _harvest_step(self, st: dict[str, Any], book: dict[str, Any], now: datetime, allow_new: bool) -> str | None:
        """Book long-term gains inside the year's tax-free allowance, when the owner has asked. The sale and the
        buy-back of one ticker are never on the same day: the buy-back waits for a later session, or goes into a twin."""
        today = now.date()
        h = st.get("harvest") or {}
        if h.get("rebuy") and today.isoformat() > h["after"] and self._can_trade(now):
            b = st.get("basket") or {}
            if h.get("basket") and b.get("id") == h["basket"] and b.get("status") == "open":
                return None  # the sale basket has not been placed yet
            self._refresh_prices([r["symbol"] for r in h["rebuy"]])
            buys = []
            for r in h["rebuy"]:
                px = self._last_px.get(r["symbol"])
                if px:
                    buys.append({"symbol": r["symbol"], "side": "BUY", "qty": int(r["qty"]), "price": round(px, 2),
                                 "value": round(r["qty"] * px, 2), "why": "buys back what was sold to book the gain"})
            st.pop("harvest", None)
            st["harvest_day"] = today.isoformat()
            if self._exec == "paper":
                self._decision = f"{today.isoformat()}:harvest_rebuy"
                filled = self._execute(st, book, buys, now, "harvest_rebuy")
                self.store.event("harvest", "bought back yesterday's harvest at today's price: the cost basis is now higher", orders=filled)
            elif buys:
                self._publish_basket(st, book, buys, "harvest_rebuy", now, target=st.get("target"))
            self.save(st)
            return "harvest: bought back"
        if not st.get("harvest_request"):
            return None
        if not allow_new or not self._can_trade(now):
            return None
        if ((st.get("last_plan") or {}).get("at") or "")[:10] == today.isoformat():
            # Orders already went out today. A sale of the same ticker now could be netted against them.
            if st.get("harvest_waits") != today.isoformat():
                st["harvest_waits"] = today.isoformat()
                self.store.event("harvest", "orders were placed today, so the harvest waits for the next session")
                self.save(st)
            return "harvest: waits for the next session"
        st.pop("harvest_request", None)
        if h.get("rebuy") or (self._exec != "paper" and (st.get("basket") or {}).get("status") == "open"):
            self.store.event("harvest", "not started: an earlier harvest or basket is still open. Finish that first.")
            self.save(st)
            return "harvest: waiting for an open basket"
        self._refresh_prices(list(book["lots"]))
        proposal = self._tax_year(book, now)["lots"]
        if not proposal:
            self.store.event("harvest", "nothing to harvest: no long-term equity gain is available inside this year's allowance")
            self.save(st)
            return "harvest: nothing to do"
        twins = [p["twin"] for p in proposal if p["via"] == "twin"]
        if twins:
            self._refresh_prices(twins)
        orders, rebuy = [], []
        for p in proposal:
            s, px = p["symbol"], self._last_px[p["symbol"]]
            orders.append({"symbol": s, "side": "SELL", "qty": p["qty"], "price": round(px, 2), "value": round(p["qty"] * px, 2),
                           "why": f"books Rs {p['gain']:,.0f} of long-term gain inside this year's tax-free allowance"})
            tpx = self._last_px.get(p.get("twin", ""))
            if p["via"] == "twin" and tpx:
                tq = math.floor(p["qty"] * px * 0.996 / tpx)
                if tq >= 1:
                    orders.append({"symbol": p["twin"], "side": "BUY", "qty": tq, "price": round(tpx, 2), "value": round(tq * tpx, 2),
                                   "why": f"the same index as {s}, bought today so the money stays invested"})
                    st.setdefault("aliases", {})[p["twin"]] = self._aliases.get(s, s)
                    continue
            rebuy.append({"symbol": s, "qty": p["qty"]})
        self._aliases = dict(st.get("aliases") or {})
        orders.sort(key=lambda o: o["side"] != "SELL")
        basket_id = None
        if self._exec == "paper":
            self._decision = f"{today.isoformat()}:harvest"
            filled = self._execute(st, book, orders, now, "harvest")
            self.store.event("harvest", f"booked long-term gains on {', '.join(p['symbol'] for p in proposal)}", orders=filled)
        else:
            basket_id = self._publish_basket(st, book, orders, "harvest", now, target=st.get("target"))["id"]
        st["harvest_day"] = today.isoformat()
        if rebuy:
            st["harvest"] = {"rebuy": rebuy, "after": today.isoformat(), "basket": basket_id}
        self.save(st)
        return "harvest: sold to book gains" + ("; buy-back on the next session" if rebuy else "")

    # Reporting

    def _equity(self, book: dict[str, Any], now: datetime) -> None:
        value = self._value(book)
        self.store.insert("equity", {"at": now.isoformat(), "mode": self._row_mode(),
                                     "realized_pnl": round(value - (book.get("capital") or value), 2), "unrealized_pnl": 0.0,
                                     "open_positions": len(book["lots"])})

    def _next_tick_by(self, now: datetime) -> datetime:
        """When the dashboard should next expect a heartbeat; later than that, the scheduler is not calling."""
        if self.scheduler != "serverless":
            return now + timedelta(seconds=max(self.poll * 3, 45))
        step = timedelta(minutes=max(self.tick_minutes, 1) * 2 + 2)
        if self.clock.is_market_open(now) and (now + step).time() < MARKET_CLOSE:
            return now + step
        d = now.date() if now.time() < MARKET_OPEN and self.clock.is_trading_day(now.date()) else next_trading_day(self.clock, now.date())
        return datetime.combine(d, MARKET_OPEN, tzinfo=now.tzinfo) + step

    def _actual_view(self, st: dict[str, Any], strat: Any) -> dict[str, Any]:
        actual = st.get("actual") or {}
        plan = self._plan_symbols(strat, st)
        px_extra = actual.get("px") or {}
        rows, outside = [], 0.0
        for r in actual.get("rows") or []:
            s = r["symbol"]
            ltp = self._last_px.get(s) or px_extra.get(s)
            value = round(r["qty"] * ltp, 2) if ltp else None
            in_plan = s in plan
            if not in_plan:
                outside += value if value is not None else r["qty"] * r.get("avg_price", 0.0)
            rows.append({"symbol": s, "qty": r["qty"], "avg_price": r.get("avg_price", 0.0), "ltp": round(ltp, 2) if ltp else None,
                         "value": value, "kind": daily.asset_class(s), "in_plan": in_plan})
        return {"source": actual.get("source"), "synced_at": actual.get("synced_at"), "holdings": rows,
                "outside_plan_value": round(outside, 2)}

    def _heartbeat(self, st: dict[str, Any], book: dict[str, Any], strat: Any, now: datetime, control: dict) -> None:
        value = self._value(book)
        if self._exec == "guided" and book.get("capital") is None and book["lots"] and all(self._last_px.get(s) for s in book["lots"]):
            book["capital"] = round(value, 2)  # the starting point for "since you started", fixed at the first priced look
            self.save(st)
        capital = book.get("capital") if book.get("capital") is not None else value
        holdings = []
        for s, lot in sorted(book["lots"].items()):
            px = self._px(book, s)
            holdings.append({"symbol": s, "qty": lot["qty"], "avg_price": round(lot["cost"] / lot["qty"], 2),
                             "ltp": round(px, 2), "value": round(lot["qty"] * px, 2),
                             "weight": round(lot["qty"] * px / value * 100, 1) if value else 0,
                             "pnl": round(lot["qty"] * px - lot["cost"], 2), "since": lot.get("since") or now.isoformat()})
        today = now.date()
        nxt = today if self.clock.is_trading_day(today) and now.time() < self.run_at else next_trading_day(self.clock, today)
        if not st.get("pending"):
            while not daily.REBALANCE[strat.rebalance](nxt, next_trading_day(self.clock, nxt)):
                nxt = next_trading_day(self.clock, nxt)
        running = not control.get("kill_switch") and bool(control.get("trading_enabled"))
        weights = self._target_weights(st, strat)
        drift, next_deposit = self._drift(book, weights)
        basket = st.get("basket")
        public_basket = None
        if basket:
            public_basket = {k: basket[k] for k in ("id", "at", "reason", "status", "reconciled_at", "mismatch") if k in basket}
            public_basket["orders"] = [{k: o[k] for k in ("symbol", "side", "qty", "limit", "value", "why")} for o in basket["orders"]]
        self.store.set_control("heartbeat", {
            "at": now.isoformat(), "wall_at": now_ist().isoformat(), "mode": "live" if self._exec == "auto" else "paper",
            "style": "invest", "strategy": strat.name, "open_positions": len(holdings), "positions": [],
            "realized_pnl": round(value - capital, 2), "unrealized_pnl": 0.0, "trades_today": 0,
            "halted": False, "market_open": self.clock.is_market_open(now), "capital": capital,
            "trading": "running" if running else "stopped", "feed": self.feed_status() if self.feed_status else None,
            "scheduler": self.scheduler, "next_tick_by": self._next_tick_by(now).isoformat(),
            "portfolio": {"value": round(value, 2), "cash": round(book.get("cash", 0.0), 2), "capital": capital,
                          "invested_pct": round((value - book.get("cash", 0.0)) / value * 100, 1) if value else 0,
                          "holdings": holdings, "next_rebalance": nxt.isoformat(), "last_run": st.get("last_run"),
                          "run_at": self.run_at.strftime("%H:%M"), "rebalance": strat.rebalance, "filter": self._filter,
                          "realized": book.get("realized", 0.0), "pending": bool(st.get("pending")),
                          "missed": st.get("missed"), "last_plan": st.get("last_plan"),
                          "liquid_symbol": self.liquid_symbol, "signals": st.get("signals"),
                          "target": getattr(strat, "weights", None) or (st.get("last_plan") or {}).get("target"),
                          # How orders are carried out, the drift corridors, deposits, the tax year, the basket and
                          # what is really held (dashboard/lib/portfolio.ts).
                          "exec_mode": self._exec, "exec_note": self._exec_note,
                          "band": {"abs_pct": self.band_abs_pct, "rel_pct": self.band_rel_pct},
                          "drift": drift, "next_deposit": next_deposit, "tax_year": self._tax_year(book, now),
                          "basket": public_basket, "actual": self._actual_view(st, strat),
                          "pending_deposit": round(book.get("deposit_pending", 0.0), 2)},
        })
