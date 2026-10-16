"""VWAP mean reversion (intraday, MIS).

Fades a stretched move away from session VWAP once momentum is exhausted (RSI
extreme) and the bar closes back in the reversion direction. Target is VWAP.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..indicators import atr, rsi, session_vwap
from ..models import Candle, Product, Side, Signal
from .base import Strategy


@dataclass
class VWAPReversionParams:
    stretch_atr: float = 2.0  # distance from VWAP, in ATRs, that counts as stretched
    rsi_period: int = 7
    rsi_extreme: float = 25.0  # long when RSI <= this; short when RSI >= 100 - this
    stop_atr: float = 1.0
    min_reward_risk: float = 1.0
    min_bars: int = 6  # don't fade the opening drive
    atr_period: int = 14
    allow_short: bool = True


class VWAPReversion(Strategy):
    name = "vwap_reversion"
    label = "VWAP reversion"
    description = (
        "Fades price stretched far from VWAP when RSI is at an extreme and the bar reverses. "
        "Targets a return to VWAP; skips trades whose target doesn't cover the stop."
    )
    params_cls = VWAPReversionParams
    param_specs = [
        {"name": "stretch_atr", "label": "Stretch (ATR)", "type": "float", "min": 0.5, "max": 5.0, "step": 0.1},
        {"name": "rsi_period", "label": "RSI period", "type": "int", "min": 2, "max": 30, "step": 1},
        {"name": "rsi_extreme", "label": "RSI extreme", "type": "float", "min": 5, "max": 40, "step": 1},
        {"name": "stop_atr", "label": "Stop (ATR)", "type": "float", "min": 0.3, "max": 4.0, "step": 0.1},
        {"name": "min_reward_risk", "label": "Min reward : risk", "type": "float", "min": 0.5, "max": 4.0, "step": 0.1},
        {"name": "min_bars", "label": "Skip first N bars", "type": "int", "min": 1, "max": 30, "step": 1},
    ]

    def __init__(self, params: VWAPReversionParams | None = None) -> None:
        self.p = params or VWAPReversionParams()
        self._fired: set[str] = set()

    def reset_day(self) -> None:
        self._fired.clear()

    def on_bar(self, symbol: str, session_bars: Sequence[Candle], prior_bars: Sequence[Candle] = ()) -> Signal | None:
        p = self.p
        if symbol in self._fired or len(session_bars) < p.min_bars:
            return None
        history = (list(prior_bars[-p.atr_period * 4:]) + list(session_bars))[-p.atr_period * 5:]
        a = atr(history, p.atr_period)
        closes = [b.close for b in history][-p.rsi_period * 5:]
        r = rsi(closes, p.rsi_period)
        if a is None or r is None or a <= 0:
            return None
        bar = session_bars[-1]
        vwap = session_vwap(session_bars)[-1]
        stretch = (bar.close - vwap) / a

        side: Side | None = None
        if stretch <= -p.stretch_atr and r <= p.rsi_extreme and bar.close > bar.open:
            side = Side.BUY
        elif p.allow_short and stretch >= p.stretch_atr and r >= 100 - p.rsi_extreme and bar.close < bar.open:
            side = Side.SELL
        if side is None:
            return None

        entry = bar.close
        if side is Side.BUY:
            stop = min(bar.low, entry - p.stop_atr * a)
        else:
            stop = max(bar.high, entry + p.stop_atr * a)
        target = vwap
        risk = abs(entry - stop)
        if risk <= 0 or abs(target - entry) / risk < p.min_reward_risk:
            return None

        self._fired.add(symbol)
        return Signal(
            symbol=symbol, side=side, product=Product.MIS,
            entry=round(entry, 2), stop=round(stop, 2), target=round(target, 2),
            strategy=self.name, ts=bar.ts,
            reason=(f"Price {abs(stretch):.1f} ATR {'below' if side is Side.BUY else 'above'} VWAP {vwap:.2f}, "
                    f"RSI({p.rsi_period}) {r:.0f}, reversal bar; targeting VWAP"),
            features={"vwap": round(vwap, 2), "atr": round(a, 3), "rsi": round(r, 1),
                      "stretch_atr": round(stretch, 2), "bars_into_session": len(session_bars)},
        )
