from datetime import date, timedelta

import pytest

from thunderbot.daily import (
    BENCHMARK,
    INDEX,
    CapitalGainsTax,
    DeliveryCosts,
    IndexTrend,
    MomentumRotation,
    backtest,
    clean_series,
    financial_year,
    momentum_scores,
)


def trading_days(start: date, n: int) -> list[date]:
    out, d = [], start
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d)
        d += timedelta(days=1)
    return out


DAYS = trading_days(date(2018, 1, 1), 900)


def series(f) -> dict[date, float]:
    return {d: f(i) for i, d in enumerate(DAYS)}


def test_delivery_costs_match_groww_schedule():
    c = DeliveryCosts(slippage_pct=0)
    # Rs 1 lakh stock round trip ~ Rs 293 in the cost research (excl. slippage).
    rt = c.order(100_000, True, "RELIANCE") + c.order(100_000, False, "RELIANCE")
    assert rt == pytest.approx(293.3, abs=1.0)
    # ETFs pay STT only on the sell side, at 0.001%.
    assert c.order(100_000, True, "NIFTYBEES") < c.order(100_000, True, "RELIANCE") - 99
    assert DeliveryCosts.brokerage(1_000) == 1.0 * 5 and DeliveryCosts.brokerage(100) == 2.5
    assert DeliveryCosts.brokerage(50_000) == 20.0


def test_capital_gains_tax_rules():
    t = CapitalGainsTax(cess=0)
    assert t.year_tax(10_000, 0) == 2_000
    assert t.year_tax(0, 125_000) == 0 and t.year_tax(0, 225_000) == 12_500
    assert t.year_tax(-10_000, 135_000) == 0  # short-term loss offsets long-term gain
    assert financial_year(date(2025, 3, 31)) == 2024 and financial_year(date(2025, 4, 1)) == 2025


def test_clean_series_drops_spikes_and_back_adjusts_splits():
    s = series(lambda i: 100.0 + i * 0.1)
    bad = dict(s)
    bad[DAYS[50]] = 10.0  # one-day bad tick
    bad[DAYS[51]] = 10.0
    for d in DAYS[300:]:
        bad[d] = s[d] / 10  # unadjusted 1:10 split
    fixed, notes = clean_series(bad)
    assert DAYS[50] not in fixed and DAYS[51] not in fixed
    assert fixed[DAYS[299]] == pytest.approx(s[DAYS[299]] / 10)
    assert any("back-adjusted" in n for n in notes)


def test_momentum_scores_rank_the_trend():
    hist = {"UP": [100 * 1.001 ** i for i in range(300)], "FLAT": [100 + (i % 2) for i in range(300)],
            "DOWN": [100 * 0.999 ** i for i in range(300)]}
    s = momentum_scores(hist)
    assert s["UP"] > s["FLAT"] > s["DOWN"]


def test_index_trend_exits_below_average_and_trades_next_day():
    up_then_down = lambda i: 100 * 1.002 ** i if i < 500 else 100 * 1.002 ** 500 * 0.995 ** (i - 500)  # noqa: E731
    px = {INDEX: series(up_then_down), BENCHMARK: series(up_then_down)}
    r = backtest(IndexTrend(sma_days=50, buffer_pct=0, rebalance="weekly"), px, DAYS[60], DAYS[-1],
                 costs=DeliveryCosts(slippage_pct=0))
    m = r.metrics()
    assert 0 < m["time_invested_pct"] < 100
    assert m["max_drawdown_pct"] > m["benchmark"]["max_drawdown_pct"]  # it sidestepped most of the fall
    assert r.trades >= 2


def test_momentum_rotation_holds_the_strongest_and_pays_tax():
    px = {INDEX: series(lambda i: 100 * 1.0005 ** i), BENCHMARK: series(lambda i: 100 * 1.0005 ** i)}
    for k in range(12):
        px[f"S{k}"] = series(lambda i, k=k: 100 * (1 + 0.0002 * k) ** i)
    syms = [f"S{k}" for k in range(12)]
    strat = MomentumRotation(symbols=syms, top_n=3, keep_rank=3, trend_filter=False, rank_every="monthly")
    r = backtest(strat, px, DAYS[300], DAYS[-1], tax=CapitalGainsTax())
    assert r.metrics()["cagr_pct"] > 0 and r.trades >= 3
    assert r.metrics()["rebalances"] > 10
    # Quarterly ranking keeps the holdings between ranking months, so it decides far less often.
    q = backtest(MomentumRotation(symbols=syms, top_n=3, keep_rank=3, trend_filter=False, rank_every="quarterly"),
                 px, DAYS[300], DAYS[-1])
    assert 0 < q.metrics()["rebalances"] < r.metrics()["rebalances"]


# Asset classes, the liquid ETF, ETF rotation and the no-timing yardstick.

def test_costs_and_tax_depend_on_the_kind_of_etf():
    from thunderbot.daily import asset_class, tax_bucket

    c = DeliveryCosts(slippage_pct=0, liquid_slippage_pct=0)
    assert asset_class("GOLDBEES") == "commodity_etf" and asset_class("LIQUIDCASE") == "debt_etf"
    # Gold and liquid ETFs pay no STT; an equity ETF pays 0.001% on the sell side only.
    assert c.order(1_000_000, False, "NIFTYBEES") - c.order(1_000_000, False, "GOLDBEES") == pytest.approx(10.0)
    assert c.order(1_000_000, True, "NIFTYBEES") == pytest.approx(c.order(1_000_000, True, "GOLDBEES"))
    assert tax_bucket("NIFTYBEES", 200) == "stcg" and tax_bucket("NIFTYBEES", 400) == "ltcg"
    assert tax_bucket("GOLDBEES", 200) == "slab" and tax_bucket("GOLDBEES", 400) == "other_ltcg"
    assert tax_bucket("LIQUIDCASE", 900) == "slab"


def test_tax_by_bucket_with_loss_set_off_and_carry_forward():
    t = CapitalGainsTax(cess=0, slab_rate=0.30)
    assert t.year_tax(0, 0, other_ltcg=100_000) == 12_500  # gold long-term: no Rs 1.25 lakh exemption
    assert t.year_tax(0, 0, slab=100_000) == 30_000  # liquid ETF gain at the slab rate
    # A short-term equity loss is used against the highest-taxed gain first.
    assert t.year_tax(-40_000, 0, slab=100_000) == 18_000
    carry: dict[str, float] = {}
    assert t.year_tax(-50_000, 0, carry=carry) == 0 and carry["st"] == 50_000
    assert t.year_tax(60_000, 0, carry=carry) == 2_000 and carry["st"] == 0
    # A long-term loss cannot reduce a short-term gain.
    assert t.year_tax(10_000, -30_000) == 2_000


def test_liquid_series_compounds_each_years_rate_less_costs():
    from thunderbot.daily import liquid_series

    days = [date(2022, 12, 30), date(2023, 12, 29), date(2024, 12, 31)]
    px = liquid_series(days, yields={2022: 5.0, 2023: 7.0, 2024: 6.0}, cost_pct=0.0)
    assert px[days[1]] / px[days[0]] == pytest.approx(1.07 ** (364 / 365), rel=1e-6)
    assert px[days[2]] / px[days[1]] == pytest.approx(1.06 ** (368 / 365), rel=1e-6)
    assert liquid_series(days, yields={2022: 5.0}, cost_pct=1.0)[days[2]] < liquid_series(days, yields={2022: 5.0}, cost_pct=0.0)[days[2]]


def rotation_prices():
    from thunderbot.daily import LIQUID, liquid_series

    up = lambda i: 100 * 1.0008 ** i  # noqa: E731
    falls = lambda i: 100 * 1.0008 ** i if i < 450 else 100 * 1.0008 ** 450 * 0.997 ** (i - 450)  # noqa: E731
    px = {INDEX: series(up), BENCHMARK: series(up), "JUNIORBEES": series(falls), "GOLDBEES": series(lambda i: 100 * 1.0004 ** i)}
    px[LIQUID] = liquid_series(DAYS)
    return px


def test_trend_rotation_parks_the_falling_etf_in_the_liquid_etf():
    from thunderbot.daily import KEEP, LIQUID, EtfRotation

    strat = EtfRotation(assets=[BENCHMARK, "JUNIORBEES", "GOLDBEES"], mode="trend", sma_days=100)
    px = rotation_prices()
    hist_late = {s: [v for d, v in sorted(p.items())][:700] for s, p in px.items()}
    want = strat.target(DAYS[699], hist_late, {})
    assert want == pytest.approx({BENCHMARK: 1 / 3, "GOLDBEES": 1 / 3, LIQUID: 1 / 3})
    assert strat.target(DAYS[699], hist_late, dict(want)) == KEEP  # on target: no trade, no tax
    drifted = {BENCHMARK: 0.50, "GOLDBEES": 0.25, LIQUID: 0.25}
    assert strat.target(DAYS[699], hist_late, drifted) == want  # more than 10 points off: rebalance
    r = backtest(strat, px, DAYS[260], DAYS[-1], tax=CapitalGainsTax())
    assert r.metrics()["taxes"] > 0 and r.weights[-1][1].get(LIQUID, 0) > 0.25
    assert "JUNIORBEES" not in r.weights[-1][1]


def test_rank_rotation_holds_the_strongest_that_beat_cash():
    from thunderbot.daily import LIQUID, EtfRotation

    px = rotation_prices()
    hist = {s: [v for d, v in sorted(p.items())][:700] for s, p in px.items()}
    top1 = EtfRotation(assets=[BENCHMARK, "JUNIORBEES", "GOLDBEES"], top_n=1).target(DAYS[699], hist, {})
    assert top1 == {BENCHMARK: 1.0}
    # With three slots the falling ETF fails the cash hurdle and its slot goes to the liquid ETF.
    top3 = EtfRotation(assets=[BENCHMARK, "JUNIORBEES", "GOLDBEES"], top_n=3).target(DAYS[699], hist, {})
    assert "JUNIORBEES" not in top3 and top3[LIQUID] == pytest.approx(1 / 3)
    assert EtfRotation(assets=["GOLDBEES"]).target(DAYS[10], {s: v[:10] for s, v in hist.items()}, {}) is None


def test_static_mix_trades_once_a_year_and_reports_exit_tax():
    from thunderbot.daily import StaticMix, build_daily, no_timing_twin, result_payload

    px = rotation_prices()
    r = backtest(StaticMix({BENCHMARK: 0.5, "GOLDBEES": 0.5}), px, DAYS[0], DAYS[-1], tax=CapitalGainsTax())
    m = r.metrics()
    assert 2 <= m["rebalances"] <= 5  # the first day, then each March
    assert m["exit_tax"] > 0 and m["cagr_after_exit_tax_pct"] < m["cagr_pct"]
    assert m["benchmark"]["cagr_after_exit_tax_pct"] <= m["benchmark"]["cagr_pct"]
    alloc = result_payload(r)["allocation"]
    assert set(alloc) == {BENCHMARK, "GOLDBEES"} and sum(alloc.values()) == pytest.approx(100, abs=1.5)
    mix = build_daily("core_mix", {"gold_pct": 20, "next50_pct": 0})
    assert mix.weights == pytest.approx({BENCHMARK: 0.8, "GOLDBEES": 0.2}) and mix.name == "core_mix"
    twin = no_timing_twin(build_daily("etf_trend", {"midcap": 1}))
    assert set(twin.weights) == {BENCHMARK, "JUNIORBEES", "MOM100", "GOLDBEES"}
    assert build_daily("index_trend", {"liquid": 1}, cash_asset="LIQUIDCASE").cash_asset == "LIQUIDCASE"
    with pytest.raises(ValueError):
        build_daily("nope")


def test_backtest_decides_on_the_first_day_and_can_fill_the_same_day():
    px = {INDEX: series(lambda i: 100 * 1.001 ** i), BENCHMARK: series(lambda i: 100 * 1.001 ** i)}
    r1 = backtest(IndexTrend(sma_days=50, buffer_pct=0), px, DAYS[100], DAYS[160], costs=DeliveryCosts(slippage_pct=0))
    assert r1.weights[0][0] == DAYS[101]  # decided on day one, filled at the next close
    r0 = backtest(IndexTrend(sma_days=50, buffer_pct=0), px, DAYS[100], DAYS[160], costs=DeliveryCosts(slippage_pct=0), trade_lag=0)
    assert r0.weights[0][0] == DAYS[100] and r0.equity[-1][1] > r1.equity[-1][1]


def test_load_prices_uses_the_fetcher_cleans_and_adds_the_liquid_etf(tmp_path):
    from thunderbot.daily import LIQUID, load_prices

    calls = []

    def fetch(symbols, start, end):
        calls.append(list(symbols))
        return {s: {d: 100.0 + i for i, d in enumerate(DAYS[:300])} for s in symbols if s != "BAD"}, {"BAD": "HTTP 404"}

    errors: dict[str, str] = {}
    px = load_prices([INDEX, BENCHMARK, "BAD", LIQUID], DAYS[0], DAYS[299], cache_dir=tmp_path, fetch=fetch, errors=errors)
    assert set(px) == {INDEX, BENCHMARK, LIQUID} and errors == {"BAD": "HTTP 404"}
    assert px[LIQUID][DAYS[299]] > px[LIQUID][DAYS[0]] and len(px[LIQUID]) == 300
    load_prices([INDEX, BENCHMARK], DAYS[0], DAYS[299], cache_dir=tmp_path, fetch=fetch)
    assert len(calls) == 1  # the second call was served from the cache file
