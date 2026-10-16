"""EMA trend pullback (intraday, MIS).

In an established intraday trend (fast EMA above slow EMA, price on the right
side of VWAP), buys a pullback that tags the slow EMA and closes back above the
fast EMA. Mirror for shorts.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..indicators import atr, ema, session_vwap
from ..models import Candle, Product, Side, Signal
from .base import Strategy


@dataclass
class EMAPullbackParams:
    fast: int = 9
    slow: int = 21
    trend_bars: int = 6  # fast must have been beyond slow for this many bars
    stop_atr: float = 0.5  # stop goes this many ATRs beyond the pullback bar's extreme
    reward_risk: float = 2.0
    min_bars: int = 6
    atr_period: int = 14
    allow_short: bool = True


class EMAPullback(Strategy):
    name = "ema_pullback"
    label = "EMA trend pullback"
    description = (
        "Joins an established intraday trend on a pullback to the slow EMA that closes back beyond "
        "the fast EMA, on the right side of VWAP. Stop beyond the pullback bar, fixed reward-to-risk."
    )
    params_cls = EMAPullbackParams
    param_specs = [
        {"name": "fast", "label": "Fast EMA", "type": "int", "min": 3, "max": 30, "step": 1},
        {"name": "slow", "label": "Slow EMA", "type": "int", "min": 10, "max": 80, "step": 1},
        {"name": "trend_bars", "label": "Trend bars", "type": "int", "min": 1, "max": 30, "step": 1},
        {"name": "stop_atr", "label": "Stop buffer (ATR)", "type": "float", "min": 0.0, "max": 3.0, "step": 0.1},
        {"name": "reward_risk", "label": "Reward : risk", "type": "float", "min": 0.5, "max": 5.0, "step": 0.1},
        {"name": "min_bars", "label": "Skip first N bars", "type": "int", "min": 1, "max": 30, "step": 1},
    ]

    def __init__(self, params: EMAPullbackParams | None = None) -> None:
        self.p = params or EMAPullbackParams()
        self._fired: set[str] = set()

    def reset_day(self) -> None:
        self._fired.clear()

    def on_bar(self, symbol: str, session_bars: Sequence[Candle], prior_bars: Sequence[Candle] = ()) -> Signal | None:
        p = self.p
        if symbol in self._fired or len(session_bars) < p.min_bars or p.fast >= p.slow:
            return None
        tail = max(p.slow * 5, p.atr_period * 5)
        history = (list(prior_bars[-tail:]) + list(session_bars))[-tail:]
        if len(history) < p.slow + p.trend_bars:
            return None
        closes = [b.close for b in history]
        f, s = ema(closes, p.fast), ema(closes, p.slow)
        a = atr(history[-p.atr_period * 5:], p.atr_period)
        if a is None or a <= 0:
            return None
        bar = session_bars[-1]
        vwap = session_vwap(session_bars)[-1]
        up_trend = all(f[-i] > s[-i] for i in range(2, p.trend_bars + 2))
        down_trend = all(f[-i] < s[-i] for i in range(2, p.trend_bars + 2))

        side: Side | None = None
        if up_trend and bar.low <= s[-1] and bar.close > f[-1] and bar.close > bar.open and bar.close > vwap:
            side = Side.BUY
        elif (p.allow_short and down_trend and bar.high >= s[-1] and bar.close < f[-1]
              and bar.close < bar.open and bar.close < vwap):
            side = Side.SELL
        if side is None:
            return None

        entry = bar.close
        stop = bar.low - p.stop_atr * a if side is Side.BUY else bar.high + p.stop_atr * a
        risk = abs(entry - stop)
        if risk <= 0:
            return None
        target = entry + side.sign * p.reward_risk * risk

        self._fired.add(symbol)
        return Signal(
            symbol=symbol, side=side, product=Product.MIS,
            entry=round(entry, 2), stop=round(stop, 2), target=round(target, 2),
            strategy=self.name, ts=bar.ts,
            reason=(f"{'Up' if side is Side.BUY else 'Down'}trend (EMA{p.fast} {'>' if side is Side.BUY else '<'} "
                    f"EMA{p.slow} for {p.trend_bars}+ bars); pullback tagged EMA{p.slow} {s[-1]:.2f} and closed back "
                    f"{'above' if side is Side.BUY else 'below'} EMA{p.fast}"),
            features={"ema_fast": round(f[-1], 2), "ema_slow": round(s[-1], 2), "vwap": round(vwap, 2),
                      "atr": round(a, 3), "bars_into_session": len(session_bars)},
        )
