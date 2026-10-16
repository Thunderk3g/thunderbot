from __future__ import annotations

from datetime import datetime

import pytest

from thunderbot.clock import IST, MarketClock, token_is_stale
from thunderbot.compliance import OrderRefGenerator, check_static_ip
from thunderbot.config import HARD_MAX_LEVERAGE, HARD_MAX_ORDERS_PER_SECOND, Settings
from thunderbot.costs import CostModel
from thunderbot.models import Product, Side
from thunderbot.throttle import OrderThrottle

from .conftest import DAY, ts


class TestClock:
    def test_last_completed_bar(self, clock: MarketClock):
        assert clock.last_completed_bar_start(ts(9, 17), 5) is None
        assert clock.last_completed_bar_start(ts(9, 20), 5) == ts(9, 15)
        assert clock.last_completed_bar_start(ts(9, 44), 5) == ts(9, 35)

    def test_windows(self, clock: MarketClock):
        assert not clock.in_entry_window(ts(9, 20))
        assert clock.in_entry_window(ts(10, 0))
        assert not clock.in_entry_window(ts(14, 30))
        assert clock.should_flatten(ts(15, 5))
        assert not clock.should_flatten(ts(15, 4))

    def test_weekend_and_holiday(self):
        c = MarketClock(holidays={DAY})
        assert not c.is_trading_day(DAY)
        assert not c.is_market_open(datetime(2026, 10, 17, 10, 0, tzinfo=IST))  # Saturday

    def test_token_expiry_at_6am(self):
        issued = datetime(2026, 10, 15, 8, 0, tzinfo=IST)
        assert not token_is_stale(issued, datetime(2026, 10, 15, 23, 0, tzinfo=IST))
        assert token_is_stale(issued, datetime(2026, 10, 16, 6, 0, tzinfo=IST))
        early = datetime(2026, 10, 15, 5, 0, tzinfo=IST)
        assert token_is_stale(early, datetime(2026, 10, 15, 6, 1, tzinfo=IST))


class TestConfig:
    def test_hard_ceilings_cannot_be_exceeded(self, monkeypatch):
        monkeypatch.setenv("TB_ORDERS_PER_SECOND", "50")
        monkeypatch.setenv("TB_MAX_LEVERAGE", "20")
        monkeypatch.setenv("TB_LLM_FAIL_MODE", "yolo")
        s = Settings.from_env()
        assert s.orders_per_second == HARD_MAX_ORDERS_PER_SECOND
        assert s.max_leverage == HARD_MAX_LEVERAGE
        assert s.llm_fail_mode == "reject"
        assert len(s.warnings) == 3

    def test_live_and_mtf_off_by_default(self):
        s = Settings.from_env()
        assert s.live_trading_enabled is False
        assert s.allow_mtf_api is False
        assert s.llm_model == "claude-opus-5-5"


class TestCosts:
    def test_intraday_round_trip(self):
        c = CostModel()
        # 100 shares @ 1000 -> Rs 1 lakh per leg: brokerage capped at Rs 20 per leg
        total = c.round_trip(Side.BUY, 100, 1000.0, 1010.0, Product.MIS)
        buy = c.leg(Side.BUY, 100, 1000.0, Product.MIS)
        sell = c.leg(Side.SELL, 100, 1010.0, Product.MIS)
        assert total == pytest.approx(buy + sell, abs=0.01)
        assert sell > buy  # STT only on the sell side intraday
        assert 60 < total < 90

    def test_delivery_costs_more_than_intraday(self):
        c = CostModel()
        assert c.round_trip(Side.BUY, 100, 1000, 1000, Product.CNC) > c.round_trip(Side.BUY, 100, 1000, 1000, Product.MIS)

    def test_small_order_brokerage_floor(self):
        c = CostModel(stt_intraday_sell=0, exchange_txn=0, sebi_fee=0, stamp_intraday_buy=0, gst=0)
        assert c.leg(Side.BUY, 1, 100.0, Product.MIS) == 5.0  # 0.1% would be Rs 0.10

    def test_mtf_interest(self):
        assert CostModel().mtf_interest(100_000, 10) == 410.0


class TestThrottle:
    def test_blocks_beyond_per_second(self):
        t = [0.0]
        waits = []

        def sleep(d):
            waits.append(d)
            t[0] += d

        th = OrderThrottle(3, 100, clock=lambda: t[0], sleep=sleep)
        for _ in range(3):
            assert th.acquire() == 0
        assert th.acquire() == pytest.approx(1.0)
        assert waits == [pytest.approx(1.0)]

    def test_blocks_beyond_per_minute(self):
        t = [0.0]

        def sleep(d):
            t[0] += d

        th = OrderThrottle(100, 5, clock=lambda: t[0], sleep=sleep)
        for _ in range(5):
            th.acquire()
            t[0] += 0.5
        waited = th.acquire()
        assert waited == pytest.approx(60.0 - 2.5)


class TestCompliance:
    def test_ip_whitelist(self):
        assert check_static_ip("1.2.3.4,5.6.7.8", observed="5.6.7.8").ok
        assert not check_static_ip("1.2.3.4", observed="9.9.9.9").ok
        assert not check_static_ip(None, observed="1.2.3.4").ok

    def test_order_refs_unique_and_valid(self):
        g = OrderRefGenerator()
        refs = {g.next(ts(10, 0)) for _ in range(500)}
        assert len(refs) == 500
        assert all(r.isalnum() and 8 <= len(r) <= 20 for r in refs)
