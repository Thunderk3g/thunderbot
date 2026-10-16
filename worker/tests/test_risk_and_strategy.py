from __future__ import annotations

from datetime import timedelta

from thunderbot.llm.types import LLMDecision
from thunderbot.models import ManagedPosition, Product, Side, Signal
from thunderbot.risk import RiskManager
from thunderbot.strategy.orb import OpeningRangeBreakout, ORBParams

from .conftest import bar, breakout_session, ts


def long_signal(symbol="AAA", entry=100.0, stop=99.0, target=102.0, product=Product.MIS, side=Side.BUY) -> Signal:
    return Signal(symbol, side, product, entry, stop, target, "test", ts(10, 0))


def decision(approve=True, mult=1.0, conf=0.9) -> LLMDecision:
    return LLMDecision(approve=approve, size_multiplier=mult, confidence=conf, rationale="test")


class TestRiskManager:
    def test_fixed_fractional_sizing(self, settings, clock):
        rm = RiskManager(settings, clock)
        v = rm.evaluate(long_signal(), None, {}, ts(10, 0))
        # 1% of 1 lakh = 1000 risk / Rs 1 per share = 1000 shares, capped by 1x notional (1000 * 100 = 1 lakh)
        assert v.approved and v.qty == 1000

    def test_llm_cannot_increase_size(self, settings, clock):
        rm = RiskManager(settings, clock)
        base = rm.evaluate(long_signal(entry=100, stop=98), None, {}, ts(10, 0)).qty
        boosted = rm.evaluate(long_signal(entry=100, stop=98), decision(mult=5.0), {}, ts(10, 0))
        assert boosted.qty == base
        assert boosted.size_multiplier == 1.0

    def test_llm_can_shrink_and_veto(self, settings, clock):
        rm = RiskManager(settings, clock)
        half = rm.evaluate(long_signal(entry=100, stop=98), decision(mult=0.5), {}, ts(10, 0))
        assert half.qty == 250
        vetoed = rm.evaluate(long_signal(), decision(approve=False), {}, ts(10, 0))
        assert not vetoed.approved and "LLM veto" in vetoed.reasons[0]
        unsure = rm.evaluate(long_signal(), decision(conf=0.1), {}, ts(10, 0))
        assert not unsure.approved

    def test_failed_llm_rejects_by_default(self, settings, clock):
        rm = RiskManager(settings, clock)
        d = LLMDecision.failed("timeout", settings.llm_fail_mode, "m")
        assert not rm.evaluate(long_signal(), d, {}, ts(10, 0)).approved
        d = LLMDecision.failed("timeout", "pass", "m")
        assert rm.evaluate(long_signal(), d, {}, ts(10, 0)).approved

    def test_product_rules(self, settings, clock):
        rm = RiskManager(settings, clock)
        assert not rm.evaluate(long_signal(product=Product.MTF), None, {}, ts(10, 0)).approved
        settings.allow_mtf_api = True
        assert rm.evaluate(long_signal(product=Product.MTF), None, {}, ts(10, 0)).approved
        short_cnc = long_signal(entry=100, stop=101, target=98, product=Product.CNC, side=Side.SELL)
        assert not rm.evaluate(short_cnc, None, {}, ts(10, 0)).approved
        short_mis = long_signal(entry=100, stop=101, target=98, side=Side.SELL)
        assert rm.evaluate(short_mis, None, {}, ts(10, 0)).approved

    def test_limits(self, settings, clock):
        rm = RiskManager(settings, clock)
        assert not rm.evaluate(long_signal(), None, {}, ts(9, 20)).approved  # before entry window
        assert not rm.evaluate(long_signal(), None, {}, ts(14, 45)).approved  # after entry window
        assert not rm.evaluate(long_signal(symbol="ZZZ"), None, {}, ts(10, 0)).approved
        assert not rm.evaluate(long_signal(stop=95), None, {}, ts(10, 0)).approved  # 5% stop > 3% cap
        assert not rm.evaluate(long_signal(stop=101), None, {}, ts(10, 0)).approved  # bad geometry
        assert not rm.evaluate(long_signal(), None, {}, ts(10, 0), kill_switch=True).approved
        pos = ManagedPosition("AAA", Side.BUY, Product.MIS, 10, 100, 99, 102, ts(9, 45), "x")
        assert not rm.evaluate(long_signal(), None, {"AAA": pos}, ts(10, 0)).approved

    def test_notional_and_cash_caps(self, settings, clock):
        rm = RiskManager(settings, clock)
        pos = ManagedPosition("BBB", Side.BUY, Product.MIS, 900, 100, 99, 102, ts(9, 45), "x")
        v = rm.evaluate(long_signal(), None, {"BBB": pos}, ts(10, 0))
        assert v.qty == 100  # only Rs 10k of the 1 lakh left
        v = rm.evaluate(long_signal(), None, {}, ts(10, 0), available_cash=5_000)
        assert v.qty == 50

    def test_daily_loss_halts(self, settings, clock):
        rm = RiskManager(settings, clock)
        rm.roll_day(ts(10, 0))
        rm.record_close(-1500)
        assert not rm.check_daily_loss(unrealized=-400)
        assert rm.check_daily_loss(unrealized=-600)
        v = rm.evaluate(long_signal(), None, {}, ts(10, 0))
        assert not v.approved and "halted" in v.reasons[0]

    def test_max_trades_per_day_resets_next_day(self, settings, clock):
        rm = RiskManager(settings, clock)
        rm.roll_day(ts(10, 0))
        for _ in range(settings.max_trades_per_day):
            rm.record_open()
        assert not rm.evaluate(long_signal(), None, {}, ts(10, 0)).approved
        from datetime import date

        from .conftest import ts as mk
        nxt = mk(10, 0, date(2026, 10, 16))
        assert rm.evaluate(long_signal(), None, {}, nxt).approved


class TestORB:
    def test_long_breakout(self):
        bars = breakout_session()
        s = OpeningRangeBreakout()
        sig = None
        for i in range(len(bars)):
            sig = s.on_bar("AAA", bars[: i + 1]) or sig
        assert sig is not None
        assert sig.side is Side.BUY and sig.product is Product.MIS
        assert sig.entry == 101.5 and sig.stop == 99.0
        assert sig.target == round(101.5 + 2 * 2.5, 2)
        assert sig.ts == bars[-1].ts

    def test_fires_once_per_day(self):
        bars = breakout_session()
        s = OpeningRangeBreakout()
        assert s.on_bar("AAA", bars) is not None
        assert s.on_bar("AAA", bars) is None
        s.reset_day()
        assert s.on_bar("AAA", bars) is not None

    def test_requires_volume(self):
        bars = breakout_session()
        last = bars[-1]
        bars[-1] = bar(last.ts, last.open, last.high, last.low, last.close, 500)
        assert OpeningRangeBreakout().on_bar("AAA", bars) is None

    def test_no_signal_if_already_outside(self):
        bars = breakout_session()
        prev = bars[-2]
        bars[-2] = bar(prev.ts, prev.open, 101.4, prev.low, 101.2, prev.volume)
        assert OpeningRangeBreakout().on_bar("AAA", bars) is None

    def test_range_width_filter(self):
        bars = breakout_session()
        assert OpeningRangeBreakout(ORBParams(max_range_pct=1.0)).on_bar("AAA", bars) is None

    def test_uses_prior_day_same_slot_volume(self):
        bars = breakout_session()
        # Prior days had huge volume at 9:40, so today's 4000 is not a volume surge.
        prior = [bar(b.ts - timedelta(days=d), 100, 100, 100, 100, 50_000) for d in (1, 2) for b in bars]
        prior.sort(key=lambda b: b.ts)
        assert OpeningRangeBreakout().on_bar("AAA", bars, prior) is None
