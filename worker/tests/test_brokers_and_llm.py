from __future__ import annotations

from types import SimpleNamespace

import pytest

from thunderbot.broker.base import BrokerError
from thunderbot.broker.groww import GrowwBroker, map_status
from thunderbot.broker.paper import PaperBroker
from thunderbot.data import max_window_days, parse_groww_candles
from thunderbot.llm.filter import ClaudeSignalFilter, build_user_message
from thunderbot.llm.types import ReviewContext
from thunderbot.models import (
    OrderRequest,
    OrderStatus,
    OrderType,
    Product,
    Side,
    Signal,
)
from thunderbot.throttle import OrderThrottle

from .conftest import breakout_session, ts


def throttle() -> OrderThrottle:
    return OrderThrottle(9, 250, sleep=lambda _: None)


class TestPaperBroker:
    def test_marketable_limit_fills_at_better_of_ltp_and_limit(self):
        b = PaperBroker(100_000, slippage_bps=0)
        b.update_price("AAA", 100.0)
        o = b.place_order(OrderRequest("AAA", Side.BUY, 10, Product.MIS, OrderType.LIMIT, price=100.5))
        assert o.status is OrderStatus.FILLED and o.avg_price == 100.0
        assert b.positions()[0].qty == 10

    def test_non_marketable_limit_rests(self):
        b = PaperBroker(100_000, slippage_bps=0)
        b.update_price("AAA", 100.0)
        o = b.place_order(OrderRequest("AAA", Side.BUY, 10, Product.MIS, OrderType.LIMIT, price=99.0))
        assert o.status is OrderStatus.PENDING
        b.update_price("AAA", 98.9)
        assert b.order_status(o.order_id).status is OrderStatus.FILLED

    def test_sell_stop_triggers(self):
        b = PaperBroker(100_000, slippage_bps=0)
        b.update_price("AAA", 100.0)
        b.place_order(OrderRequest("AAA", Side.BUY, 10, Product.MIS, OrderType.LIMIT, price=101))
        stop = b.place_order(OrderRequest("AAA", Side.SELL, 10, Product.MIS, OrderType.SL, price=98.5, trigger_price=99.0))
        assert stop.status is OrderStatus.PENDING
        b.update_price("AAA", 99.5)
        assert b.order_status(stop.order_id).status is OrderStatus.PENDING
        filled = b.update_price("AAA", 98.0)
        assert [o.order_id for o in filled] == [stop.order_id]
        assert b.order_status(stop.order_id).avg_price == 98.0  # gap: fills below the limit (pessimistic)
        assert b.positions() == []

    def test_cancel(self):
        b = PaperBroker(100_000)
        o = b.place_order(OrderRequest("AAA", Side.BUY, 1, Product.MIS, OrderType.LIMIT, price=1))
        assert b.cancel_order(o.order_id).status is OrderStatus.CANCELLED


class FakeGroww:
    def __init__(self):
        self.calls = []

    def place_order(self, **kw):
        self.calls.append(("place_order", kw))
        return {"groww_order_id": "GMK123", "order_status": "OPEN", "order_reference_id": kw["order_reference_id"]}

    def get_order_detail(self, segment, groww_order_id):
        return {"groww_order_id": groww_order_id, "order_status": "EXECUTED", "filled_quantity": 10,
                "quantity": 10, "average_fill_price": 101.25}

    def cancel_order(self, groww_order_id, segment):
        self.calls.append(("cancel_order", groww_order_id))
        return {}

    def get_positions_for_user(self, segment=None):
        return {"positions": [
            {"trading_symbol": "AAA", "product": "MIS", "quantity": -5, "net_price": 99.5, "exchange": "NSE"},
            {"trading_symbol": "BBB", "product": "CNC", "quantity": 0, "net_price": 0},
        ]}

    def get_ltp(self, exchange_trading_symbols, segment):
        self.calls.append(("get_ltp", exchange_trading_symbols))
        return {"NSE_AAA": 101.0, "NSE_BBB": 55.5}

    def get_available_margin_details(self):
        return {"clear_cash": 50_000, "equity_margin_details": {"mis_balance_available": 42_000}}


class TestGrowwBroker:
    def test_place_order_maps_fields(self):
        client = FakeGroww()
        b = GrowwBroker(client, throttle())
        o = b.place_order(OrderRequest("AAA", Side.BUY, 10, Product.MIS, OrderType.LIMIT, price=101.234, reference_id="TB1"))
        name, kw = client.calls[0]
        assert kw == {
            "validity": "DAY", "exchange": "NSE", "order_type": "LIMIT", "product": "MIS", "quantity": 10,
            "segment": "CASH", "trading_symbol": "AAA", "transaction_type": "BUY", "order_reference_id": "TB1",
            "price": 101.23, "trigger_price": None,
        }
        assert o.order_id == "GMK123" and o.status is OrderStatus.PENDING
        st = b.order_status("GMK123")
        assert st.status is OrderStatus.FILLED and st.avg_price == 101.25 and st.request.symbol == "AAA"

    def test_mtf_blocked_unless_enabled(self):
        b = GrowwBroker(FakeGroww(), throttle())
        with pytest.raises(BrokerError):
            b.place_order(OrderRequest("AAA", Side.BUY, 1, Product.MTF, OrderType.LIMIT, price=10))
        b = GrowwBroker(FakeGroww(), throttle(), allow_mtf=True)
        assert b.place_order(OrderRequest("AAA", Side.BUY, 1, Product.MTF, OrderType.LIMIT, price=10)).order_id

    def test_order_validation(self):
        b = GrowwBroker(FakeGroww(), throttle())
        with pytest.raises(BrokerError):
            b.place_order(OrderRequest("AAA", Side.SELL, 1, Product.MIS, OrderType.SL, price=10))

    def test_positions_ltp_margin(self):
        client = FakeGroww()
        b = GrowwBroker(client, throttle())
        pos = b.positions()
        assert len(pos) == 1 and pos[0].qty == -5 and pos[0].product is Product.MIS
        assert b.ltp(["AAA", "BBB"]) == {"AAA": 101.0, "BBB": 55.5}
        assert ("get_ltp", ("NSE_AAA", "NSE_BBB")) in client.calls
        assert b.available_cash() == 42_000

    @pytest.mark.parametrize("raw,filled,qty,expected", [
        ("EXECUTED", 10, 10, OrderStatus.FILLED),
        ("COMPLETED", 10, 10, OrderStatus.FILLED),
        ("APPROVED", 4, 10, OrderStatus.PARTIAL),
        ("TRIGGER_PENDING", 0, 10, OrderStatus.PENDING),
        ("REJECTED", 0, 10, OrderStatus.REJECTED),
        ("FAILED", 0, 10, OrderStatus.REJECTED),
        ("CANCELLED", 0, 10, OrderStatus.CANCELLED),
        ("CANCELLED", 3, 10, OrderStatus.PARTIAL),
        ("NEW", 0, 10, OrderStatus.PENDING),
    ])
    def test_status_mapping(self, raw, filled, qty, expected):
        assert map_status(raw, filled, qty) is expected


class TestCandleParsing:
    def test_epoch_and_iso(self):
        resp = {"candles": [
            [1760500200, 100, 101, 99, 100.5, 1000, None],
            ["2025-10-15T09:20:00", 100.5, 102, 100, 101, 2000],
            [1760500200000, 100, 101, 99, 100.5, 1000],
        ]}
        c = parse_groww_candles(resp)
        assert len(c) == 3
        assert c[0].ts.utcoffset().total_seconds() == 19800
        assert c[-1].ts.hour == 9 and c[-1].ts.minute == 20

    def test_window_limits(self):
        assert max_window_days(1) == 30 and max_window_days(5) == 30
        assert max_window_days(15) == 90 and max_window_days(60) == 180


def _signal() -> Signal:
    return Signal("AAA", Side.BUY, Product.MIS, 101.5, 99.0, 106.5, "orb", ts(9, 40), "breakout", {"vwap": 100.4})


class FakeMessages:
    def __init__(self, response=None, exc=None):
        self.response, self.exc, self.kwargs = response, exc, None

    def parse(self, **kwargs):
        self.kwargs = kwargs
        if self.exc:
            raise self.exc
        return self.response


def fake_client(messages):
    return SimpleNamespace(beta=SimpleNamespace(messages=messages))


class TestClaudeFilter:
    def _ctx(self):
        return ReviewContext(_signal(), breakout_session())

    def test_request_shape_and_parse(self, settings):
        out = SimpleNamespace(decision="approve", size_multiplier=1.7, confidence=0.8,
                              rationale=" Clean break. ", risk_flags=["late_session", " "])
        resp = SimpleNamespace(stop_reason="end_turn", parsed_output=out, model="claude-opus-5-5",
                               usage=SimpleNamespace(input_tokens=900, output_tokens=120), _request_id="req_1")
        msgs = FakeMessages(resp)
        d = ClaudeSignalFilter(settings, client=fake_client(msgs)).review(self._ctx())
        assert d.approve and d.size_multiplier == 1.0  # clamped
        assert d.rationale == "Clean break." and d.risk_flags == ["late_session"]
        kw = msgs.kwargs
        assert kw["model"] == "claude-opus-5-5"
        assert kw["fallbacks"] == "default" and kw["betas"] == ["server-side-fallback-2026-07-01"]
        assert kw["output_config"] == {"effort": "medium"}
        assert "thinking" not in kw and "temperature" not in kw
        assert '"symbol": "AAA"' in kw["messages"][0]["content"]

    def test_refusal_fails_closed(self, settings):
        resp = SimpleNamespace(stop_reason="refusal", parsed_output=None, stop_details=SimpleNamespace(category=None),
                               usage=None, _request_id="req_2")
        d = ClaudeSignalFilter(settings, client=fake_client(FakeMessages(resp))).review(self._ctx())
        assert not d.approve and d.error and "refusal" in d.error

    def test_exception_respects_fail_mode(self, settings):
        f = ClaudeSignalFilter(settings, client=fake_client(FakeMessages(exc=RuntimeError("boom"))))
        assert not f.review(self._ctx()).approve
        settings.llm_fail_mode = "pass"
        assert f.review(self._ctx()).approve

    def test_prompt_contains_only_given_bars(self):
        msg = build_user_message(self._ctx())
        assert msg.count('"t":') == len(breakout_session())
        assert "09:40" in msg
