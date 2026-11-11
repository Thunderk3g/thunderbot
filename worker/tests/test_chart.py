from datetime import date, datetime, timedelta, timezone

import pytest

from thunderbot.chart import (
    ChartError,
    ChartQuotes,
    fetch_candles,
    fetch_daily,
    fetch_many,
    ticker,
)


def payload(days, closes, adj=None, price=None, at=None):
    stamps = [int(datetime(d.year, d.month, d.day, 3, 45, tzinfo=timezone.utc).timestamp()) for d in days]
    return {"chart": {"error": None, "result": [{
        "meta": {"regularMarketPrice": price, "regularMarketTime": at},
        "timestamp": stamps,
        "indicators": {"quote": [{"close": closes, "open": closes, "high": closes, "low": closes, "volume": [10] * len(closes)}],
                       **({"adjclose": [{"adjclose": adj}]} if adj else {})},
    }]}}


def test_ticker_suffix():
    assert ticker("NIFTYBEES") == "NIFTYBEES.NS" and ticker("^NSEI") == "^NSEI" and ticker("X.BO") == "X.BO"


def test_fetch_daily_prefers_adjusted_closes_and_skips_gaps():
    days = [date(2026, 11, 9), date(2026, 11, 10), date(2026, 11, 11)]
    seen = {}

    def get(path, params):
        seen.update(path=path, **params)
        return payload(days, [100.0, None, 102.0], adj=[50.0, None, 51.0])

    out = fetch_daily("NIFTYBEES", date(2026, 11, 1), date(2026, 11, 11), get)
    assert out == {days[0]: 50.0, days[2]: 51.0}
    assert seen["path"].endswith("/NIFTYBEES.NS") and seen["interval"] == "1d" and seen["period2"] > seen["period1"]


def test_fetch_many_reports_failures_instead_of_raising():
    def get(path, params):
        if "BAD" in path:
            raise ChartError("HTTP 404")
        return payload([date(2026, 11, 11)], [10.0])

    prices, errors = fetch_many(["GOOD", "BAD"], date(2026, 11, 1), date(2026, 11, 11), get)
    assert list(prices) == ["GOOD"] and "404" in errors["BAD"]
    with pytest.raises(ChartError):
        fetch_daily("X", date(2026, 11, 1), date(2026, 11, 2), lambda p, q: {"chart": {"result": None, "error": {"code": "Not Found"}}})


def test_quotes_drop_stale_prices_and_remember_trade_times():
    now = datetime(2026, 11, 11, 9, 45, tzinfo=timezone.utc)
    fresh, old = int((now - timedelta(minutes=2)).timestamp()), int((now - timedelta(days=3)).timestamp())

    def get(path, params):
        return payload([], [], price=286.54, at=old if "STALE" in path else fresh)

    q = ChartQuotes(get, now_fn=lambda: now)
    assert q.ltp(["NIFTYBEES", "STALE"]) == {"NIFTYBEES": 286.54}
    assert "STALE" in q.error and q.status()["ok"] is False and q.as_of["NIFTYBEES"].tzinfo is not None
    assert q.ltp(["NIFTYBEES"]) == {"NIFTYBEES": 286.54} and q.status()["ok"] is True


def test_fetch_candles_returns_ohlcv_in_order():
    days = [date(2026, 11, 10), date(2026, 11, 11)]
    bars = fetch_candles("RELIANCE", 5, datetime(2026, 11, 10, tzinfo=timezone.utc), datetime(2026, 11, 12, tzinfo=timezone.utc),
                         lambda p, q: payload(days, [1300.0, 1310.0]))
    assert [b[4] for b in bars] == [1300.0, 1310.0] and bars[0][5] == 10.0 and bars[0][0] < bars[1][0]
    with pytest.raises(ValueError):
        fetch_candles("RELIANCE", 7, datetime(2026, 11, 10, tzinfo=timezone.utc), datetime(2026, 11, 12, tzinfo=timezone.utc))
