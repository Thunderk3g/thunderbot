"""Small, dependency-free indicator helpers operating on lists of candles."""

from __future__ import annotations

from collections.abc import Sequence

from .models import Candle


def ema(values: Sequence[float], period: int) -> list[float]:
    if period <= 0:
        raise ValueError("period must be positive")
    out: list[float] = []
    k = 2.0 / (period + 1)
    for i, v in enumerate(values):
        out.append(v if i == 0 else v * k + out[-1] * (1 - k))
    return out


def session_vwap(bars: Sequence[Candle]) -> list[float]:
    """Cumulative VWAP over the bars given (pass only the current session)."""
    out: list[float] = []
    pv = vol = 0.0
    for b in bars:
        typical = (b.high + b.low + b.close) / 3.0
        pv += typical * b.volume
        vol += b.volume
        out.append(pv / vol if vol > 0 else typical)
    return out


def true_ranges(bars: Sequence[Candle]) -> list[float]:
    out: list[float] = []
    for i, b in enumerate(bars):
        if i == 0:
            out.append(b.high - b.low)
        else:
            pc = bars[i - 1].close
            out.append(max(b.high - b.low, abs(b.high - pc), abs(b.low - pc)))
    return out


def atr(bars: Sequence[Candle], period: int = 14) -> float | None:
    trs = true_ranges(bars)
    if len(trs) < period:
        return None
    # Wilder smoothing
    value = sum(trs[:period]) / period
    for tr in trs[period:]:
        value = (value * (period - 1) + tr) / period
    return value


def opening_range(bars: Sequence[Candle], n_bars: int) -> tuple[float, float] | None:
    if len(bars) < n_bars or n_bars <= 0:
        return None
    window = bars[:n_bars]
    return max(b.high for b in window), min(b.low for b in window)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def rsi(values: Sequence[float], period: int = 14) -> float | None:
    """Wilder RSI of the last value. None until there are ``period + 1`` values."""
    if len(values) <= period:
        return None
    gains = losses = 0.0
    for i in range(1, period + 1):
        d = values[i] - values[i - 1]
        gains += max(d, 0.0)
        losses += max(-d, 0.0)
    avg_g, avg_l = gains / period, losses / period
    for i in range(period + 1, len(values)):
        d = values[i] - values[i - 1]
        avg_g = (avg_g * (period - 1) + max(d, 0.0)) / period
        avg_l = (avg_l * (period - 1) + max(-d, 0.0)) / period
    if avg_l == 0:
        return 100.0
    rs = avg_g / avg_l
    return 100.0 - 100.0 / (1.0 + rs)
