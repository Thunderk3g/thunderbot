"""Market data sources: Groww historical API, local CSV files, and synthetic data for demos/tests."""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict
from collections.abc import Iterable
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Protocol

from .clock import IST, MARKET_CLOSE, MARKET_OPEN, to_ist
from .models import Candle

CANDLE_INTERVALS = {
    1: "1minute", 2: "2minute", 3: "3minute", 5: "5minute", 10: "10minute",
    15: "15minute", 30: "30minute", 60: "1hour", 240: "4hour", 1440: "1day",
}


def max_window_days(interval_minutes: int) -> int:
    """Groww's per-request history window for a candle interval."""
    if interval_minutes <= 5:
        return 30
    if interval_minutes <= 30:
        return 90
    return 180


class MarketData(Protocol):
    def candles(self, symbol: str, interval_minutes: int, start: datetime, end: datetime) -> list[Candle]: ...


def _parse_ts(value: Any) -> datetime:
    if isinstance(value, (int, float)):
        v = float(value)
        if v > 1e12:  # epoch milliseconds
            v /= 1000.0
        return datetime.fromtimestamp(v, tz=IST)
    s = str(value).strip()
    if s.isdigit():
        return _parse_ts(int(s))
    s = s.replace("Z", "+00:00")
    return to_ist(datetime.fromisoformat(s))


def parse_groww_candles(resp: dict[str, Any] | None) -> list[Candle]:
    """Parse ``get_historical_candles`` output: ``{"candles": [[ts, o, h, l, c, v, (oi)], ...]}``."""
    rows = (resp or {}).get("candles") or []
    out = []
    for row in rows:
        if isinstance(row, dict):
            ts, o, h, l, c, v = (row.get(k) for k in ("timestamp", "open", "high", "low", "close", "volume"))
        else:
            ts, o, h, l, c, v = row[:6]
        if None in (ts, o, h, l, c):
            continue
        out.append(Candle(_parse_ts(ts), float(o), float(h), float(l), float(c), float(v or 0)))
    out.sort(key=lambda b: b.ts)
    return out


class GrowwMarketData:
    """Historical candles from the Groww Backtesting API (needs a paid Trade API plan)."""

    def __init__(self, client: Any, exchange: str = "NSE", segment: str = "CASH") -> None:
        self.client = client
        self.exchange = exchange
        self.segment = segment

    def candles(self, symbol: str, interval_minutes: int, start: datetime, end: datetime) -> list[Candle]:
        if interval_minutes not in CANDLE_INTERVALS:
            raise ValueError(f"unsupported interval {interval_minutes}m; choose from {sorted(CANDLE_INTERVALS)}")
        window = timedelta(days=max_window_days(interval_minutes))
        out: dict[datetime, Candle] = {}
        cur = to_ist(start)
        end = to_ist(end)
        while cur < end:
            chunk_end = min(cur + window, end)
            resp = self.client.get_historical_candles(
                exchange=self.exchange,
                segment=self.segment,
                groww_symbol=f"{self.exchange}-{symbol}",
                start_time=cur.strftime("%Y-%m-%d %H:%M:%S"),
                end_time=chunk_end.strftime("%Y-%m-%d %H:%M:%S"),
                candle_interval=CANDLE_INTERVALS[interval_minutes],
            )
            for c in parse_groww_candles(resp):
                out[c.ts] = c
            cur = chunk_end
        return [out[k] for k in sorted(out)]


class CSVMarketData:
    """Reads ``<dir>/<SYMBOL>.csv`` with columns ts,open,high,low,close,volume (ts ISO-8601, IST)."""

    def __init__(self, directory: str | Path) -> None:
        self.dir = Path(directory)
        self._cache: dict[str, list[Candle]] = {}

    def _load(self, symbol: str) -> list[Candle]:
        if symbol not in self._cache:
            path = self.dir / f"{symbol}.csv"
            if not path.exists():
                raise FileNotFoundError(f"no data file for {symbol}: {path}")
            with path.open() as f:
                rows = [
                    Candle(_parse_ts(r["ts"]), float(r["open"]), float(r["high"]), float(r["low"]),
                           float(r["close"]), float(r.get("volume") or 0))
                    for r in csv.DictReader(f)
                ]
            rows.sort(key=lambda b: b.ts)
            self._cache[symbol] = rows
        return self._cache[symbol]

    def candles(self, symbol: str, interval_minutes: int, start: datetime, end: datetime) -> list[Candle]:
        start, end = to_ist(start), to_ist(end)
        return [c for c in self._load(symbol) if start <= c.ts < end]

    def symbols(self) -> list[str]:
        return sorted(p.stem for p in self.dir.glob("*.csv"))


def write_csv(path: str | Path, candles: Iterable[Candle]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["ts", "open", "high", "low", "close", "volume"])
        for c in candles:
            w.writerow([c.ts.isoformat(), f"{c.open:.2f}", f"{c.high:.2f}", f"{c.low:.2f}", f"{c.close:.2f}", int(c.volume)])


def group_by_day(candles: Iterable[Candle]) -> dict[date, list[Candle]]:
    days: dict[date, list[Candle]] = defaultdict(list)
    for c in candles:
        days[c.ts.date()].append(c)
    return dict(sorted(days.items()))


def synthetic_session(
    d: date,
    start_price: float,
    interval_minutes: int = 5,
    daily_vol: float = 0.015,
    drift: float = 0.0,
    rng: random.Random | None = None,
) -> list[Candle]:
    """A random-walk intraday session with a U-shaped volume profile. For demos and tests only."""
    rng = rng or random.Random()
    open_dt = datetime.combine(d, MARKET_OPEN, tzinfo=IST)
    close_dt = datetime.combine(d, MARKET_CLOSE, tzinfo=IST)
    n = int((close_dt - open_dt).total_seconds() // 60 // interval_minutes)
    step_vol = daily_vol / math.sqrt(n)
    price = start_price
    out = []
    for i in range(n):
        o = price
        ret = rng.gauss(drift / n, step_vol)
        c = max(o * (1 + ret), 0.01)
        wiggle = abs(rng.gauss(0, step_vol / 2))
        h = max(o, c) * (1 + wiggle)
        l = min(o, c) * (1 - wiggle)
        x = i / max(n - 1, 1)
        vol_profile = 1.0 + 2.5 * (x - 0.5) ** 2 * 4  # U-shape
        v = max(rng.gauss(50_000 * vol_profile, 10_000), 1_000)
        out.append(Candle(open_dt + timedelta(minutes=i * interval_minutes), round(o, 2), round(h, 2), round(l, 2), round(c, 2), round(v)))
        price = c
    return out


def synthetic_history(
    symbols: list[str], start: date, days: int, interval_minutes: int = 5, seed: int = 7
) -> dict[str, list[Candle]]:
    rng = random.Random(seed)
    out: dict[str, list[Candle]] = {}
    for sym in symbols:
        price = rng.uniform(300, 3000)
        bars: list[Candle] = []
        d = start
        produced = 0
        while produced < days:
            if d.weekday() < 5:
                gap = rng.gauss(0, 0.006)
                session = synthetic_session(d, price * (1 + gap), interval_minutes, rng=rng, drift=rng.gauss(0, 0.01))
                bars.extend(session)
                price = session[-1].close
                produced += 1
            d += timedelta(days=1)
        out[sym] = bars
    return out


def session_bounds(d: date) -> tuple[datetime, datetime]:
    return datetime.combine(d, MARKET_OPEN, tzinfo=IST), datetime.combine(d, time(15, 30), tzinfo=IST)
