"""Intraday bars for the AI desk from Yahoo's chart endpoint (free, about a second behind NSE).

Yahoo's intraday answer ends with one extra point stamped with the last trade time, which is not a
bar; it is returned separately as the last price. Bars still forming, off the bar grid or outside
market hours are dropped.
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time, timedelta

from ..chart import ChartError, fetch_candles
from ..clock import IST, to_ist
from ..models import Candle

log = logging.getLogger(__name__)

OPEN, CLOSE = time(9, 15), time(15, 30)
HISTORY_DAYS = 59  # Yahoo keeps 5-minute bars for 60 days


def clean(rows: list[tuple], interval_minutes: int, now: datetime) -> tuple[list[Candle], float | None]:
    """(completed bars oldest first, last traded price or None)."""
    now = to_ist(now)
    step = timedelta(minutes=interval_minutes)
    bars: dict[datetime, Candle] = {}
    last_price: float | None = None
    for ts, o, h, low, c, v in rows:
        ts = to_ist(ts)
        if c > 0:
            last_price = c
        aligned = ts.second == 0 and ts.microsecond == 0 and (ts.hour * 60 + ts.minute - 555) % interval_minutes == 0
        if not aligned or not (OPEN <= ts.time() < CLOSE) or ts + step > now:
            continue
        if min(o, h, low, c) <= 0 or h < low:
            continue
        bars[ts] = Candle(ts, o, max(h, o, c), min(low, o, c), c, v)
    return [bars[k] for k in sorted(bars)], last_price


def fetch_one(symbol: str, interval_minutes: int, start: datetime, now: datetime, get=None) -> tuple[list[Candle], float | None]:
    rows = fetch_candles(symbol, interval_minutes, start, now + timedelta(minutes=1), get=get)
    return clean(rows, interval_minutes, now)


def fetch_many(symbols: list[str], interval_minutes: int, days: int, now: datetime, get=None,
               workers: int = 8) -> tuple[dict[str, list[Candle]], dict[str, float], dict[str, str]]:
    """Bars, last prices and errors by symbol. A symbol Yahoo refuses is reported, never guessed."""
    start = now - timedelta(days=days)
    bars: dict[str, list[Candle]] = {}
    prices: dict[str, float] = {}
    errors: dict[str, str] = {}

    def one(sym: str):
        try:
            return sym, fetch_one(sym, interval_minutes, start, now, get), None
        except (ChartError, ValueError, KeyError, TypeError) as e:
            return sym, None, f"{type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(symbols) or 1))) as pool:
        for sym, res, err in pool.map(one, symbols):
            if res and res[0]:
                bars[sym] = res[0]
                if res[1]:
                    prices[sym] = res[1]
            else:
                errors[sym] = err or "no bars"
    return bars, prices, errors


def split_today(bars: list[Candle], now: datetime, keep_prior: int = 400) -> tuple[list[Candle], list[Candle]]:
    today = to_ist(now).date()
    return [b for b in bars if b.ts.date() == today], [b for b in bars if b.ts.date() < today][-keep_prior:]


__all__ = ["IST", "HISTORY_DAYS", "clean", "fetch_one", "fetch_many", "split_today"]
