"""Daily prices and last prices from Yahoo Finance's chart endpoint, with ``requests`` alone.

The daily strategies need one adjusted close per day for a handful of ETFs. Calling the chart
endpoint directly keeps the worker small enough for a serverless function (no pandas, numpy or
yfinance) and gives one request per symbol:

    GET https://query1.finance.yahoo.com/v8/finance/chart/NIFTYBEES.NS?period1=..&period2=..&interval=1d

Yahoo is an unofficial source. It needs a browser-like User-Agent, it can answer 429 when a
datacenter address asks too often, and its NSE data has gaps and bad ticks (see
``daily.clean_series``). Callers must treat every failure here as "no data today", never as a price.
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from typing import Any

log = logging.getLogger(__name__)

HOSTS = ("https://query1.finance.yahoo.com", "https://query2.finance.yahoo.com")
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/130.0 Safari/537.36")
IST_OFFSET = timedelta(hours=5, minutes=30)

Getter = Callable[[str, dict[str, Any]], dict[str, Any]]


class ChartError(RuntimeError):
    pass


def ticker(symbol: str) -> str:
    """NIFTYBEES -> NIFTYBEES.NS. Index symbols (^NSEI) and suffixed symbols are kept."""
    return symbol if symbol.startswith("^") or "." in symbol else f"{symbol}.NS"


def _http_get(path: str, params: dict[str, Any], attempts: int = 3, timeout: float = 20.0) -> dict[str, Any]:
    import requests

    last = "no attempt"
    for i in range(attempts):
        host = HOSTS[i % len(HOSTS)]
        try:
            r = requests.get(host + path, params=params, headers={"User-Agent": USER_AGENT}, timeout=timeout)
        except requests.RequestException as e:
            last = f"{type(e).__name__}: {e}"
        else:
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
            if r.status_code == 404:
                break  # unknown symbol: retrying will not help
        time.sleep(0.6 * (i + 1))
    raise ChartError(f"Yahoo chart request failed for {path.rsplit('/', 1)[-1]}: {last}")


def _result(payload: dict[str, Any]) -> dict[str, Any]:
    chart = payload.get("chart") or {}
    if chart.get("error") or not chart.get("result"):
        raise ChartError(f"Yahoo returned no data: {chart.get('error')}")
    return chart["result"][0]


def fetch_daily(symbol: str, start: date, end: date, get: Getter | None = None) -> dict[date, float]:
    """Adjusted daily closes (splits and dividends) for one symbol, keyed by the IST trading date."""
    p1 = int(datetime(start.year, start.month, start.day, tzinfo=timezone.utc).timestamp())
    p2 = int(datetime(end.year, end.month, end.day, tzinfo=timezone.utc).timestamp()) + 86_400
    res = _result((get or _http_get)(f"/v8/finance/chart/{ticker(symbol)}",
                                     {"period1": p1, "period2": p2, "interval": "1d", "events": "div,splits"}))
    stamps = res.get("timestamp") or []
    ind = res.get("indicators") or {}
    closes = ((ind.get("quote") or [{}])[0]).get("close") or []
    adj = ((ind.get("adjclose") or [{}])[0]).get("adjclose") or closes
    out: dict[date, float] = {}
    for ts, c, a in zip(stamps, closes, adj, strict=False):
        px = a if a is not None else c
        if px is None or px <= 0:
            continue
        d = (datetime.fromtimestamp(ts, timezone.utc) + IST_OFFSET).date()
        if start <= d <= end:
            out[d] = float(px)
    return out


def fetch_many(symbols: list[str], start: date, end: date, get: Getter | None = None,
               workers: int = 6) -> tuple[dict[str, dict[date, float]], dict[str, str]]:
    """Daily closes for many symbols. Returns (prices, errors); a failed symbol is reported, not raised."""
    prices: dict[str, dict[date, float]] = {}
    errors: dict[str, str] = {}

    def one(sym: str) -> tuple[str, dict[date, float] | None, str | None]:
        try:
            return sym, fetch_daily(sym, start, end, get), None
        except Exception as e:  # one bad symbol must not sink the rest
            return sym, None, f"{type(e).__name__}: {e}"

    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(symbols) or 1))) as pool:
        for sym, series, err in pool.map(one, symbols):
            if series:
                prices[sym] = series
            else:
                errors[sym] = err or "no rows"
    return prices, errors


INTERVALS = {1: "1m", 2: "2m", 5: "5m", 15: "15m", 30: "30m", 60: "60m", 1440: "1d"}


def fetch_candles(symbol: str, interval_minutes: int, start: datetime, end: datetime,
                  get: Getter | None = None) -> list[tuple[datetime, float, float, float, float, float]]:
    """Intraday or daily bars as (start time in UTC, open, high, low, close, volume), oldest first.
    Yahoo keeps 1-minute bars for 7 days, 2- to 30-minute bars for 60 days and hourly bars for 2 years."""
    if interval_minutes not in INTERVALS:
        raise ValueError(f"Yahoo has no {interval_minutes}-minute bars; choose from {sorted(INTERVALS)}")
    res = _result((get or _http_get)(f"/v8/finance/chart/{ticker(symbol)}", {
        "period1": int(start.timestamp()), "period2": int(end.timestamp()), "interval": INTERVALS[interval_minutes]}))
    q = ((res.get("indicators") or {}).get("quote") or [{}])[0]
    out = []
    for i, ts in enumerate(res.get("timestamp") or []):
        o, h, low, c = (q.get(k, [None])[i] if i < len(q.get(k) or []) else None for k in ("open", "high", "low", "close"))
        if None in (o, h, low, c):
            continue
        vol = (q.get("volume") or [0])[i] if i < len(q.get("volume") or []) else 0
        out.append((datetime.fromtimestamp(ts, timezone.utc), float(o), float(h), float(low), float(c), float(vol or 0)))
    return out


def last_price(symbol: str, get: Getter | None = None) -> tuple[float, datetime] | None:
    """The latest traded price and its exchange time, from the chart metadata."""
    res = _result((get or _http_get)(f"/v8/finance/chart/{ticker(symbol)}", {"range": "1d", "interval": "1d"}))
    meta = res.get("meta") or {}
    px, at = meta.get("regularMarketPrice"), meta.get("regularMarketTime")
    if not px or px <= 0 or not at:
        return None
    return float(px), datetime.fromtimestamp(at, timezone.utc)


class ChartQuotes:
    """Last prices for the invest runner (the ``quotes.ltp`` contract), without pandas or yfinance.

    ``max_age`` guards against a stale quote being used as today's price: a symbol whose last trade is
    older than that is left out, and the caller decides what to do without it.
    """

    name = "yahoo"

    def __init__(self, get: Getter | None = None, max_age: timedelta | None = timedelta(hours=30),
                 now_fn: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self._get = get
        self.max_age = max_age
        self._now = now_fn
        self.error: str | None = None
        self.as_of: dict[str, datetime] = {}

    def ltp(self, symbols: list[str]) -> dict[str, float]:
        out: dict[str, float] = {}
        problems: list[str] = []

        def one(sym: str) -> tuple[str, tuple[float, datetime] | None, str | None]:
            try:
                return sym, last_price(sym, self._get), None
            except Exception as e:
                return sym, None, str(e)

        with ThreadPoolExecutor(max_workers=max(1, min(6, len(symbols) or 1))) as pool:
            for sym, got, err in pool.map(one, symbols):
                if got is None:
                    problems.append(f"{sym}: {err or 'no price'}")
                    continue
                px, at = got
                if self.max_age is not None and self._now() - at > self.max_age:
                    problems.append(f"{sym}: last trade {at:%Y-%m-%d %H:%M} UTC is stale")
                    continue
                out[sym] = round(px, 2)
                self.as_of[sym] = at
        self.error = "; ".join(problems) if problems else None
        return out

    def status(self) -> dict[str, Any]:
        return {"source": "yahoo", "ok": self.error is None,
                "message": self.error or "free Yahoo Finance data; prices can lag the exchange"}
