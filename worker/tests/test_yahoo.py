from datetime import datetime, timedelta

import pytest

from thunderbot.clock import IST
from thunderbot.jobs import DataLoader, JobError
from thunderbot.yahoo import YahooFeed, YahooMarketData, YahooQuotes, frame_to_candles, yahoo_ticker

pd = pytest.importorskip("pandas")

NOW = datetime(2026, 10, 16, 15, 30, tzinfo=IST)


def bars_frame(start: datetime, n: int, price: float = 100.0):
    idx = pd.DatetimeIndex([start + timedelta(minutes=5 * i) for i in range(n)])
    return pd.DataFrame({"Open": price, "High": price + 1, "Low": price - 1, "Close": price + 0.5,
                         "Adj Close": price + 0.5, "Volume": 1000}, index=idx)


def test_ticker_mapping():
    assert yahoo_ticker("RELIANCE") == "RELIANCE.NS"
    assert yahoo_ticker("RELIANCE", "BSE") == "RELIANCE.BO"
    assert yahoo_ticker("^NSEI") == "^NSEI" and yahoo_ticker("TCS.NS") == "TCS.NS"


def test_frame_to_candles_skips_gaps_and_keeps_ist():
    df = bars_frame(datetime(2026, 10, 16, 9, 15, tzinfo=IST), 3)
    df.iloc[1, df.columns.get_loc("Close")] = float("nan")
    out = frame_to_candles(df)
    assert [c.ts.strftime("%H:%M") for c in out] == ["09:15", "09:25"]
    assert out[0].close == 100.5 and out[0].ts.utcoffset() == timedelta(hours=5, minutes=30)


def test_candles_clip_to_yahoo_window_and_request_right_ticker():
    calls = []

    def fake(**kw):
        calls.append(kw)
        return bars_frame(datetime(2026, 10, 16, 9, 15, tzinfo=IST), 4)

    md = YahooMarketData(downloader=fake, now_fn=lambda: NOW)
    out = md.candles("INFY", 5, NOW - timedelta(days=200), NOW)
    assert len(out) == 4
    assert calls[0]["tickers"] == "INFY.NS" and calls[0]["interval"] == "5m"
    assert calls[0]["start"] >= NOW - timedelta(days=60)  # 5-minute bars exist only for ~60 days
    with pytest.raises(ValueError):
        md.candles("INFY", 7, NOW - timedelta(days=1), NOW)


def test_candles_outside_window_return_nothing_without_a_request():
    md = YahooMarketData(downloader=lambda **kw: pytest.fail("no request expected"), now_fn=lambda: NOW)
    assert md.candles("INFY", 5, NOW - timedelta(days=300), NOW - timedelta(days=200)) == []


def test_quotes_take_last_close_per_symbol_and_cache():
    calls = []

    def fake(**kw):
        calls.append(kw)
        frames = {"RELIANCE.NS": bars_frame(NOW - timedelta(minutes=15), 3, 1200.0),
                  "INFY.NS": bars_frame(NOW - timedelta(minutes=15), 3, 1500.0)}
        return pd.concat(frames, axis=1)

    clock = [0.0]
    q = YahooQuotes(downloader=fake, cache_seconds=10, monotonic=lambda: clock[0])
    assert q.ltp(["RELIANCE", "INFY"]) == {"RELIANCE": 1200.5, "INFY": 1500.5}
    q.ltp(["INFY"])
    assert len(calls) == 1  # served from the cache
    clock[0] = 11
    q.ltp(["INFY"])
    assert len(calls) == 2 and q.error is None


def test_quotes_report_empty_answers():
    q = YahooQuotes(downloader=lambda **kw: pd.DataFrame())
    assert q.ltp(["NOPE"]) == {}
    assert "no prices" in q.error
    feed = YahooFeed()
    feed.quotes = q
    assert feed.status()["ok"] is False


def test_job_loader_yahoo_source(settings, monkeypatch):
    import thunderbot.yahoo as y

    monkeypatch.setattr(y, "_download", lambda **kw: bars_frame(datetime.now(IST).replace(hour=9, minute=15, second=0, microsecond=0) - timedelta(days=1), 10))
    monkeypatch.setattr("thunderbot.jobs.time.sleep", lambda s: None)
    today = datetime.now(IST).date()
    data, note = DataLoader(settings).load("yahoo", ["AAA"], today - timedelta(days=10), today)
    assert len(data["AAA"]) == 10 and "Yahoo" in note
    monkeypatch.setattr(y, "_download", lambda **kw: pd.DataFrame())
    with pytest.raises(JobError):
        DataLoader(settings).load("yahoo", ["AAA"], today - timedelta(days=10), today)
