"""Free market data from Yahoo Finance, through the open-source ``yfinance`` library (Apache-2.0).

Use it to backtest and paper trade without a paid Groww data plan. It is not good enough for live orders:
- Intraday history is short: 1-minute bars for the last 7 days, 2- to 30-minute bars for the last
  60 days, 1-hour bars for about 2 years. Daily bars go back decades.
- Yahoo is an unofficial source. Quotes can lag the exchange, the newest bar's volume is partial, and
  Yahoo can change or rate-limit the service without notice.
"""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Any

from .clock import IST, now_ist, to_ist
from .models import Candle

log = logging.getLogger(__name__)

YF_INTERVALS = {1: "1m", 2: "2m", 5: "5m", 15: "15m", 30: "30m", 60: "60m", 1440: "1d"}
# How far back Yahoo serves each interval (a day of margin under its documented limits).
LOOKBACK_DAYS = {1: 6, 2: 59, 5: 59, 15: 59, 30: 59, 60: 729}
SUFFIX = {"NSE": ".NS", "BSE": ".BO"}

Downloader = Callable[..., Any]


def yahoo_ticker(symbol: str, exchange: str = "NSE") -> str:
    """RELIANCE on NSE -> RELIANCE.NS. Symbols that already carry a suffix or an index caret are kept."""
    if "." in symbol or symbol.startswith("^"):
        return symbol
    return symbol + SUFFIX.get(exchange.upper(), ".NS")


def _download(**kwargs: Any) -> Any:
    import yfinance as yf

    return yf.download(progress=False, auto_adjust=False, threads=False, **kwargs)


def _num(v: Any) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(f) else f


def frame_to_candles(df: Any) -> list[Candle]:
    """A yfinance OHLCV frame (one ticker, flat columns) to candles in exchange time."""
    if df is None or len(df) == 0:
        return []
    out = []
    for ts, row in df.iterrows():
        o, h, l, c = (_num(row.get(k)) for k in ("Open", "High", "Low", "Close"))
        if None in (o, h, l, c):
            continue
        dt = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
        dt = dt.replace(tzinfo=IST) if dt.tzinfo is None else to_ist(dt)
        out.append(Candle(dt, round(o, 2), round(h, 2), round(l, 2), round(c, 2), _num(row.get("Volume")) or 0.0))
    out.sort(key=lambda b: b.ts)
    return out


class YahooMarketData:
    """Historical candles from Yahoo Finance (MarketData protocol)."""

    name = "yahoo"

    def __init__(self, exchange: str = "NSE", downloader: Downloader | None = None,
                 now_fn: Callable[[], datetime] = now_ist) -> None:
        self.exchange = exchange
        self._download = downloader or _download
        self._now = now_fn

    def earliest(self, interval_minutes: int) -> datetime | None:
        days = LOOKBACK_DAYS.get(interval_minutes)
        return None if days is None else self._now() - timedelta(days=days)

    def candles(self, symbol: str, interval_minutes: int, start: datetime, end: datetime) -> list[Candle]:
        if interval_minutes not in YF_INTERVALS:
            raise ValueError(f"Yahoo has no {interval_minutes}-minute bars; choose from {sorted(YF_INTERVALS)}")
        start, end = to_ist(start), min(to_ist(end), self._now() + timedelta(days=1))
        floor = self.earliest(interval_minutes)
        if floor is not None and start < floor:
            start = floor
        if start >= end:
            return []
        df = self._download(tickers=yahoo_ticker(symbol, self.exchange), start=start, end=end,
                            interval=YF_INTERVALS[interval_minutes], multi_level_index=False)
        return [c for c in frame_to_candles(df) if start <= c.ts < end]


class YahooQuotes:
    """Last traded prices from Yahoo's 1-minute bars, one request for all symbols, cached briefly."""

    name = "yahoo"

    def __init__(self, exchange: str = "NSE", downloader: Downloader | None = None, cache_seconds: float = 10.0,
                 monotonic: Callable[[], float] = time.monotonic) -> None:
        self.exchange = exchange
        self._download = downloader or _download
        self._cache_seconds = cache_seconds
        self._monotonic = monotonic
        self._cache: tuple[float, dict[str, float]] | None = None
        self.error: str | None = None
        self.last_ok: float | None = None

    def ltp(self, symbols: list[str]) -> dict[str, float]:
        now = self._monotonic()
        if self._cache and now - self._cache[0] < self._cache_seconds:
            cached = self._cache[1]
            if all(s in cached for s in symbols):
                return {s: cached[s] for s in symbols}
        tickers = {yahoo_ticker(s, self.exchange): s for s in symbols}
        try:
            df = self._download(tickers=list(tickers), period="1d", interval="1m", group_by="ticker",
                                multi_level_index=True)
        except Exception as e:
            self.error = f"Yahoo quotes failed: {e}"
            raise
        out: dict[str, float] = {}
        for ticker, sym in tickers.items():
            try:
                closes = df[ticker]["Close"].dropna()
            except (KeyError, TypeError):
                continue
            if len(closes):
                out[sym] = round(float(closes.iloc[-1]), 2)
        if symbols and not out:
            self.error = "Yahoo returned no prices (symbols wrong, or the service is down or rate-limiting)"
        else:
            self.error = None
            self.last_ok = now
        self._cache = (now, out)
        return out


class YahooFeed:
    """Quotes + candles + a status for the dashboard, in the shape the engine expects from a feed."""

    def __init__(self, exchange: str = "NSE", downloader: Downloader | None = None) -> None:
        self.quotes = YahooQuotes(exchange, downloader)
        self.data = YahooMarketData(exchange, downloader)

    def ensure(self) -> str | None:
        try:
            import yfinance  # noqa: F401
        except ImportError:
            return "the yfinance package is not installed (pip install 'thunderbot[yahoo]')"
        return None

    def status(self) -> dict[str, Any]:
        problem = self.ensure() or self.quotes.error
        return {"source": "yahoo", "ok": problem is None,
                "message": problem or "free Yahoo Finance data; prices can lag the exchange"}
