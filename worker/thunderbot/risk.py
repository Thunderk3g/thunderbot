"""Hard risk limits. This module has the final say on every entry.

The LLM review (``thunderbot.llm``) produces an ``LLMDecision`` that can only
veto a signal or scale its size by a factor in [0, 1]. ``RiskManager.evaluate``
clamps that factor and applies its own checks, so no LLM output can increase
size, bypass a limit, or change entry/stop/target.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date, datetime

from .clock import MarketClock, to_ist
from .config import Settings
from .llm.types import LLMDecision
from .models import ManagedPosition, Product, Side, Signal


@dataclass
class RiskVerdict:
    approved: bool
    qty: int = 0
    reasons: list[str] = field(default_factory=list)
    size_multiplier: float = 1.0

    def reject(self, reason: str) -> "RiskVerdict":
        self.approved = False
        self.qty = 0
        self.reasons.append(reason)
        return self


@dataclass
class DayState:
    day: date | None = None
    realized_pnl: float = 0.0
    trades_opened: int = 0
    halted: bool = False
    halt_reason: str = ""


class RiskManager:
    def __init__(self, settings: Settings, clock: MarketClock) -> None:
        self.s = settings
        self.clock = clock
        self.state = DayState()

    # Day lifecycle

    def roll_day(self, ts: datetime) -> None:
        d = to_ist(ts).date()
        if self.state.day != d:
            self.state = DayState(day=d)

    def record_open(self) -> None:
        self.state.trades_opened += 1

    def record_close(self, net_pnl: float) -> None:
        self.state.realized_pnl += net_pnl

    def halt(self, reason: str) -> None:
        if not self.state.halted:
            self.state.halted = True
            self.state.halt_reason = reason

    @property
    def max_daily_loss(self) -> float:
        return self.s.capital * self.s.max_daily_loss_pct / 100.0

    def check_daily_loss(self, unrealized: float) -> bool:
        """Halt for the day if realized + unrealized loss breaches the limit. Returns True if halted."""
        if self.state.realized_pnl + unrealized <= -self.max_daily_loss:
            self.halt(
                f"daily loss limit hit: realized {self.state.realized_pnl:.2f} + "
                f"unrealized {unrealized:.2f} <= -{self.max_daily_loss:.2f}"
            )
        return self.state.halted

    # Entry evaluation

    def evaluate(
        self,
        signal: Signal,
        decision: LLMDecision | None,
        open_positions: dict[str, ManagedPosition],
        now: datetime,
        kill_switch: bool = False,
        available_cash: float | None = None,
    ) -> RiskVerdict:
        self.roll_day(now)
        s = self.s
        v = RiskVerdict(approved=True)

        if kill_switch:
            return v.reject("kill switch engaged")
        if self.state.halted:
            return v.reject(f"trading halted: {self.state.halt_reason}")
        if not self.clock.in_entry_window(now):
            return v.reject("outside entry window")
        if signal.symbol not in s.symbols:
            return v.reject(f"{signal.symbol} not in configured universe")
        if signal.symbol in open_positions:
            return v.reject(f"already holding {signal.symbol}")
        if len(open_positions) >= s.max_open_positions:
            return v.reject(f"max open positions ({s.max_open_positions}) reached")
        if self.state.trades_opened >= s.max_trades_per_day:
            return v.reject(f"max trades per day ({s.max_trades_per_day}) reached")

        # Product rules
        if signal.product is Product.MTF and not s.allow_mtf_api:
            return v.reject("MTF via API is disabled (unverified on Groww); set TB_ALLOW_MTF_API after verifying")
        if signal.side is Side.SELL and signal.product is not Product.MIS:
            return v.reject("short selling is only allowed intraday (MIS)")
        if signal.side is Side.SELL and not s.allow_short:
            return v.reject("short selling disabled")

        # Signal geometry
        if signal.entry <= 0:
            return v.reject("non-positive entry price")
        if signal.side is Side.BUY and not (signal.stop < signal.entry < signal.target):
            return v.reject("long signal must satisfy stop < entry < target")
        if signal.side is Side.SELL and not (signal.target < signal.entry < signal.stop):
            return v.reject("short signal must satisfy target < entry < stop")
        stop_pct = signal.risk_per_share / signal.entry * 100
        if stop_pct > s.max_stop_distance_pct:
            return v.reject(f"stop distance {stop_pct:.2f}% exceeds {s.max_stop_distance_pct}%")

        # LLM review: veto or shrink only
        multiplier = 1.0
        if decision is not None:
            if not decision.approve:
                return v.reject(f"LLM veto: {decision.rationale[:200]}")
            if decision.confidence < s.llm_min_confidence:
                return v.reject(f"LLM confidence {decision.confidence:.2f} below {s.llm_min_confidence}")
            multiplier = min(max(decision.size_multiplier, 0.0), 1.0)
            if multiplier == 0.0:
                return v.reject("LLM size multiplier is zero")
        v.size_multiplier = multiplier

        # Position sizing: fixed fractional risk, then notional caps
        risk_budget = s.capital * s.risk_per_trade_pct / 100.0 * multiplier
        qty = math.floor(risk_budget / signal.risk_per_share)

        leverage = s.max_leverage if signal.product is Product.MIS else 1.0
        notional_cap = s.capital * leverage * s.max_position_notional_pct / 100.0
        qty = min(qty, math.floor(notional_cap / signal.entry))

        used = sum(p.qty * p.entry_price for p in open_positions.values())
        remaining = s.capital * leverage - used
        if available_cash is not None:
            remaining = min(remaining, available_cash * leverage)
        qty = min(qty, math.floor(max(remaining, 0.0) / signal.entry))

        if qty < 1:
            return v.reject("position size rounds to zero under risk/notional limits")
        v.qty = qty
        return v
