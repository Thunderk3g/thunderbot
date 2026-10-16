from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from thunderbot.clock import IST, MarketClock
from thunderbot.config import Settings
from thunderbot.models import Candle

DAY = date(2026, 10, 15)  # a Thursday


def ts(hh: int, mm: int, d: date = DAY) -> datetime:
    return datetime(d.year, d.month, d.day, hh, mm, tzinfo=IST)


def bar(t: datetime, o: float, h: float, l: float, c: float, v: float = 1000) -> Candle:
    return Candle(t, o, h, l, c, v)


def flat_session(d: date = DAY, price: float = 100.0, n: int = 75, vol: float = 1000) -> list[Candle]:
    start = ts(9, 15, d)
    return [bar(start + timedelta(minutes=5 * i), price, price + 0.1, price - 0.1, price, vol) for i in range(n)]


def breakout_session(d: date = DAY) -> list[Candle]:
    """Opening range 99-101 for 3 bars, quiet bars, then a high-volume upside breakout at 9:45."""
    t0 = ts(9, 15, d)
    bars = [
        bar(t0, 100, 101, 99, 100.5, 3000),
        bar(t0 + timedelta(minutes=5), 100.5, 100.8, 99.5, 100.2, 2500),
        bar(t0 + timedelta(minutes=10), 100.2, 100.9, 99.8, 100.4, 2000),
        bar(t0 + timedelta(minutes=15), 100.4, 100.9, 100.1, 100.6, 1000),
        bar(t0 + timedelta(minutes=20), 100.6, 100.95, 100.3, 100.8, 1000),
        bar(t0 + timedelta(minutes=25), 100.8, 101.6, 100.7, 101.5, 4000),  # breakout bar 9:40
    ]
    return bars


@pytest.fixture
def settings(tmp_path) -> Settings:
    s = Settings(
        capital=100_000,
        risk_per_trade_pct=1.0,
        max_daily_loss_pct=2.0,
        max_open_positions=2,
        max_trades_per_day=4,
        max_leverage=1.0,
        max_position_notional_pct=100.0,
        symbols=["AAA", "BBB"],
        data_dir=str(tmp_path / "var"),
        slippage_bps=0.0,
        fill_timeout_seconds=2,
    )
    s.apply_hard_limits()
    return s


@pytest.fixture
def clock() -> MarketClock:
    return MarketClock()
