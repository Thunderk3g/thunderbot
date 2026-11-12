"""Turn intraday history into labelled examples: every setup the generators produced, with the
features it had when it fired and what a trade on it would actually have made after costs.

The label uses the same fills as the backtester: entry at the next bar's open, stop before target
inside a bar, everything closed at the flatten time, slippage against the trade, Groww's charges.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from ..clock import MarketClock
from ..config import Settings
from ..costs import CostModel
from ..data import group_by_day
from ..models import Candle, Side, Signal
from . import INDEX, features

PRIOR_BARS = 400


@dataclass
class Sample:
    day: date
    symbol: str
    ts: str
    generator: str
    side: str
    x: list[float]
    y: int  # 1 when the trade made money after costs
    r_net: float  # result in units of the risk taken (1R = distance from entry to stop), after costs
    outcome: str


def size_for(sig: Signal, s: Settings) -> int:
    """Shares the risk manager would allow at full size (no LLM shrink), ignoring other open positions."""
    if sig.risk_per_share <= 0 or sig.entry <= 0:
        return 0
    qty = math.floor(s.capital * s.risk_per_trade_pct / 100.0 / sig.risk_per_share)
    cap = s.capital * s.max_leverage * s.max_position_notional_pct / 100.0
    return max(min(qty, math.floor(cap / sig.entry)), 0)


def simulate(sig: Signal, later: Sequence[Candle], s: Settings, clock: MarketClock, costs: CostModel) -> tuple[float, str] | None:
    """Net result in R of taking ``sig`` at the next bar's open. None when it could not have been filled."""
    if not later:
        return None
    slip = s.slippage_bps / 10_000.0
    long = sig.side is Side.BUY
    first = later[0]
    fill = first.open * (1 + slip * sig.side.sign)
    if clock.should_flatten(first.ts) or not ((sig.stop < fill < sig.target) if long else (sig.target < fill < sig.stop)):
        return None
    qty = size_for(sig, s)
    if qty < 1:
        return None

    def adverse(px: float) -> float:
        return px * (1 - slip if long else 1 + slip)

    exit_px, outcome = adverse(later[-1].close), "eod"
    for bar in later:
        if clock.should_flatten(bar.ts):
            exit_px, outcome = adverse(bar.open), "eod"
            break
        if (long and bar.open <= sig.stop) or (not long and bar.open >= sig.stop):
            exit_px, outcome = adverse(bar.open), "stop"
            break
        if (long and bar.low <= sig.stop) or (not long and bar.high >= sig.stop):
            exit_px, outcome = adverse(sig.stop), "stop"
            break
        if (long and bar.open >= sig.target) or (not long and bar.open <= sig.target):
            exit_px, outcome = bar.open, "target"
            break
        if (long and bar.high >= sig.target) or (not long and bar.low <= sig.target):
            exit_px, outcome = sig.target, "target"
            break
    gross = (exit_px - fill) * qty * sig.side.sign
    net = gross - costs.round_trip(sig.side, qty, fill, exit_px, sig.product)
    return net / (qty * sig.risk_per_share), outcome


def build_samples(data: dict[str, list[Candle]], s: Settings, clock: MarketClock | None = None,
                  costs: CostModel | None = None, progress: Callable[[float], Any] = lambda p: None,
                  min_stop_pct: float = 0.0) -> list[Sample]:
    from ..strategy.ai import make_generators, widen

    clock = clock or s.clock()
    costs = costs or CostModel()
    index_days = group_by_day(data.get(INDEX, []))
    symbols = [sym for sym in data if sym != INDEX]
    out: list[Sample] = []
    for n, sym in enumerate(symbols):
        prior: list[Candle] = []
        for day, bars in group_by_day(data[sym]).items():
            if not clock.is_trading_day(day):
                continue
            gens = make_generators(s.allow_short)
            idx = index_days.get(day, [])
            for i in range(len(bars)):
                session = bars[: i + 1]
                for g in gens:
                    sig = g.on_bar(sym, session, prior)
                    if sig is None or not clock.in_entry_window(sig.ts + _interval(s)):
                        continue
                    sig = widen(sig, min_stop_pct)
                    res = simulate(sig, bars[i + 1:], s, clock, costs)
                    if res is None:
                        continue
                    r_net, outcome = res
                    feats = features.build(sig, session, prior, idx, generator=g.name)
                    out.append(Sample(day, sym, sig.ts.isoformat(), g.name, sig.side.value, features.vector(feats),
                                      int(r_net > 0), round(r_net, 4), outcome))
            prior = (prior + bars)[-PRIOR_BARS:]
        progress((n + 1) / max(len(symbols), 1))
    out.sort(key=lambda x: (x.day, x.ts, x.symbol))
    return out


def _interval(s: Settings):
    from datetime import timedelta

    return timedelta(minutes=s.interval_minutes)
