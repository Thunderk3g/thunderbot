from datetime import date, datetime, time, timedelta

from thunderbot.clock import IST, MarketClock
from thunderbot.daily import BENCHMARK
from thunderbot.invest import STATE_KEY, InvestRunner
from thunderbot.store import CompositeStore, SQLiteStore


def history_factory(index_trend_up=True):
    def history(symbols, start, end):
        days, d = [], start
        while d <= end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        f = (lambda i: 100 * 1.001 ** i) if index_trend_up else (lambda i: 100 * 0.999 ** i)
        return {s: {d: f(i) for i, d in enumerate(days)} for s in symbols}
    return history


class Quotes:
    def __init__(self, px):
        self.px = px

    def ltp(self, symbols):
        return {s: self.px for s in symbols}


def make(tmp_path, now, up=True, price=200.0):
    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    clock = [now]
    r = InvestRunner(store, Quotes(price), MarketClock(), capital=100_000, history=history_factory(up),
                     now_fn=lambda: clock[0], sleep_fn=lambda s: None, run_at=time(15, 10))
    return store, r, clock


def test_waits_for_start_then_buys_etf_before_close(tmp_path):
    store, r, clock = make(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST))  # a Wednesday
    r.tick()
    assert store.get_control().get(STATE_KEY) is None  # not started: no trades
    hb = store.get_control()["heartbeat"]
    assert hb["style"] == "invest" and hb["trading"] == "stopped"

    store.set_control("trading_enabled", True)
    r.tick()
    st = store.get_control()[STATE_KEY]
    assert BENCHMARK in st["lots"] and st["lots"][BENCHMARK]["qty"] == 498  # whole shares of a 200-rupee ETF
    assert 0 < st["cash"] < 1_000
    assert store.get_control()["heartbeat"]["portfolio"]["invested_pct"] > 99
    r.tick()  # same day again: no second run
    assert len(store.local.rows("orders")) == 1


def test_downtrend_goes_to_cash_and_stop_sells_everything(tmp_path):
    store, r, clock = make(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST))
    store.set_control("trading_enabled", True)
    r.tick()
    assert store.get_control()[STATE_KEY]["lots"]
    store.set_control("trading_enabled", False)
    clock[0] = datetime(2026, 10, 22, 10, 0, tzinfo=IST)
    r.tick()
    st = store.get_control()[STATE_KEY]
    assert st["lots"] == {} and st["cash"] > 99_000
    assert store.local.rows("trades")[0]["exit_reason"] == "stopped"


def test_below_average_stays_in_cash(tmp_path):
    store, r, clock = make(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST), up=False, price=50.0)
    store.set_control("trading_enabled", True)
    r.tick()
    st = store.get_control()[STATE_KEY]
    assert st["lots"] == {} and st["last_run"] == "2026-10-21"
    assert store.get_control()["heartbeat"]["portfolio"]["filter"]["above"] is False


def test_no_run_on_weekend_or_before_decision_time(tmp_path):
    store, r, clock = make(tmp_path, datetime(2026, 10, 24, 15, 12, tzinfo=IST))  # Saturday
    store.set_control("trading_enabled", True)
    r.tick()
    assert store.get_control().get(STATE_KEY) is None
    clock[0] = datetime(2026, 10, 26, 14, 0, tzinfo=IST)  # Monday, before 15:10
    r.tick()
    assert store.get_control().get(STATE_KEY) is None
    assert date.fromisoformat(store.get_control()["heartbeat"]["portfolio"]["next_rebalance"]) >= date(2026, 10, 26)
