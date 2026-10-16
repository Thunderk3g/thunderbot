"""Opening Range Breakout with VWAP and volume confirmation (intraday, MIS)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from ..indicators import atr, mean, opening_range, session_vwap
from ..models import Candle, Product, Side, Signal
from .base import Strategy


@dataclass
class ORBParams:
    range_bars: int = 3  # 3 x 5-min = 15-minute opening range
    min_range_pct: float = 0.3
    max_range_pct: float = 2.5
    volume_mult: float = 1.2  # breakout bar volume vs. typical volume for that time of day
    rvol_lookback_bars: int = 6  # fallback baseline when there is no prior-day history
    reward_risk: float = 2.0
    atr_period: int = 14
    atr_stop_mult: float = 1.5  # stop = tighter of OR-opposite-side and entry -/+ k*ATR
    allow_short: bool = True


class OpeningRangeBreakout(Strategy):
    name = "orb"

    def __init__(self, params: ORBParams | None = None) -> None:
        self.p = params or ORBParams()
        self._fired: set[str] = set()

    def reset_day(self) -> None:
        self._fired.clear()

    def _baseline_volume(self, bar: Candle, session_bars: Sequence[Candle], prior_bars: Sequence[Candle]) -> float:
        """Relative-volume baseline: mean volume of the same time slot on prior days.

        Intraday volume is U-shaped, so comparing a mid-morning bar to the session
        average (dominated by the opening bars) would reject nearly every breakout.
        Falls back to the mean of the last few session bars without prior history.
        """
        slot = bar.ts.time()
        same_slot = [b.volume for b in prior_bars if b.ts.time() == slot]
        if len(same_slot) >= 2:
            return mean(same_slot)
        return mean([b.volume for b in session_bars[-1 - self.p.rvol_lookback_bars : -1]])

    def on_bar(
        self,
        symbol: str,
        session_bars: Sequence[Candle],
        prior_bars: Sequence[Candle] = (),
    ) -> Signal | None:
        p = self.p
        if symbol in self._fired or len(session_bars) <= p.range_bars:
            return None

        rng = opening_range(session_bars, p.range_bars)
        if rng is None:
            return None
        or_high, or_low = rng
        mid = (or_high + or_low) / 2
        range_pct = (or_high - or_low) / mid * 100
        if not (p.min_range_pct <= range_pct <= p.max_range_pct):
            return None

        bar = session_bars[-1]
        prev = session_bars[-2]
        vwap = session_vwap(session_bars)[-1]
        avg_vol = self._baseline_volume(bar, session_bars, prior_bars)
        vol_ok = avg_vol > 0 and bar.volume >= p.volume_mult * avg_vol

        history = list(prior_bars) + list(session_bars)
        a = atr(history, p.atr_period)

        side: Side | None = None
        # A breakout is the first close beyond the range, so the previous bar must still be inside it.
        if bar.close > or_high and prev.close <= or_high and bar.close > vwap and vol_ok:
            side = Side.BUY
        elif p.allow_short and bar.close < or_low and prev.close >= or_low and bar.close < vwap and vol_ok:
            side = Side.SELL
        if side is None:
            return None

        entry = bar.close
        if side is Side.BUY:
            stop = or_low
            if a is not None:
                stop = max(stop, entry - p.atr_stop_mult * a)
        else:
            stop = or_high
            if a is not None:
                stop = min(stop, entry + p.atr_stop_mult * a)
        risk = abs(entry - stop)
        if risk <= 0:
            return None
        target = entry + side.sign * p.reward_risk * risk

        self._fired.add(symbol)
        return Signal(
            symbol=symbol,
            side=side,
            product=Product.MIS,
            entry=round(entry, 2),
            stop=round(stop, 2),
            target=round(target, 2),
            strategy=self.name,
            ts=bar.ts,
            reason=(
                f"{'Up' if side is Side.BUY else 'Down'}side break of {p.range_bars}-bar opening range "
                f"[{or_low:.2f}, {or_high:.2f}] with close {'above' if side is Side.BUY else 'below'} "
                f"VWAP {vwap:.2f} on {bar.volume / avg_vol:.1f}x volume"
            ),
            features={
                "or_high": round(or_high, 2),
                "or_low": round(or_low, 2),
                "range_pct": round(range_pct, 3),
                "vwap": round(vwap, 2),
                "atr": round(a, 3) if a is not None else None,
                "volume_ratio": round(bar.volume / avg_vol, 2),
                "bars_into_session": len(session_bars),
            },
        )
