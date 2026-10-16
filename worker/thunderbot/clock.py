"""NSE market calendar and session timing, all in IST."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)
# Groww documents MIS auto square-off at 3:20 PM (third-party pages say 3:10-3:15).
# We flatten at 3:05 by default so the discrepancy never matters.
DEFAULT_FLATTEN_AT = time(15, 5)
# Groww access tokens expire daily at 6:00 AM IST.
TOKEN_EXPIRY = time(6, 0)


def parse_hhmm(value: str) -> time:
    hh, mm = value.strip().split(":")
    return time(int(hh), int(mm))


def now_ist() -> datetime:
    return datetime.now(IST)


def to_ist(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        return ts.replace(tzinfo=IST)
    return ts.astimezone(IST)


def load_holidays(path: str | Path | None) -> set[date]:
    """Load exchange holidays from a file with one ISO date per line (``#`` comments allowed)."""
    if not path:
        return set()
    p = Path(path)
    if not p.exists():
        return set()
    out: set[date] = set()
    for line in p.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(date.fromisoformat(line))
    return out


@dataclass
class MarketClock:
    entry_start: time = time(9, 30)
    entry_end: time = time(14, 30)
    flatten_at: time = DEFAULT_FLATTEN_AT
    holidays: set[date] = field(default_factory=set)

    def is_trading_day(self, d: date) -> bool:
        return d.weekday() < 5 and d not in self.holidays

    def is_market_open(self, ts: datetime) -> bool:
        ts = to_ist(ts)
        return self.is_trading_day(ts.date()) and MARKET_OPEN <= ts.time() < MARKET_CLOSE

    def in_entry_window(self, ts: datetime) -> bool:
        ts = to_ist(ts)
        return self.is_market_open(ts) and self.entry_start <= ts.time() < self.entry_end

    def should_flatten(self, ts: datetime) -> bool:
        ts = to_ist(ts)
        return self.is_trading_day(ts.date()) and ts.time() >= self.flatten_at

    def session_open(self, d: date) -> datetime:
        return datetime.combine(d, MARKET_OPEN, tzinfo=IST)

    def last_completed_bar_start(self, ts: datetime, interval_minutes: int) -> datetime | None:
        """Start time of the most recent bar that has fully closed at ``ts``."""
        ts = to_ist(ts)
        open_dt = self.session_open(ts.date())
        if ts < open_dt + timedelta(minutes=interval_minutes):
            return None
        elapsed = int((ts - open_dt).total_seconds() // 60)
        bars_done = elapsed // interval_minutes
        return open_dt + timedelta(minutes=(bars_done - 1) * interval_minutes)


def token_is_stale(issued_at: datetime, now: datetime) -> bool:
    """True if a Groww token issued at ``issued_at`` has passed a 6:00 AM IST expiry."""
    issued_at, now = to_ist(issued_at), to_ist(now)
    expiry = datetime.combine(issued_at.date(), TOKEN_EXPIRY, tzinfo=IST)
    if issued_at >= expiry:
        expiry += timedelta(days=1)
    return now >= expiry
