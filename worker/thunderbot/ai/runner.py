"""The AI desk as a function that is woken once per 5-minute bar.

Nothing stays running. Each call reads its state from the store, works through the bars that closed
since the last call, and writes the state back:

1. fill entries decided on the previous bar; exit positions whose stop or target a bar touched
   (stop first when both were inside one bar); close everything from the flatten time;
2. stop for the day when the loss limit is reached;
3. on the bar that just closed: replay today's bars through the setup generators, score the new
   setups with the model, ask the LLM trader about those that pass, apply the risk limits, enter;
4. follow every setup (taken, skipped or vetoed) to its stop, target or the close, so the journal
   shows what each decision was worth.

This is paper trading. Fills are simulated from bars with slippage and Groww's charges, the same
way the backtester and the training labels do it. Real orders need a machine with a registered
static IP, where ``thunderbot live`` runs the same strategy, model and LLM through the trading engine.
"""

from __future__ import annotations

import dataclasses
import logging
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from ..clock import now_ist, to_ist
from ..config import Settings
from ..costs import CostModel
from ..indicators import session_vwap
from ..llm.types import LLMDecision, ReviewContext
from ..models import Candle, ManagedPosition, Product, Side, Signal
from ..risk import DayState, RiskManager
from ..store import new_id
from . import INDEX, features
from .market import fetch_many, split_today

log = logging.getLogger(__name__)

STATE_KEY, DESK_KEY, HISTORY_KEY, MEMORY_KEY, PARAMS_KEY = "intraday_state", "ai_desk", "ai_history", "ai_memory", "ai_params"
SETTLE_SECONDS = 6.0  # wait this long after a bar closes for Yahoo to publish it
FRESH_SECONDS = 200.0  # enter only on a bar that closed this recently
MAX_REVIEWS_PER_BAR = 4
MAX_DECISIONS = 80
RETRAIN_AFTER_HOURS = 20.0

Fetch = Callable[[list[str], int, int, datetime], tuple[dict[str, list[Candle]], dict[str, float], dict[str, str]]]


def _hm(ts: datetime) -> str:
    return to_ist(ts).strftime("%H:%M")


class IntradayRunner:
    def __init__(self, settings: Settings, store: Any, *, fetch: Fetch | None = None,
                 filter_factory: Callable[[Settings], Any] | None = None, now_fn: Callable[[], datetime] = now_ist,
                 costs: CostModel | None = None, mode: str = "paper", sleep: Callable[[float], None] = time.sleep) -> None:
        self.base = settings
        self.store = store
        self.fetch = fetch or (lambda syms, interval, days, now: fetch_many(syms, interval, days, now))
        self.filter_factory = filter_factory
        self.now = now_fn
        self.costs = costs or CostModel()
        self.mode = mode
        self.sleep = sleep

    # Settings and state

    def _settings(self, control: dict[str, Any]) -> Settings:
        s, _ = self.base.with_overrides(control.get("settings_overrides") or {})
        return dataclasses.replace(s, symbols=list(s.ai_symbols), strategy="ai", strategy_params={})

    def _new_state(self, day: str) -> dict[str, Any]:
        return {"day": day, "last_bar": None, "positions": {}, "pending": {}, "shadows": {}, "decisions": [],
                "risk": {"realized_pnl": 0.0, "trades_opened": 0, "halted": False, "halt_reason": ""},
                "wins": 0, "losses": 0, "costs": 0.0, "curve": [], "finalized": False, "feed_error": None}

    def _state(self, control: dict[str, Any], now: datetime) -> dict[str, Any]:
        st = control.get(STATE_KEY)
        today = now.date().isoformat()
        if not isinstance(st, dict) or st.get("day") != today:
            if isinstance(st, dict) and st.get("day") and not st.get("finalized"):
                self._record_day(st, control)  # yesterday never reached its close here; keep its numbers
            st = self._new_state(today)
        return st

    def _filter(self, s: Settings) -> Any:
        if self.filter_factory is not None:
            return self.filter_factory(s)
        from ..llm.filter import build_filter

        return build_filter(s)

    # One call

    def tick(self) -> dict[str, Any]:
        now = to_ist(self.now())
        control = self.store.get_control()
        s = self._settings(control)
        clock = s.clock()
        st = self._state(control, now)
        enabled = bool(control.get("intraday_enabled")) and not control.get("kill_switch")
        busy = bool(st["positions"] or st["pending"] or st["shadows"])
        step = timedelta(minutes=s.interval_minutes)

        if not clock.is_trading_day(now.date()):
            return self._idle(st, s, control, now, "closed", enabled)
        if not clock.is_market_open(now):
            if now.time() >= clock.flatten_at and not st["finalized"] and (busy or st["decisions"]):
                return self._finish_day(st, s, control, now, enabled)
            return self._idle(st, s, control, now, "closed" if now.time() >= clock.flatten_at else "waiting", enabled)
        if not enabled and not busy:
            return self._idle(st, s, control, now, "off", enabled)

        bar_start = clock.last_completed_bar_start(now, s.interval_minutes)
        if bar_start is None:
            return self._idle(st, s, control, now, "waiting", enabled)
        if st["last_bar"] == bar_start.isoformat():
            return {"intraday": "bar already processed"}
        claim = getattr(self.store, "claim", None)
        claim_id = claim(f"intraday {_hm(bar_start)}", now.date().isoformat()) if claim else "local"
        if claim_id is None:
            return {"intraday": "another run has this bar"}
        try:
            wait = SETTLE_SECONDS - (now - (bar_start + step)).total_seconds()
            if wait > 0:
                self.sleep(wait)
                now = to_ist(self.now())
            summary = self._run_bar(st, s, control, now, bar_start, enabled)
        except Exception:
            release = getattr(self.store, "release", None)
            if release and claim_id != "local":
                release(claim_id)
            raise
        finish = getattr(self.store, "finish", None)
        if finish and claim_id != "local":
            finish(claim_id, "done", summary)
        return summary

    def _run_bar(self, st: dict[str, Any], s: Settings, control: dict[str, Any], now: datetime, bar_start: datetime,
                 enabled: bool) -> dict[str, Any]:
        clock = s.clock()
        step = timedelta(minutes=s.interval_minutes)
        bars, prices, errors = self.fetch(list(s.symbols) + [INDEX], s.interval_minutes, 7, now)
        if not any(sym in bars for sym in s.symbols):
            problem = "no prices from Yahoo: " + "; ".join(f"{k} ({v})" for k, v in list(errors.items())[:3])
            if st.get("feed_error") != problem:
                self.store.event("feed_error", problem)
                st["feed_error"] = problem
            self._save(st, s, control, now, "no_prices", enabled)
            return {"intraday": "no prices"}
        st["feed_error"] = None
        sessions: dict[str, list[Candle]] = {}
        priors: dict[str, list[Candle]] = {}
        for sym, rows in bars.items():
            sessions[sym], priors[sym] = split_today([b for b in rows if b.ts <= bar_start], now)
        index_session = sessions.pop(INDEX, [])
        priors.pop(INDEX, None)
        lookup = {sym: {b.ts: b for b in rows} for sym, rows in sessions.items()}

        risk = RiskManager(s, clock)
        risk.state = DayState(day=now.date(), **st["risk"])
        last = datetime.fromisoformat(st["last_bar"]) if st["last_bar"] else None
        timeline = sorted({b.ts for rows in sessions.values() for b in rows if (last is None or b.ts > last)})
        if last is None:
            timeline = timeline[-1:]  # first call today: nothing was open before now, so only the newest bar matters
        for ts in timeline:
            self._process_bar(ts, lookup, st, s, clock, risk)

        fresh = (now - (bar_start + step)).total_seconds() <= FRESH_SECONDS
        can_enter = enabled and not control.get("paused") and not risk.state.halted and fresh
        market = features.regime(index_session, sessions)
        taken = self._scan(st, s, control, risk, sessions, priors, index_session, prices, bar_start, market, can_enter)

        st["risk"] = {"realized_pnl": round(risk.state.realized_pnl, 2), "trades_opened": risk.state.trades_opened,
                      "halted": risk.state.halted, "halt_reason": risk.state.halt_reason}
        st["last_bar"] = bar_start.isoformat()
        unreal = self._unrealized(st, sessions, prices)
        st["curve"] = (st["curve"] + [[_hm(bar_start + step), round(risk.state.realized_pnl + unreal, 2)]])[-90:]
        status = "halted" if risk.state.halted else "paused" if control.get("paused") else "running" if enabled else "closing"
        self._save(st, s, control, now, status, enabled, sessions=sessions, priors=priors, prices=prices, market=market)
        self._ensure_model(control, st)
        return {"intraday": status, "bar": _hm(bar_start), "entered": taken, "open": len(st["positions"]),
                "realized": st["risk"]["realized_pnl"]}

    # Bars: fills, exits, shadows

    def _process_bar(self, ts: datetime, lookup: dict[str, dict[datetime, Candle]], st: dict[str, Any], s: Settings,
                     clock: Any, risk: RiskManager) -> None:
        slip = s.slippage_bps / 10_000.0
        flatten = clock.should_flatten(ts)
        for sym in sorted(set(st["pending"]) | set(st["positions"])):
            bar = lookup.get(sym, {}).get(ts)
            if bar is None:
                continue
            if sym in st["pending"]:
                p = st["pending"].pop(sym)
                sign = 1 if p["side"] == "BUY" else -1
                fill = round(bar.open * (1 + slip * sign), 2)
                ok = (p["stop"] < fill < p["target"]) if sign > 0 else (p["target"] < fill < p["stop"])
                if flatten or not ok:
                    self._mark(st, p["signal_id"], status="not filled", note="price moved past the stop or target before the entry")
                    self.store.event("entry_skipped", f"{sym}: open {bar.open} already outside stop/target", signal_id=p["signal_id"])
                else:
                    self._open(st, risk, p, fill, ts, ts)
            pos = st["positions"].get(sym)
            if pos is None or ts < datetime.fromisoformat(pos["entry_bar"]):
                continue
            long = pos["side"] == "BUY"

            def adverse(px: float, long: bool = long) -> float:
                return px * (1 - slip if long else 1 + slip)

            if flatten:
                self._close(st, risk, sym, adverse(bar.open), ts, "eod_flatten")
            elif (long and bar.open <= pos["stop"]) or (not long and bar.open >= pos["stop"]):
                self._close(st, risk, sym, adverse(bar.open), ts, "stop_gap")
            elif (long and bar.low <= pos["stop"]) or (not long and bar.high >= pos["stop"]):
                self._close(st, risk, sym, adverse(pos["stop"]), ts, "stop")
            elif (long and bar.open >= pos["target"]) or (not long and bar.open <= pos["target"]):
                self._close(st, risk, sym, bar.open, ts, "target_gap")
            elif (long and bar.high >= pos["target"]) or (not long and bar.low <= pos["target"]):
                self._close(st, risk, sym, pos["target"], ts, "target")

        for sid, sh in list(st["shadows"].items()):
            bar = lookup.get(sh["symbol"], {}).get(ts)
            if bar is None or ts <= datetime.fromisoformat(sh["signal_ts"]):
                continue
            long = sh["side"] == "BUY"
            if flatten:
                self._close_shadow(st, sid, bar.open, "eod", ts)
            elif (long and bar.low <= sh["stop"]) or (not long and bar.high >= sh["stop"]):
                self._close_shadow(st, sid, sh["stop"], "stop", ts)
            elif (long and bar.high >= sh["target"]) or (not long and bar.low <= sh["target"]):
                self._close_shadow(st, sid, sh["target"], "target", ts)

        unreal = 0.0
        for sym, pos in st["positions"].items():
            bar = lookup.get(sym, {}).get(ts)
            if bar is not None:
                unreal += (bar.close - pos["entry"]) * pos["qty"] * (1 if pos["side"] == "BUY" else -1)
        was_halted = risk.state.halted
        if risk.check_daily_loss(unreal):
            if not was_halted:
                self.store.event("halt", risk.state.halt_reason)
            for sym in list(st["positions"]):
                bar = lookup.get(sym, {}).get(ts)
                self._close(st, risk, sym, bar.close if bar else st["positions"][sym]["entry"], ts, "daily_loss_halt")
            for p in st["pending"].values():
                self._mark(st, p["signal_id"], status="not filled", note="trading halted for the day")
            st["pending"].clear()

    def _open(self, st: dict[str, Any], risk: RiskManager, p: dict[str, Any], fill: float, at: datetime, entry_bar: datetime) -> None:
        side = Side(p["side"])
        st["positions"][p["symbol"]] = {
            "symbol": p["symbol"], "side": p["side"], "qty": p["qty"], "entry": fill, "stop": p["stop"], "target": p["target"],
            "opened_at": at.isoformat(), "entry_bar": entry_bar.isoformat(), "signal_id": p["signal_id"],
            "generator": p.get("generator"), "ml_prob": p.get("ml_prob"),
        }
        risk.record_open()
        self._order(p["symbol"], side, p["qty"], fill, p["signal_id"], "entry")
        self.store.event("position_opened", f"{p['side']} {p['qty']} {p['symbol']} @ {fill}", signal_id=p["signal_id"], symbol=p["symbol"])
        self._mark(st, p["signal_id"], status="open", fill=fill)

    def _close(self, st: dict[str, Any], risk: RiskManager, sym: str, price: float, ts: datetime, reason: str) -> None:
        pos = st["positions"].pop(sym)
        side, price = Side(pos["side"]), round(price, 2)
        costs = self.costs.round_trip(side, pos["qty"], pos["entry"], price, Product.MIS)
        gross = round((price - pos["entry"]) * pos["qty"] * side.sign, 2)
        net = round(gross - costs, 2)
        risk.record_close(net)
        st["wins" if net > 0 else "losses"] += 1
        st["costs"] = round(st["costs"] + costs, 2)
        self._order(sym, side.opposite(), pos["qty"], price, pos["signal_id"], f"exit:{reason}")
        self.store.insert("trades", {
            "signal_id": pos["signal_id"], "symbol": sym, "side": side, "product": Product.MIS, "qty": pos["qty"],
            "entry_price": pos["entry"], "exit_price": price, "opened_at": pos["opened_at"], "closed_at": ts.isoformat(),
            "exit_reason": reason, "gross_pnl": gross, "costs": costs, "net_pnl": net, "strategy": "ai", "mode": self.mode,
        })
        self.store.event("position_closed", f"{sym} closed ({reason}) net {net:.2f}", symbol=sym)
        self._mark(st, pos["signal_id"], status="closed", exit=reason, exit_price=price, pnl=net)

    def _close_shadow(self, st: dict[str, Any], sid: str, exit_price: float, outcome: str, ts: datetime) -> None:
        sh = st["shadows"].pop(sid)
        risk = abs(sh["entry"] - sh["stop"]) or 1e-9
        sign = 1 if sh["side"] == "BUY" else -1
        r = round((exit_price - sh["entry"]) * sign / risk, 3)
        self.store.insert("signal_outcomes", {**sh, "exit_price": round(exit_price, 2), "outcome": outcome,
                                              "closed_at": ts.isoformat(), "r_multiple": r, "mode": self.mode})
        self._mark(st, sid, r=r, outcome=outcome)

    def _order(self, sym: str, side: Side, qty: int, price: float, signal_id: str, purpose: str) -> None:
        self.store.insert("orders", {
            "order_id": f"paper-{new_id()[:8]}", "reference_id": None, "signal_id": signal_id, "purpose": purpose,
            "symbol": sym, "side": side, "product": Product.MIS, "order_type": "LIMIT", "qty": qty, "price": price,
            "trigger_price": None, "status": "FILLED", "filled_qty": qty, "avg_price": price,
            "message": "simulated from 5-minute bars", "broker": "paper", "mode": self.mode,
        })

    def _mark(self, st: dict[str, Any], signal_id: str, **fields: Any) -> None:
        for d in st["decisions"]:
            if d["id"] == signal_id:
                d.update(fields)
                return

    # The newest bar: setups, model, LLM, risk

    def _strategy(self, s: Settings, control: dict[str, Any]):
        from ..strategy import build_strategy
        from .train import load_active_model

        strat = build_strategy("ai", control.get(PARAMS_KEY) or {}, s.allow_short)
        try:
            row = load_active_model(self.store, (control.get("ai_model") or {}).get("id"))
        except Exception as e:
            log.warning("no model: %s", e)
            row = None
        if row:
            strat.set_model(row.get("model"), row.get("id"))
        return strat

    def _scan(self, st: dict[str, Any], s: Settings, control: dict[str, Any], risk: RiskManager,
              sessions: dict[str, list[Candle]], priors: dict[str, list[Candle]], index_session: list[Candle],
              prices: dict[str, float], bar_start: datetime, market: dict[str, Any], can_enter: bool) -> int:
        clock = s.clock()
        step = timedelta(minutes=s.interval_minutes)
        if not clock.in_entry_window(bar_start + step):
            return 0
        strat = self._strategy(s, control)
        strat.observe_index(index_session)
        fresh = []
        for sym in s.symbols:
            rows = sessions.get(sym) or []
            for i in range(len(rows)):
                strat.last_candidates = []
                strat.on_bar(sym, rows[: i + 1], priors.get(sym, []))
            if rows and rows[-1].ts == bar_start:
                fresh.extend(strat.last_candidates)
        if not fresh:
            return 0
        fresh.sort(key=lambda c: -(c.prob if c.prob is not None else 0.0))
        signal_filter = self._filter(s) if can_enter else None
        summary = control.get("ai_model") or {}
        extra = {
            "market": market,
            "ml": {"track_record": {k: summary.get(k) for k in ("verdict_text", "best", "all") if summary.get(k)}}
            if summary else {"track_record": "no model trained yet; every setup is passed through unscored"},
            "lessons": (control.get(MEMORY_KEY) or {}).get("lessons") or [],
        }
        slip = s.slippage_bps / 10_000.0
        reviews = entered = 0
        for c in fresh:
            sig: Signal = c.signal
            sid = new_id()
            self.store.insert("signals", {
                "id": sid, "symbol": sig.symbol, "side": sig.side, "product": sig.product, "strategy": sig.strategy,
                "signal_ts": sig.ts, "entry": sig.entry, "stop": sig.stop, "target": sig.target, "reason": sig.reason,
                "features": sig.features, "mode": self.mode,
            })
            dec = {"id": sid, "t": _hm(sig.ts + step), "symbol": sig.symbol, "side": sig.side.value, "kind": c.generator,
                   "entry": sig.entry, "stop": sig.stop, "target": sig.target, "prob": None if c.prob is None else round(c.prob, 3),
                   "expected_r": sig.features.get("ml_expected_r"), "why": sig.reason, "verdict": "", "by": "", "note": "", "flags": []}
            st["decisions"] = (st["decisions"] + [dec])[-MAX_DECISIONS:]
            shadow = {"signal_id": sid, "symbol": sig.symbol, "strategy": sig.strategy, "side": sig.side.value, "entry": sig.entry,
                      "stop": sig.stop, "target": sig.target, "signal_ts": sig.ts.isoformat(), "llm_decision": "none",
                      "llm_size_multiplier": None, "risk_approved": False}
            st["shadows"][sid] = shadow

            if not c.taken:
                dec.update(verdict="skip", by="model", note="scored below the floor" if c.prob is not None else "a better setup fired on the same bar")
                continue
            if not can_enter:
                dec.update(verdict="skip", by="desk", note="not taking new trades right now")
                continue
            if sig.symbol in st["positions"] or sig.symbol in st["pending"]:
                dec.update(verdict="skip", by="desk", note="already in this stock")
                continue

            decision: LLMDecision | None = None
            if signal_filter is not None and signal_filter.enabled:
                if reviews >= MAX_REVIEWS_PER_BAR:
                    dec.update(verdict="skip", by="desk", note="too many setups on one bar; only the best-scored are reviewed")
                    continue
                reviews += 1
                book = [{"symbol": p["symbol"], "side": p["side"], "qty": p["qty"], "entry": p["entry"]} for p in st["positions"].values()]
                decision = signal_filter.review(ReviewContext(
                    signal=sig, recent_bars=sessions[sig.symbol][-12:], open_positions=book,
                    day_realized_pnl=risk.state.realized_pnl, trades_today=risk.state.trades_opened, extra=extra))
                self.store.insert("llm_decisions", {
                    "signal_id": sid, "symbol": sig.symbol, "approve": decision.approve, "size_multiplier": decision.size_multiplier,
                    "confidence": decision.confidence, "rationale": decision.rationale, "risk_flags": decision.risk_flags,
                    "model": decision.model, "latency_ms": decision.latency_ms, "input_tokens": decision.input_tokens,
                    "output_tokens": decision.output_tokens, "error": decision.error, "request_id": decision.request_id,
                    "prompt": decision.prompt,
                })
                shadow.update(llm_decision="approve" if decision.approve else "reject", llm_size_multiplier=decision.size_multiplier)
                dec.update(by=decision.model, note=decision.rationale, flags=decision.risk_flags,
                           confidence=round(decision.confidence, 2), size=round(decision.size_multiplier, 2))
                if decision.error:
                    dec["error"] = decision.error

            held = {p["symbol"]: ManagedPosition(p["symbol"], Side(p["side"]), Product.MIS, p["qty"], p["entry"], p["stop"],
                                                 p["target"], bar_start, "paper")
                    for p in list(st["positions"].values()) + [{**q, "entry": q["entry_ref"]} for q in st["pending"].values()]}
            verdict = risk.evaluate(sig, decision, held, bar_start + step, kill_switch=bool(control.get("kill_switch")))
            self.store.insert("events", {"kind": "risk_verdict", "message": "approved" if verdict.approved else "; ".join(verdict.reasons),
                                         "data": {"signal_id": sid, "qty": verdict.qty, "size_multiplier": verdict.size_multiplier}})
            shadow["risk_approved"] = verdict.approved
            if not verdict.approved:
                llm_said_no = decision is not None and not decision.approve
                dec.update(verdict="skip", by=dec["by"] if llm_said_no else "risk limits",
                           note=dec["note"] if llm_said_no else "; ".join(verdict.reasons))
                continue
            dec.update(verdict="take", by=dec["by"] or "model", qty=verdict.qty)
            order = {"symbol": sig.symbol, "side": sig.side.value, "qty": verdict.qty, "stop": sig.stop, "target": sig.target,
                     "signal_id": sid, "generator": c.generator, "ml_prob": dec["prob"], "entry_ref": sig.entry}
            ltp = prices.get(sig.symbol)
            fill = round(ltp * (1 + slip * sig.side.sign), 2) if ltp else None
            inside = fill is not None and ((sig.stop < fill < sig.target) if sig.side is Side.BUY else (sig.target < fill < sig.stop))
            if inside:
                self._open(st, risk, order, fill, bar_start + step, bar_start + step)
            elif fill is None:
                st["pending"][sig.symbol] = order  # no live price: fill at the next bar's open instead
                dec["status"] = "pending"
            else:
                dec.update(status="not filled", note="price moved past the stop or target before the entry")
                continue
            entered += 1
        return entered

    # After the close

    def _finish_day(self, st: dict[str, Any], s: Settings, control: dict[str, Any], now: datetime, enabled: bool) -> dict[str, Any]:
        """Close out anything a missed call left open, record the day, write the review, queue retraining."""
        clock = s.clock()
        if st["positions"] or st["pending"] or st["shadows"]:
            bars, _, _ = self.fetch(list(s.symbols), s.interval_minutes, 3, now)
            lookup = {sym: {b.ts: b for b in rows if b.ts.date() == now.date()} for sym, rows in bars.items()}
            risk = RiskManager(s, clock)
            risk.state = DayState(day=now.date(), **st["risk"])
            last = datetime.fromisoformat(st["last_bar"]) if st["last_bar"] else None
            for ts in sorted({ts for rows in lookup.values() for ts in rows if last is None or ts > last}):
                self._process_bar(ts, lookup, st, s, clock, risk)
            for sym in list(st["positions"]):  # no bar reached the flatten time for this stock
                rows = lookup.get(sym) or {}
                px = rows[max(rows)].close if rows else st["positions"][sym]["entry"]
                self._close(st, risk, sym, px, now, "session_end")
            for sid in list(st["shadows"]):
                sh = st["shadows"][sid]
                rows = lookup.get(sh["symbol"]) or {}
                self._close_shadow(st, sid, rows[max(rows)].close if rows else sh["entry"], "eod", now)
            st["pending"].clear()
            st["risk"] = {"realized_pnl": round(risk.state.realized_pnl, 2), "trades_opened": risk.state.trades_opened,
                          "halted": risk.state.halted, "halt_reason": risk.state.halt_reason}
        st["finalized"] = True
        self._record_day(st, control)
        from .reflect import review_day

        try:
            review_day(self.store, s, st, control)
        except Exception as e:  # the review is a nicety; it must never block the day's close
            log.warning("day review failed: %s", e)
            self.store.event("error", f"AI day review failed: {type(e).__name__}: {e}")
        self._save(st, s, control, now, "closed", enabled)
        self._ensure_model(control, st, after_close=True)
        return {"intraday": "day closed", "realized": st["risk"]["realized_pnl"], "trades": st["risk"]["trades_opened"]}

    def _record_day(self, st: dict[str, Any], control: dict[str, Any]) -> None:
        trades = st["wins"] + st["losses"]
        if not trades and not st["decisions"]:
            return
        history = [h for h in (control.get(HISTORY_KEY) or []) if h.get("day") != st["day"]]
        history.append({"day": st["day"], "net": st["risk"]["realized_pnl"], "trades": trades, "wins": st["wins"],
                        "costs": st["costs"], "setups": len(st["decisions"])})
        self.store.set_control(HISTORY_KEY, history[-250:])

    def _ensure_model(self, control: dict[str, Any], st: dict[str, Any], after_close: bool = False) -> None:
        """Queue a training job when there is no model yet, or after the close when the model is a day old."""
        summary = control.get("ai_model") or {}
        if summary and not after_close:
            return
        if summary:
            try:
                age = now_ist() - datetime.fromisoformat(summary["trained_at"])
            except (KeyError, ValueError):
                age = timedelta(days=9)
            if age < timedelta(hours=RETRAIN_AFTER_HOURS):
                return
        if st.get("train_queued") == st["day"] and not after_close:
            return
        if self.store.select("jobs", {"kind": "train", "status": "queued"}, limit=1):
            return
        self.store.insert("jobs", {"kind": "train", "params": {}, "status": "queued", "progress": 0})
        st["train_queued"] = st["day"]
        self.store.set_control(STATE_KEY, st)

    # Publishing

    def _unrealized(self, st: dict[str, Any], sessions: dict[str, list[Candle]], prices: dict[str, float]) -> float:
        total = 0.0
        for sym, pos in st["positions"].items():
            px = prices.get(sym) or (sessions[sym][-1].close if sessions.get(sym) else pos["entry"])
            total += (px - pos["entry"]) * pos["qty"] * (1 if pos["side"] == "BUY" else -1)
        return total

    def _idle(self, st: dict[str, Any], s: Settings, control: dict[str, Any], now: datetime, status: str, enabled: bool) -> dict[str, Any]:
        desk = control.get(DESK_KEY) or {}
        if desk.get("status") != status or desk.get("enabled") != enabled or desk.get("day") != st["day"]:
            self._save(st, s, control, now, status, enabled)
        if enabled or not control.get("ai_model"):
            self._ensure_model(control, st)
        return {"intraday": status}

    def _save(self, st: dict[str, Any], s: Settings, control: dict[str, Any], now: datetime, status: str, enabled: bool, *,
              sessions: dict[str, list[Candle]] | None = None, priors: dict[str, list[Candle]] | None = None,
              prices: dict[str, float] | None = None, market: dict[str, Any] | None = None) -> None:
        self.store.set_control(STATE_KEY, st)
        prev = control.get(DESK_KEY) or {}
        positions = []
        unreal = 0.0
        for sym, p in st["positions"].items():
            px = (prices or {}).get(sym) or ((sessions or {}).get(sym) or [None])[-1]
            px = px.close if isinstance(px, Candle) else px or p["entry"]
            u = round((px - p["entry"]) * p["qty"] * (1 if p["side"] == "BUY" else -1), 2)
            unreal += u
            positions.append({**{k: p[k] for k in ("symbol", "side", "qty", "entry", "stop", "target", "opened_at", "generator", "ml_prob")},
                              "ltp": round(px, 2), "unrealized": u})
        watch = prev.get("watch") or []
        if sessions is not None:
            watch = []
            for sym in s.symbols:
                rows = sessions.get(sym)
                if not rows:
                    continue
                last = (prices or {}).get(sym) or rows[-1].close
                vwap = session_vwap(rows)[-1]
                prior = (priors or {}).get(sym) or []
                rvol = features.relative_volume(rows, prior)[1] if prior else None
                prev_close = prior[-1].close if prior else rows[0].open
                watch.append({"symbol": sym, "ltp": round(last, 2), "chg_pct": round((last / prev_close - 1) * 100, 2),
                              "vs_vwap_pct": round((last / vwap - 1) * 100, 2) if vwap else 0.0,
                              "rvol": None if rvol is None else round(rvol, 2),
                              "m30_pct": round((rows[-1].close / rows[max(0, len(rows) - 7)].close - 1) * 100, 2)})
        self.store.set_control(DESK_KEY, {
            "at": now.isoformat(), "day": st["day"], "status": status, "enabled": enabled, "mode": self.mode,
            "bar": _hm(datetime.fromisoformat(st["last_bar"]) + timedelta(minutes=s.interval_minutes)) if st["last_bar"] else None,
            "market": market if market is not None else prev.get("market") or {},
            "watch": watch, "positions": positions,
            "pending": [{k: p[k] for k in ("symbol", "side", "qty", "stop", "target")} for p in st["pending"].values()],
            "decisions": st["decisions"][-MAX_DECISIONS:],
            "stats": {"realized": st["risk"]["realized_pnl"], "unrealized": round(unreal, 2), "trades": st["risk"]["trades_opened"],
                      "wins": st["wins"], "losses": st["losses"], "costs": st["costs"], "halted": st["risk"]["halted"],
                      "halt_reason": st["risk"]["halt_reason"], "setups": len(st["decisions"])},
            "curve": st["curve"],
            "llm": {"on": s.llm_enabled and (s.chat_llm or s.llm_provider == "Anthropic"), "provider": s.llm_provider,
                    "model": s.llm_chat_model if s.chat_llm else (s.llm_model if s.llm_enabled else None)},
            "limits": {"capital": s.capital, "risk_per_trade_pct": s.risk_per_trade_pct, "max_daily_loss_pct": s.max_daily_loss_pct,
                       "max_open_positions": s.max_open_positions, "max_trades_per_day": s.max_trades_per_day,
                       "entry_window": f"{s.entry_start}-{s.entry_end}", "flatten_at": s.flatten_at},
            "params": control.get(PARAMS_KEY) or {}, "universe": len(s.symbols), "feed_error": st.get("feed_error"),
        })
