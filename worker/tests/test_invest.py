from datetime import date, datetime, time, timedelta

from thunderbot.clock import IST, MarketClock
from thunderbot.daily import BENCHMARK
from thunderbot.invest import STATE_KEY, InvestRunner
from thunderbot.store import CompositeStore, SQLiteStore


def history_factory(index_trend_up=True, last=200.0):
    """Prices that trend up (or down) and end at ``last``, so the live quote is a normal next step."""
    def history(symbols, start, end):
        days, d = [], start
        while d <= end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        step = 1.001 if index_trend_up else 0.999
        n = len(days)
        return {s: {d: last * step ** (i - n + 1) for i, d in enumerate(days)} for s in symbols}
    return history


class Quotes:
    def __init__(self, px):
        self.px = px

    def ltp(self, symbols):
        return {s: self.px for s in symbols}


def make(tmp_path, now, up=True, price=200.0, **kw):
    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    clock = [now]
    r = InvestRunner(store, Quotes(price), MarketClock(), capital=100_000, history=history_factory(up, price),
                     now_fn=lambda: clock[0], sleep_fn=lambda s: None, run_at=time(15, 10), strategy="index_trend",
                     params={"liquid": 0}, **kw)
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


# New behaviour: the steady mix, bad-price guard, late and missed runs, the reviewer, the run lock.

def make_mix(tmp_path, now, price=200.0, **kw):
    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    clock = [now]
    quotes = kw.pop("quotes", None) or Quotes(price)
    r = InvestRunner(store, quotes, MarketClock(), capital=300_000, history=history_factory(True, price),
                     now_fn=lambda: clock[0], sleep_fn=lambda s: None, run_at=time(15, 10), **kw)
    store.set_control("trading_enabled", True)
    return store, r, clock


def test_default_strategy_buys_the_three_etf_mix_and_records_the_plan(tmp_path):
    store, r, _ = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST))
    out = r.tick()
    st = store.get_control()[STATE_KEY]
    assert set(st["lots"]) == {"NIFTYBEES", "JUNIORBEES", "GOLDBEES"} and out["did"].startswith("rebalanced")
    plan = st["last_plan"]
    assert {o["symbol"] for o in plan["orders"]} == set(st["lots"]) and all(o["side"] == "BUY" for o in plan["orders"])
    assert plan["target"]["GOLDBEES"] == 0.33 and plan["late"] is False
    hb = store.get_control()["heartbeat"]
    assert hb["portfolio"]["last_plan"]["orders"] and hb["scheduler"] == "worker" and hb["next_tick_by"]


def test_a_price_jump_postpones_the_rebalance_until_prices_are_sane(tmp_path):
    class Jumpy(Quotes):
        def ltp(self, symbols):
            return {s: (20.0 if s == "GOLDBEES" else self.px) for s in symbols}  # an unadjusted 1:10 split

    store, r, clock = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST), quotes=Jumpy(200.0))
    assert r.tick()["did"] == "postponed: bad prices"
    st = store.get_control()[STATE_KEY]
    assert st["lots"] == {} and st["pending"] is True
    assert any(e["kind"] == "invest_blocked" for e in store.local.rows("events"))
    r.quotes = Quotes(200.0)
    clock[0] = datetime(2026, 10, 22, 15, 12, tzinfo=IST)
    assert r.tick()["did"].startswith("rebalanced")  # pending: decided again the next session, not at month-end


def test_a_late_paper_run_uses_closing_prices_and_says_so(tmp_path):
    store, r, _ = make_mix(tmp_path, datetime(2026, 10, 21, 16, 5, tzinfo=IST))  # the scheduler fired after the close
    assert r.tick()["did"].startswith("rebalanced")
    assert store.get_control()[STATE_KEY]["last_plan"]["late"] is True


def test_a_live_run_after_the_cutoff_does_not_trade_and_alerts_once(tmp_path):
    sent = []
    store, r, clock = make_mix(tmp_path, datetime(2026, 10, 21, 15, 40, tzinfo=IST), broker=object(), mode="live",
                               notify=sent.append)
    assert r.tick()["did"].startswith("missed")
    r.tick()
    st = store.get_control()[STATE_KEY]
    assert st["lots"] == {} and st["missed"] == "2026-10-21" and st["pending"] is True
    assert len(sent) == 1 and "too late" in sent[0]


def test_reviewer_can_postpone_twice_then_the_rule_runs(tmp_path):
    from thunderbot.llm.rebalance import RebalanceVerdict

    class Postponer:
        calls = 0

        def review(self, ctx):
            Postponer.calls += 1
            assert ctx.orders and ctx.facts["NIFTYBEES"]["price"] == 200.0
            return RebalanceVerdict(False, 0.8, "GOLDBEES price looks stale.", ["stale_price"], model="test")

    store, r, clock = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST), reviewer=Postponer())
    assert r.tick()["did"] == "postponed by the reviewer"
    clock[0] = datetime(2026, 10, 22, 15, 12, tzinfo=IST)
    assert r.tick()["did"] == "postponed by the reviewer"
    clock[0] = datetime(2026, 10, 23, 15, 12, tzinfo=IST)
    assert r.tick()["did"].startswith("rebalanced")  # two postponements is the limit
    assert Postponer.calls == 3 and len(store.local.rows("llm_decisions")) == 3
    assert store.get_control()[STATE_KEY]["lots"]


def test_a_broken_reviewer_never_blocks_the_rule(tmp_path):
    class Broken:
        def review(self, ctx):
            raise RuntimeError("model unavailable")

    store, r, _ = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST), reviewer=Broken())
    assert r.tick()["did"].startswith("rebalanced")


def test_only_one_of_two_simultaneous_runs_trades(tmp_path):
    store, r, _ = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST))
    held = set()

    def claim(kind, day):
        if (kind, day) in held:
            return None
        held.add((kind, day))
        return "claim-1"

    store.claim, store.finish, store.release = claim, lambda *a, **k: None, lambda cid: held.clear()
    held.add(("invest", "2026-10-21"))  # another invocation got there first
    assert r.tick()["did"] == "another run holds today's lock"
    assert store.get_control().get(STATE_KEY) is None
    held.clear()
    assert r.tick()["did"].startswith("rebalanced")


def test_an_unlisted_holiday_is_detected_from_the_last_trade_time(tmp_path):
    class Closed(Quotes):
        as_of = {"NIFTYBEES": datetime(2026, 10, 20, 15, 29, tzinfo=IST)}

    store, r, _ = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST), quotes=Closed(200.0))
    assert r.tick()["did"] == "skipped: market looks closed"
    assert store.get_control()[STATE_KEY]["lots"] == {}


def test_holdings_are_marked_to_market_for_a_worker_that_was_just_woken(tmp_path):
    store, r, clock = make_mix(tmp_path, datetime(2026, 10, 21, 15, 12, tzinfo=IST))
    r.tick()
    assert store.get_control()[STATE_KEY]["marks"]["px"]["NIFTYBEES"] == 200.0

    calls = []

    class Counting(Quotes):
        def ltp(self, symbols):
            calls.append(sorted(symbols))
            return super().ltp(symbols)

    def woken(at, price):
        """A fresh process, as a serverless function is: nothing in memory but what the store holds."""
        clock[0] = at
        fresh = InvestRunner(store, Counting(price), MarketClock(), capital=300_000, history=history_factory(True, price),
                             now_fn=lambda: clock[0], sleep_fn=lambda s: None, run_at=time(15, 10))
        fresh.tick()
        return store.get_control()["heartbeat"]["portfolio"]

    p = woken(datetime(2026, 10, 21, 15, 20, tzinfo=IST), 210.0)  # 8 minutes later: marks are recent, no request
    assert calls == [] and p["holdings"][0]["ltp"] == 200.0
    p = woken(datetime(2026, 10, 22, 10, 0, tzinfo=IST), 210.0)  # next morning, market open: refreshed
    assert len(calls) == 1 and p["holdings"][0]["ltp"] == 210.0 and p["value"] > 300_000
    woken(datetime(2026, 10, 22, 10, 5, tzinfo=IST), 220.0)  # within 15 minutes: not again
    assert len(calls) == 1
    woken(datetime(2026, 10, 22, 17, 0, tzinfo=IST), 220.0)  # the day's late check fetches prices once ...
    woken(datetime(2026, 10, 22, 21, 0, tzinfo=IST), 225.0)  # ... and nothing more that evening
    assert len(calls) == 2 and store.get_control()[STATE_KEY]["marks"]["px"]["GOLDBEES"] == 220.0
    woken(datetime(2026, 10, 24, 12, 0, tzinfo=IST), 230.0)  # Saturday: one refresh for Friday's close ...
    woken(datetime(2026, 10, 25, 12, 0, tzinfo=IST), 235.0)  # ... and none on Sunday
    assert len(calls) == 3 and store.get_control()[STATE_KEY]["marks"]["px"]["GOLDBEES"] == 230.0
