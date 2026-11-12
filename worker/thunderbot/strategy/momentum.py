"""Momentum burst (intraday, MIS): a close at a new session extreme on a volume surge, with VWAP."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..indicators import atr, mean, session_vwap
from ..models import Candle, Product, Side, Signal
from .base import Strategy


@dataclass
class MomentumParams:
    min_bars: int = 9  # not before 10:00: the opening range belongs to the breakout strategy
    volume_mult: float = 1.5
    max_stretch_atr: float = 3.0  # skip a move already this far from VWAP
    atr_stop_mult: float = 1.2
    reward_risk: float = 1.5
    atr_period: int = 14
    allow_short: bool = True


class MomentumBurst(Strategy):
    name = "momentum"
    label = "Momentum burst"
    description = (
        "Trades the first close at a new high (or low) for the day after 10:00, on at least 1.5 times the "
        "usual volume for that time and on the right side of VWAP. ATR stop, fixed reward-to-risk target."
    )
    params_cls = MomentumParams
    param_specs = [
        {"name": "min_bars", "label": "Skip first N bars", "type": "int", "min": 3, "max": 40, "step": 1},
        {"name": "volume_mult", "label": "Volume surge x", "type": "float", "min": 0.5, "max": 4.0, "step": 0.1},
        {"name": "max_stretch_atr", "label": "Max stretch from VWAP (ATR)", "type": "float", "min": 1.0, "max": 8.0, "step": 0.5},
        {"name": "atr_stop_mult", "label": "ATR stop x", "type": "float", "min": 0.5, "max": 4.0, "step": 0.1},
        {"name": "reward_risk", "label": "Reward : risk", "type": "float", "min": 0.5, "max": 5.0, "step": 0.1},
    ]

    def __init__(self, params: MomentumParams | None = None) -> None:
        self.p = params or MomentumParams()
        self._fired: set[str] = set()

    def reset_day(self) -> None:
        self._fired.clear()

    def on_bar(self, symbol: str, session_bars: Sequence[Candle], prior_bars: Sequence[Candle] = ()) -> Signal | None:
        p = self.p
        if symbol in self._fired or len(session_bars) <= p.min_bars:
            return None
        bar, earlier = session_bars[-1], session_bars[:-1]
        slot = bar.ts.time()
        same_slot = [b.volume for b in prior_bars if b.ts.time() == slot]
        base = mean(same_slot) if len(same_slot) >= 2 else mean([b.volume for b in earlier[-6:]])
        if base <= 0 or bar.volume < p.volume_mult * base:
            return None
        history = (list(prior_bars[-p.atr_period * 4:]) + list(session_bars))[-p.atr_period * 5:]
        a = atr(history, p.atr_period)
        if a is None or a <= 0:
            return None
        vwap = session_vwap(session_bars)[-1]
        side: Side | None = None
        if bar.close > max(b.high for b in earlier) and bar.close > vwap:
            side = Side.BUY
        elif p.allow_short and bar.close < min(b.low for b in earlier) and bar.close < vwap:
            side = Side.SELL
        if side is None or abs(bar.close - vwap) > p.max_stretch_atr * a:
            return None
        entry = bar.close
        risk = p.atr_stop_mult * a
        self._fired.add(symbol)
        return Signal(
            symbol=symbol, side=side, product=Product.MIS, entry=round(entry, 2),
            stop=round(entry - side.sign * risk, 2), target=round(entry + side.sign * p.reward_risk * risk, 2),
            strategy=self.name, ts=bar.ts,
            reason=(f"New session {'high' if side is Side.BUY else 'low'} on {bar.volume / base:.1f}x volume, "
                    f"{'above' if side is Side.BUY else 'below'} VWAP {vwap:.2f}"),
            features={"vwap": round(vwap, 2), "atr": round(a, 3), "volume_ratio": round(bar.volume / base, 2),
                      "bars_into_session": len(session_bars)},
        )
