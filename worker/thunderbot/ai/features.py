"""Features of an intraday setup, computed only from bars that had closed when it fired.

Directional numbers are aligned with the trade (multiplied by +1 for a long, -1 for a short), so the
model learns "with the move" and "against the move" once instead of separately for each side.
"""

from __future__ import annotations

from collections.abc import Sequence

from ..indicators import atr, ema, rsi, session_vwap
from ..models import Candle, Signal

GENERATORS = ("orb", "vwap_reversion", "ema_pullback", "momentum")

FEATURES: tuple[str, ...] = (
    "mins", "dow",
    "ret_1", "ret_3", "ret_6", "ret_12", "ret_open", "gap",
    "vwap_dist_atr", "atr_pct", "range_pos", "bar_range_atr", "bar_body",
    "rvol", "cum_rvol", "rsi", "ema_spread_atr", "or_pos", "trend_bars",
    "pd_ext_dist_atr", "pd_opp_dist_atr",
    "idx_ret_open", "idx_ret_6", "idx_range_pos", "rel_strength",
    "stop_pct", "reward_risk", "side",
    *(f"gen_{g}" for g in GENERATORS),
)


def _pct(a: float, b: float) -> float:
    return (a / b - 1.0) * 100.0 if b else 0.0


def _clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _ret(closes: Sequence[float], n: int) -> float:
    """Percent change over the last ``n`` bars, or since the first bar when the session is younger."""
    if len(closes) < 2:
        return 0.0
    return _pct(closes[-1], closes[max(0, len(closes) - 1 - n)])


def atr_of(session: Sequence[Candle], prior: Sequence[Candle], period: int = 14) -> float:
    history = (list(prior[-period * 4:]) + list(session))[-period * 5:]
    a = atr(history, period)
    if a is None or a <= 0:
        spans = [b.high - b.low for b in history] or [0.0]
        a = sum(spans) / len(spans)
    return a if a > 0 else max(session[-1].close * 0.002, 0.01)


def relative_volume(session: Sequence[Candle], prior: Sequence[Candle]) -> tuple[float, float]:
    """(this bar's volume, today's cumulative volume) against the same time of day on earlier sessions."""
    bar = session[-1]
    slot = bar.ts.time()
    by_day: dict = {}
    for b in prior:
        by_day.setdefault(b.ts.date(), []).append(b)
    same_slot = [b.volume for bars in by_day.values() for b in bars if b.ts.time() == slot]
    cum_prior = [sum(b.volume for b in bars if b.ts.time() <= slot) for bars in by_day.values()]
    base = sum(same_slot) / len(same_slot) if same_slot else 0.0
    cum_base = sum(cum_prior) / len(cum_prior) if cum_prior else 0.0
    rvol = bar.volume / base if base > 0 else 1.0
    cum = sum(b.volume for b in session) / cum_base if cum_base > 0 else 1.0
    return _clip(rvol, 0.0, 10.0), _clip(cum, 0.0, 10.0)


def build(sig: Signal, session: Sequence[Candle], prior: Sequence[Candle] = (),
          index_session: Sequence[Candle] = (), generator: str | None = None) -> dict[str, float]:
    """``session`` is today's bars up to and including the bar the signal fired on."""
    sign = float(sig.side.sign)
    bar = session[-1]
    closes = [b.close for b in session]
    a = atr_of(session, prior)
    vwap = session_vwap(session)[-1]
    hi, lo = max(b.high for b in session), min(b.low for b in session)
    span = hi - lo
    pos = (bar.close - lo) / span if span > 0 else 0.5
    bar_span = bar.high - bar.low
    rvol, cum_rvol = relative_volume(session, prior)
    r = rsi(([b.close for b in prior[-30:]] + closes)[-60:], 14)
    r = 50.0 if r is None else r
    seed = [b.close for b in prior[-60:]] + closes
    spread = ema(seed, 9)[-1] - ema(seed, 21)[-1]
    first = session[:3]
    or_hi, or_lo = max(b.high for b in first), min(b.low for b in first)
    or_span = or_hi - or_lo
    last12 = session[-12:]
    with_trade = sum(1 for b in last12 if (b.close - b.open) * sign > 0) / len(last12)

    prev_day = [b for b in prior if b.ts.date() == prior[-1].ts.date()] if prior else []
    if prev_day:
        pd_hi, pd_lo, pd_close = max(b.high for b in prev_day), min(b.low for b in prev_day), prev_day[-1].close
        gap = _pct(session[0].open, pd_close)
        ext = (bar.close - pd_hi) / a if sign > 0 else (pd_lo - bar.close) / a
        opp = (bar.close - pd_lo) / a if sign > 0 else (pd_hi - bar.close) / a
    else:
        gap = ext = opp = 0.0

    ret_open = _pct(bar.close, session[0].open)
    idx = [b for b in index_session if b.ts <= bar.ts]
    if idx:
        idx_closes = [b.close for b in idx]
        idx_ret_open = _pct(idx_closes[-1], idx[0].open)
        idx_ret_6 = _ret(idx_closes, 6)
        ih, il = max(b.high for b in idx), min(b.low for b in idx)
        idx_pos = (idx_closes[-1] - il) / (ih - il) if ih > il else 0.5
    else:
        idx_ret_open = idx_ret_6 = 0.0
        idx_pos = 0.5

    gen = generator or sig.strategy
    f = {
        "mins": ((bar.ts.hour * 60 + bar.ts.minute) - 555) / 375.0,
        "dow": bar.ts.weekday() / 4.0,
        "ret_1": _ret(closes, 1) * sign,
        "ret_3": _ret(closes, 3) * sign,
        "ret_6": _ret(closes, 6) * sign,
        "ret_12": _ret(closes, 12) * sign,
        "ret_open": ret_open * sign,
        "gap": _clip(gap, -10.0, 10.0) * sign,
        "vwap_dist_atr": _clip((bar.close - vwap) / a, -20.0, 20.0) * sign,
        "atr_pct": a / bar.close * 100.0,
        "range_pos": pos if sign > 0 else 1.0 - pos,
        "bar_range_atr": _clip(bar_span / a, 0.0, 10.0),
        "bar_body": ((bar.close - bar.open) / bar_span if bar_span > 0 else 0.0) * sign,
        "rvol": rvol,
        "cum_rvol": cum_rvol,
        "rsi": (r if sign > 0 else 100.0 - r) / 100.0,
        "ema_spread_atr": _clip(spread / a, -20.0, 20.0) * sign,
        "or_pos": _clip((bar.close - (or_hi + or_lo) / 2) / or_span if or_span > 0 else 0.0, -10.0, 10.0) * sign,
        "trend_bars": with_trade,
        "pd_ext_dist_atr": _clip(ext, -30.0, 30.0),
        "pd_opp_dist_atr": _clip(opp, -30.0, 30.0),
        "idx_ret_open": idx_ret_open * sign,
        "idx_ret_6": idx_ret_6 * sign,
        "idx_range_pos": idx_pos if sign > 0 else 1.0 - idx_pos,
        "rel_strength": (ret_open - idx_ret_open) * sign,
        "stop_pct": sig.risk_per_share / sig.entry * 100.0 if sig.entry else 0.0,
        "reward_risk": sig.reward_risk,
        "side": sign,
    }
    for g in GENERATORS:
        f[f"gen_{g}"] = 1.0 if gen == g else 0.0
    return {k: round(float(v), 5) for k, v in f.items()}


def vector(features: dict[str, float], names: Sequence[str] = FEATURES) -> list[float]:
    return [float(features.get(n, 0.0) or 0.0) for n in names]


def regime(index_session: Sequence[Candle], sessions: dict[str, Sequence[Candle]]) -> dict[str, float | str | int]:
    """A plain description of the market so far today: index direction, how far it has travelled, and breadth."""
    out: dict[str, float | str | int] = {"label": "unknown"}
    up = above = n = 0
    for bars in sessions.values():
        if not bars:
            continue
        n += 1
        up += bars[-1].close > bars[0].open
        above += bars[-1].close > session_vwap(bars)[-1]
    if n:
        out["breadth_up_pct"] = round(up / n * 100)
        out["above_vwap_pct"] = round(above / n * 100)
        out["stocks"] = n
    if index_session:
        closes = [b.close for b in index_session]
        hi, lo = max(b.high for b in index_session), min(b.low for b in index_session)
        ret_open = _pct(closes[-1], index_session[0].open)
        span_pct = (hi - lo) / closes[-1] * 100 if closes[-1] else 0.0
        pos = (closes[-1] - lo) / (hi - lo) if hi > lo else 0.5
        out.update(index_ret_open_pct=round(ret_open, 2), index_ret_30m_pct=round(_ret(closes, 6), 2),
                   index_range_pct=round(span_pct, 2), index_range_pos=round(pos, 2), index_last=round(closes[-1], 2))
        breadth = out.get("breadth_up_pct", 50)
        if ret_open > 0.25 and pos > 0.6 and breadth >= 55:
            out["label"] = "trend_up"
        elif ret_open < -0.25 and pos < 0.4 and breadth <= 45:
            out["label"] = "trend_down"
        elif span_pct < 0.45:
            out["label"] = "quiet_range"
        else:
            out["label"] = "choppy"
    return out
