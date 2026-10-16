from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest

from thunderbot.backtest import Backtester
from thunderbot.broker.paper import PaperBroker
from thunderbot.costs import CostModel
from thunderbot.data import synthetic_history
from thunderbot.engine import TradingEngine, round_tick
from thunderbot.llm.filter import PassThroughFilter
from thunderbot.llm.types import LLMDecision
from thunderbot.models import OrderStatus, OrderType, Side
from thunderbot.store import CompositeStore, SQLiteStore
from thunderbot.strategy.orb import OpeningRangeBreakout

from .conftest import bar, breakout_session, ts

ZERO_COSTS = CostModel(brokerage_flat=0, brokerage_min=0, stt_intraday_sell=0, exchange_txn=0, sebi_fee=0,
                       stamp_intraday_buy=0, gst=0)


def continue_session(bars, n_until=(15, 30), price=101.6):
    out = list(bars)
    t = out[-1].ts + timedelta(minutes=5)
    end = ts(*n_until)
    while t < end:
        out.append(bar(t, price, price + 0.1, price - 0.1, price, 1000))
        t += timedelta(minutes=5)
    return out


class TestBacktester:
    def run(self, settings, bars):
        return Backtester(settings, OpeningRangeBreakout(), ZERO_COSTS).run({"AAA": bars, "BBB": []})

    def test_stop_hit(self, settings):
        bars = breakout_session() + [bar(ts(9, 45), 101.6, 101.8, 98.9, 99.2, 1000)]
        res = self.run(settings, continue_session(bars, price=99.2))
        assert len(res.trades) == 1
        t = res.trades[0]
        assert t.exit_reason == "stop" and t.entry_price == 101.6 and t.exit_price == 99.0
        assert t.qty == 400  # 1% of 1 lakh / (101.5 - 99.0)
        assert t.net_pnl == pytest.approx(-2.6 * 400)

    def test_stop_assumed_first_when_both_touched(self, settings):
        bars = breakout_session() + [bar(ts(9, 45), 101.6, 107.0, 98.0, 101.0, 1000)]
        res = self.run(settings, continue_session(bars))
        assert res.trades[0].exit_reason == "stop"

    def test_target_hit(self, settings):
        bars = breakout_session() + [bar(ts(9, 45), 101.6, 102.0, 101.0, 101.8, 1000),
                                     bar(ts(9, 50), 101.8, 106.6, 101.7, 106.0, 1000)]
        res = self.run(settings, continue_session(bars, price=106))
        t = res.trades[0]
        assert t.exit_reason == "target" and t.exit_price == 106.5

    def test_eod_flatten(self, settings):
        res = self.run(settings, continue_session(breakout_session(), price=101.6))
        t = res.trades[0]
        assert t.exit_reason == "eod_flatten" and t.closed_at == ts(15, 5)

    def test_metrics_on_synthetic_data(self, settings):
        settings.symbols = ["S1", "S2", "S3"]
        data = synthetic_history(settings.symbols, date(2026, 1, 5), 20)
        m = Backtester(settings, OpeningRangeBreakout()).run(data).metrics()
        assert m["days"] == 20 and m["trades"] <= settings.max_trades_per_day * 20
        assert m["total_costs"] >= 0


class FakeData:
    def __init__(self, bars):
        self.bars = bars

    def candles(self, symbol, interval_minutes, start, end):
        if symbol != "AAA":
            return []
        return [b for b in self.bars if start <= b.ts < end]


class FakeQuotes:
    def __init__(self):
        self.prices = {}

    def ltp(self, symbols):
        return {s: self.prices[s] for s in symbols if s in self.prices}


class Harness:
    def __init__(self, settings, tmp_path, signal_filter=None, **engine_kwargs):
        self.now = ts(9, 45)
        self.quotes = FakeQuotes()
        self.broker = PaperBroker(settings.capital, slippage_bps=0)
        self.store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
        self.engine = TradingEngine(
            settings=settings, broker=self.broker, quotes=self.quotes,
            data=FakeData(continue_session(breakout_session())), strategy=OpeningRangeBreakout(),
            signal_filter=signal_filter or PassThroughFilter(), store=self.store, mode="paper",
            costs=ZERO_COSTS, now_fn=lambda: self.now, sleep_fn=lambda _: None, **engine_kwargs,
        )

    def tick(self, hh, mm, price):
        self.now = ts(hh, mm) + timedelta(seconds=5)
        self.quotes.prices["AAA"] = price
        self.engine.tick()

    def rows(self, table):
        return self.store.local.rows(table)


class TestEngine:
    def test_entry_places_protective_stop_then_exits_at_target(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        pos = h.engine.positions["AAA"]
        assert pos.side is Side.BUY and pos.qty == 400 and pos.entry_price == 101.5
        stop = h.broker.order_status(pos.stop_order_id)
        assert stop.request.order_type is OrderType.SL and stop.request.trigger_price == 99.0
        assert stop.request.price == 98.5 and stop.status is OrderStatus.PENDING

        h.tick(9, 50, 107.0)
        assert "AAA" not in h.engine.positions
        assert h.broker.order_status(pos.stop_order_id).status is OrderStatus.CANCELLED
        trades = h.rows("trades")
        assert len(trades) == 1 and trades[0]["exit_reason"] == "target"
        assert trades[0]["net_pnl"] == pytest.approx((107.0 - 101.5) * 400)
        assert h.broker.positions() == []
        assert len(h.rows("signals")) == 1

    def test_broker_stop_fill_is_recorded(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        h.tick(9, 50, 98.0)
        trades = h.rows("trades")
        assert trades[0]["exit_reason"] == "stop" and trades[0]["exit_price"] == 98.0
        assert h.engine.risk.state.realized_pnl == pytest.approx(-3.5 * 400)

    def test_flatten_at_305(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        h.tick(15, 5, 102.0)
        assert h.engine.positions == {}
        assert h.rows("trades")[0]["exit_reason"] == "eod_flatten"
        assert h.broker.positions() == []

    def test_failed_flatten_is_retried_next_tick(self, settings, tmp_path):
        from thunderbot.broker.base import BrokerError

        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        real_place = h.broker.place_order

        def reject_sells(req):
            if req.side is Side.SELL and req.order_type is OrderType.LIMIT:
                raise BrokerError("exchange rejected")
            return real_place(req)

        h.broker.place_order = reject_sells
        h.tick(15, 5, 102.0)
        assert "AAA" in h.engine.positions
        assert any(e["kind"] == "exit_failed" for e in h.rows("events"))
        h.broker.place_order = real_place
        h.tick(15, 6, 102.0)
        assert h.engine.positions == {}
        assert h.rows("trades")[0]["exit_reason"] == "eod_flatten"

    def test_kill_switch_flattens_and_blocks(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        h.store.set_control("kill_switch", True)
        h.tick(9, 50, 101.6)
        assert h.engine.positions == {}
        assert h.rows("trades")[0]["exit_reason"] == "kill_switch"

    def test_llm_veto_blocks_entry_and_is_journaled(self, settings, tmp_path):
        class Veto:
            enabled = True

            def review(self, ctx):
                return LLMDecision(False, 0.0, 0.9, "volume looks thin", ["low_volume"], model="fake")

        h = Harness(settings, tmp_path, signal_filter=Veto())
        h.tick(9, 45, 101.5)
        assert h.engine.positions == {}
        llm = h.rows("llm_decisions")
        assert len(llm) == 1 and llm[0]["approve"] is False and llm[0]["risk_flags"] == ["low_volume"]
        assert h.rows("orders") == []

    def test_daily_loss_halt_flattens(self, settings, tmp_path):
        settings.max_daily_loss_pct = 1.0  # Rs 1,000
        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        # remove the broker stop so the unrealized loss is what trips the limit
        h.broker.cancel_order(h.engine.positions["AAA"].stop_order_id)
        h.engine.positions["AAA"].stop = 90.0
        h.tick(9, 50, 98.9)  # -2.6 * 400 = -1040
        assert h.engine.risk.state.halted
        assert h.engine.positions == {}
        assert h.rows("trades")[0]["exit_reason"] == "daily_loss_halt"

    def test_outside_market_hours_is_idle(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.now = datetime(2026, 10, 15, 8, 0, tzinfo=ts(9, 0).tzinfo)
        h.engine.tick()
        assert h.engine.positions == {} and h.rows("orders") == []
        assert "heartbeat" in h.store.get_control()


    def test_login_gate_blocks_entries_until_confirmed(self, settings, tmp_path):
        h = Harness(settings, tmp_path, require_login_confirmation=True)
        h.tick(9, 45, 101.5)
        assert h.engine.positions == {}
        assert any(e["kind"] == "login_confirmation_required" for e in h.rows("events"))
        h.store.set_control("login_confirmed_for", "2026-10-15")
        h.engine.state.last_bar = None  # re-evaluate the same bar after confirmation
        h.engine.strategy.reset_day()
        h.tick(9, 45, 101.5)
        assert "AAA" in h.engine.positions

    def test_before_market_tick_hook_runs_only_in_market_hours(self, settings, tmp_path):
        calls = []
        h = Harness(settings, tmp_path, before_market_tick=calls.append)
        h.now = datetime(2026, 10, 15, 7, 0, tzinfo=ts(9, 0).tzinfo)
        h.engine.tick()
        assert calls == []
        h.tick(9, 45, 101.5)
        assert len(calls) == 1


def test_round_tick():
    assert round_tick(100.01, up=True) == 100.05
    assert round_tick(100.04, up=False) == 100.0
    assert round_tick(100.05, up=True) == 100.05
