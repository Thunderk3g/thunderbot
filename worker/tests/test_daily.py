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
