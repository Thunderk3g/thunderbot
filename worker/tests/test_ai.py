"""The AI desk: features, the model, training, the LLM trader and the bar-driven paper runner."""

from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta

import pytest

from thunderbot.ai import INDEX, features, gbm
from thunderbot.ai.dataset import Sample, build_samples, simulate
from thunderbot.ai.market import clean
from thunderbot.ai.runner import DESK_KEY, HISTORY_KEY, STATE_KEY, IntradayRunner
from thunderbot.ai.train import TrainError, load_active_model, save_model, train
from thunderbot.clock import IST
from thunderbot.config import Settings
from thunderbot.costs import CostModel
from thunderbot.data import synthetic_history
from thunderbot.llm.trader import ChatClient, ChatSignalFilter, build_trader_message, extract_json, provider_of
from thunderbot.llm.types import LLMDecision, ReviewContext
from thunderbot.models import Candle, Product, Side, Signal
from thunderbot.store import CompositeStore, SQLiteStore
from thunderbot.strategy import build_strategy
from thunderbot.strategy.ai import widen

from .conftest import DAY, bar, breakout_session, flat_session, ts

np = pytest.importorskip("numpy")


def _signal(side=Side.BUY, entry=101.5, stop=100.9, target=102.7) -> Signal:
    return Signal("AAA", side, Product.MIS, entry, stop, target, "orb", ts(9, 40), reason="test")


class TestFeatures:
    def test_every_feature_is_present_and_finite(self):
        session = breakout_session()
        prior = flat_session(DAY - timedelta(days=1))
        f = features.build(_signal(), session, prior, flat_session(DAY, 25000.0)[: len(session)], generator="orb")
        assert set(f) == set(features.FEATURES)
        assert all(isinstance(v, float) and v == v and abs(v) < 1e6 for v in f.values())
        assert f["gen_orb"] == 1.0 and f["gen_momentum"] == 0.0 and f["side"] == 1.0
        assert f["ret_open"] > 0 and f["rvol"] > 1  # up on the day, on a volume surge

    def test_directional_features_flip_with_the_side(self):
        session = breakout_session()
        long = features.build(_signal(), session, generator="orb")
        short = features.build(_signal(Side.SELL, 101.5, 102.1, 100.3), session, generator="orb")
        assert long["ret_open"] == -short["ret_open"] and long["range_pos"] == pytest.approx(1 - short["range_pos"])

    def test_regime_labels_a_trend_day(self):
        up = [bar(ts(9, 15) + timedelta(minutes=5 * i), 100 + i * 0.1, 100.2 + i * 0.1, 99.9 + i * 0.1, 100.1 + i * 0.1) for i in range(20)]
        r = features.regime(up, {"A": up, "B": up})
        assert r["label"] == "trend_up" and r["breadth_up_pct"] == 100


class TestModel:
    def _data(self, n=1500, seed=1):
        rng = np.random.default_rng(seed)
        X = rng.normal(size=(n, 6))
        y = ((X[:, 0] > 0.2) & (X[:, 3] < 0.5)).astype(float)
        flip = rng.random(n) < 0.1
        return X, np.where(flip, 1 - y, y)

    def test_learns_a_rule_and_python_prediction_matches_numpy(self):
        X, y = self._data()
        model = gbm.fit(X[:1000], y[:1000], n_trees=60, depth=3, lr=0.1, l2=1.0, min_leaf=20)
        z = gbm.raw_scores(model, X[1000:])
        assert gbm.auc(y[1000:], z) > 0.85
        assert [gbm.raw_score(model, row) for row in X[1000:1010].tolist()] == pytest.approx(z[:10].tolist())
        assert json.loads(json.dumps(model))["trees"] == model["trees"]  # plain JSON all the way down
        top = max(model["importance"], key=model["importance"].get)
        assert top in ("f0", "f3")

    def test_noise_scores_near_chance(self):
        rng = np.random.default_rng(5)
        X, y = rng.normal(size=(1200, 8)), (rng.random(1200) < 0.4).astype(float)
        model = gbm.fit(X[:800], y[:800], n_trees=40, depth=2, l2=20.0)
        assert 0.4 < gbm.auc(y[800:], gbm.raw_scores(model, X[800:])) < 0.6

    def test_platt_and_auc_edges(self):
        assert gbm.auc([1, 1, 1], [0.1, 0.2, 0.3]) is None
        assert gbm.auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == 1.0
        a, b = gbm.platt(np.array([-2.0, -1.0, 1.0, 2.0] * 30), np.array([0, 0, 1, 1] * 30))
        assert a > 0


class TestDataset:
    def test_widen_keeps_reward_to_risk(self):
        sig = _signal()  # 0.6 away on 101.5 = 0.59%
        wide = widen(sig, 1.0)
        assert wide.risk_per_share == pytest.approx(1.015, abs=0.01) and wide.reward_risk == pytest.approx(sig.reward_risk, abs=0.03)
        assert widen(sig, 0.2) is sig

    def test_simulate_charges_costs_and_respects_stop_first(self, settings, clock):
        sig = _signal()
        t0 = ts(9, 45)
        hit_both = [bar(t0, 101.5, 103.0, 100.0, 102.0)]  # stop and target inside one bar: the stop counts
        r, outcome = simulate(sig, hit_both, settings, clock, CostModel())
        assert outcome == "stop" and r < -1.0
        winner = [bar(t0, 101.5, 101.8, 101.2, 101.6), bar(t0 + timedelta(minutes=5), 101.6, 102.8, 101.5, 102.7)]
        r, outcome = simulate(sig, winner, settings, clock, CostModel())
        assert outcome == "target" and 1.5 < r < 2.0  # 2R gross, less charges
        assert simulate(sig, [bar(t0, 100.5, 100.6, 100.4, 100.5)], settings, clock, CostModel()) is None  # opened through the stop

    def test_build_samples_on_synthetic_history(self, settings):
        data = synthetic_history(["AAA", "BBB"], date(2026, 1, 5), 12, seed=3)
        samples = build_samples(data, settings, min_stop_pct=0.8)
        assert len(samples) > 10 and all(len(s.x) == len(features.FEATURES) for s in samples)
        assert {s.generator for s in samples} <= set(features.GENERATORS)
        assert samples == sorted(samples, key=lambda s: (s.day, s.ts, s.symbol))


def _samples(n_days=40, per_day=30, seed=2, signal=True) -> list[Sample]:
    rng = random.Random(seed)
    out = []
    d = date(2026, 6, 1)
    for i in range(n_days):
        for j in range(per_day):
            x = [rng.gauss(0, 1) for _ in features.FEATURES]
            good = (x[2] > 0) if signal else (rng.random() < 0.4)
            win = good if rng.random() < 0.85 else not good
            out.append(Sample(d + timedelta(days=i), f"S{j % 5}", f"{d + timedelta(days=i)}T10:{j:02d}", "orb", "BUY", x,
                              int(win), 1.4 if win else -1.1, "target" if win else "stop"))
    return out


class TestTraining:
    def test_finds_a_real_pattern_out_of_sample(self):
        model, report = train(_samples())
        assert report["verdict"] == "edge_supported" and report["oos"]["auc"] > 0.8
        assert report["oos"]["by_share"]["30"]["avg_r"] > report["oos"]["all"]["avg_r"]
        assert model["policy"]["strict"] is not None and model["policy"]["learn"] > 0
        assert model["setup"]["min_stop_pct"] == 0.8 and report["oos"]["curve"]

    def test_says_so_when_there_is_nothing_to_find(self):
        samples = _samples(signal=False)
        for s in samples:
            s.r_net = -0.3 if s.y else -1.2  # everything loses, as real setups did after costs
        model, report = train(samples)
        assert report["verdict"] == "no_edge" and "not found a profitable group" in report["verdict_text"]
        assert model["policy"]["strict"] is None

    def test_refuses_too_little_history(self):
        with pytest.raises(TrainError):
            train(_samples(n_days=5))

    def test_save_and_load(self, tmp_path):
        store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
        model, report = train(_samples())
        model_id = save_model(store, model, report)
        assert store.get_control()["ai_model"]["id"] == model_id
        assert load_active_model(store)["model"]["trees"] == model["trees"]


class TestTrader:
    def _ctx(self):
        sig = _signal()
        sig.features.update(generator="orb", ml_prob=0.41, ml_expected_r=-0.2, x={"rvol": 2.1, "ret_open": 0.8})
        return ReviewContext(sig, breakout_session(), extra={"market": {"label": "trend_up"}, "lessons": [{"day": "d", "text": "t"}]})

    def _filter(self, replies, settings=None):
        calls = []

        def post(url, body):
            calls.append((url, body))
            return replies[min(len(calls) - 1, len(replies) - 1)]

        s = settings or Settings(llm_api_key="k", llm_base_url="https://api.x.ai/v1", llm_chat_model="grok", llm_enabled=True)
        return ChatSignalFilter(s, ChatClient("k", "https://api.x.ai/v1", "grok", post=post)), calls

    def _ok(self, content):
        return 200, {"id": "r1", "model": "grok-x", "choices": [{"message": {"content": content}}],
                     "usage": {"prompt_tokens": 900, "completion_tokens": 80}}

    def test_take_is_parsed_and_clamped(self):
        f, calls = self._filter([self._ok('{"decision":"take","size_multiplier":1.7,"confidence":0.8,"rationale":"Clean.","risk_flags":["late"]}')])
        d = f.review(self._ctx())
        assert d.approve and d.size_multiplier == 1.0 and d.confidence == 0.8 and d.risk_flags == ["late"]
        assert d.model == "grok-x" and d.input_tokens == 900 and d.request_id == "r1"
        url, body = calls[0]
        assert url.endswith("/v1/chat/completions") and body["response_format"] == {"type": "json_object"}
        shown = json.loads(body["messages"][1]["content"].split("\n\n", 1)[1])
        assert shown["ml"]["prob"] == 0.41 and shown["market"]["label"] == "trend_up" and shown["stock_now"]["rvol"] == 2.1
        assert "x" not in json.dumps(shown["setup"])

    def test_skip_and_fenced_json(self):
        f, _ = self._filter([self._ok('Sure:\n```json\n{"decision": "skip", "confidence": 0.7, "rationale": "Thin."}\n```')])
        d = f.review(self._ctx())
        assert not d.approve and d.size_multiplier == 0.0

    def test_bad_reply_and_http_errors_follow_the_fail_mode(self):
        f, _ = self._filter([self._ok("I think you should buy.")])
        d = f.review(self._ctx())
        assert not d.approve and d.error and "llm_error" in d.risk_flags
        s = Settings(llm_api_key="k", llm_base_url="u", llm_chat_model="m", llm_fail_mode="pass")
        f, _ = self._filter([(401, {"error": {"message": "bad key"}})], s)
        d = f.review(self._ctx())
        assert d.approve and "bad key" in d.error

    def test_falls_back_when_json_mode_is_refused(self):
        f, calls = self._filter([(400, {"error": {"message": "response_format unsupported"}}),
                                 self._ok('{"decision":"take","size_multiplier":0.5,"confidence":0.6,"rationale":"ok"}')])
        d = f.review(self._ctx())
        assert d.approve and d.size_multiplier == 0.5 and "response_format" not in calls[1][1]

    def test_helpers(self):
        assert extract_json('x {"a": {"b": 1}} y') == {"a": {"b": 1}}
        with pytest.raises(ValueError):
            extract_json("nothing here")
        assert provider_of("https://api.x.ai/v1") == "xAI" and provider_of("https://api.groq.com/openai/v1") == "Groq"
        assert "Decide on this setup" in build_trader_message(self._ctx())


class TestMarket:
    def test_clean_drops_the_live_point_forming_bars_and_off_hours(self):
        now = datetime(2026, 10, 15, 10, 2, 30, tzinfo=IST)
        utc = lambda h, m, s=0: datetime(2026, 10, 15, h, m, s, tzinfo=IST)  # noqa: E731
        rows = [(utc(9, 10), 99, 99, 99, 99, 0), (utc(9, 50), 100, 101, 99, 100.5, 500), (utc(9, 55), 100.5, 100.4, 100.6, 100.5, 400),
                (utc(10, 0), 100.5, 100.7, 100.4, 100.6, 100), (utc(10, 2, 28), 100.65, 100.65, 100.65, 100.65, 0)]
        bars, last = clean(rows, 5, now)
        assert [b.ts.minute for b in bars] == [50] and last == 100.65  # 9:55 has high < low; 10:00 is still forming


# The runner


class Feed:
    """Bars for the runner: whatever has closed by ``now`` plus a last price, like Yahoo's answer."""

    def __init__(self, data: dict[str, list[Candle]], last: dict[str, float] | None = None):
        self.data, self.last, self.calls = data, last or {}, 0

    def __call__(self, symbols, interval, days, now):
        self.calls += 1
        step = timedelta(minutes=interval)
        bars = {s: [b for b in self.data.get(s, []) if b.ts + step <= now] for s in symbols}
        bars = {s: v for s, v in bars.items() if v}
        prices = {s: self.last.get(s, v[-1].close) for s, v in bars.items()}
        return bars, prices, {s: "no bars" for s in symbols if s not in bars}


class Take:
    enabled = True

    def __init__(self, approve=True, size=1.0):
        self.approve, self.size, self.seen = approve, size, []

    def review(self, ctx):
        self.seen.append(ctx)
        return LLMDecision(self.approve, self.size if self.approve else 0.0, 0.9, "because", ["flag"], model="fake-llm")


def _day_bars(after: list[Candle]) -> list[Candle]:
    return flat_session(DAY - timedelta(days=1), vol=1000) + breakout_session() + after


@pytest.fixture
def desk(tmp_path):
    s = Settings(capital=100_000, risk_per_trade_pct=1.0, max_position_notional_pct=100.0, slippage_bps=0.0,
                 ai_symbols=["AAA", "BBB"], data_dir=str(tmp_path))
    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    store.set_control("intraday_enabled", True)
    store.set_control("ai_model", {"id": "none", "trained_at": "2099-01-01T00:00:00+05:30"})  # no training job in these tests
    clock = {"now": ts(9, 45, DAY) + timedelta(seconds=10)}

    def make(data, llm=None, last=None):
        feed = Feed(data, last)
        runner = IntradayRunner(s, store, fetch=feed, filter_factory=lambda st: llm or Take(), now_fn=lambda: clock["now"],
                                sleep=lambda x: None)
        return runner, feed

    return s, store, clock, make


class TestRunner:
    def test_takes_a_breakout_then_exits_at_the_target(self, desk):
        s, store, clock, make = desk
        t = ts(9, 45)
        after = [bar(t, 101.5, 101.9, 101.3, 101.8), bar(t + timedelta(minutes=5), 101.8, 104.0, 101.7, 103.9)]
        llm = Take(size=0.5)
        runner, _ = make({"AAA": _day_bars(after), INDEX: flat_session(DAY, 25000.0)}, llm)

        out = runner.tick()  # 09:45:10, the 09:40 breakout bar has just closed
        assert out["entered"] == 1 and out["open"] == 1
        st = store.get_control()[STATE_KEY]
        pos = st["positions"]["AAA"]
        assert pos["side"] == "BUY" and pos["entry"] == 101.5  # filled at the last price, no slippage configured
        assert pos["stop"] == pytest.approx(101.5 * 0.992, abs=0.01)  # the 0.5% stop was widened to 0.8%
        full = int(100_000 * 0.01 / (pos["entry"] - pos["stop"]))
        assert pos["qty"] == pytest.approx(full * 0.5, abs=1)  # the LLM halved it
        ctx = llm.seen[0]
        assert ctx.extra["market"]["label"] and ctx.signal.features["generator"] == "orb"
        desk_view = store.get_control()[DESK_KEY]
        assert desk_view["status"] == "running" and desk_view["decisions"][0]["verdict"] == "take" and desk_view["watch"][0]["symbol"] == "AAA"

        assert runner.tick() == {"intraday": "bar already processed"}  # same bar, second scheduler
        clock["now"] = ts(9, 50) + timedelta(seconds=10)
        runner.tick()
        assert "AAA" in store.get_control()[STATE_KEY]["positions"]
        clock["now"] = ts(9, 55) + timedelta(seconds=10)
        runner.tick()
        st = store.get_control()[STATE_KEY]
        assert not st["positions"] and st["wins"] == 1 and st["risk"]["realized_pnl"] > 0
        trade = store.select("trades")[0]
        assert trade["exit_reason"] == "target" and trade["strategy"] == "ai" and trade["net_pnl"] == st["risk"]["realized_pnl"]
        outcome = store.select("signal_outcomes")[0]
        assert outcome["outcome"] == "target" and outcome["llm_decision"] == "approve" and outcome["risk_approved"] is True
        d = store.get_control()[DESK_KEY]["decisions"][0]
        assert d["status"] == "closed" and d["exit"] == "target" and d["r"] > 0 and d["by"] == "fake-llm"
        assert [o["purpose"] for o in store.select("orders", order="created_at", desc=False)] == ["entry", "exit:target"]

    def test_llm_skip_is_journalled_and_followed_to_its_outcome(self, desk):
        s, store, clock, make = desk
        t = ts(9, 45)
        after = [bar(t, 101.5, 101.6, 100.0, 100.2)]  # would have stopped out
        runner, _ = make({"AAA": _day_bars(after)}, Take(approve=False))
        assert runner.tick()["entered"] == 0
        d = store.get_control()[DESK_KEY]["decisions"][0]
        assert d["verdict"] == "skip" and d["by"] == "fake-llm" and d["note"] == "because"
        clock["now"] = ts(9, 50) + timedelta(seconds=10)
        runner.tick()
        outcome = store.select("signal_outcomes")[0]
        assert outcome["llm_decision"] == "reject" and outcome["outcome"] == "stop" and outcome["r_multiple"] == -1.0
        assert not store.select("trades")

    def test_model_floor_blocks_low_scores(self, desk, tmp_path):
        s, store, clock, make = desk
        model = {"kind": "gbm", "features": list(features.FEATURES), "base": -1.0, "trees": [], "calib": [1.0, 0.0],
                 "policy": {"learn": 0.5, "strict": None, "ev": [-0.3, 0.2]}, "setup": {"min_stop_pct": 0.8}}
        store.insert("models", {"id": "m1", "name": "intraday_setups", "model": {**model, "trees": [0.0]}, "report": {}})
        store.set_control("ai_model", {"id": "m1", "trained_at": "2099-01-01T00:00:00+05:30"})
        llm = Take()
        runner, _ = make({"AAA": _day_bars([])}, llm)
        assert runner.tick()["entered"] == 0 and not llm.seen  # p = sigmoid(-1) = 0.27 < 0.5: the LLM is never asked
        d = store.get_control()[DESK_KEY]["decisions"][0]
        assert d["verdict"] == "skip" and d["by"] == "model" and d["prob"] == pytest.approx(0.269, abs=0.001)
        assert store.select("signals")[0]["features"]["ml_expected_r"] == pytest.approx(-0.246, abs=0.001)

    def test_stopped_desk_takes_nothing_and_fetches_nothing(self, desk):
        s, store, clock, make = desk
        store.set_control("intraday_enabled", False)
        runner, feed = make({"AAA": _day_bars([])})
        assert runner.tick() == {"intraday": "off"} and feed.calls == 0
        assert store.get_control()[DESK_KEY]["status"] == "off"

    def test_flatten_and_day_close(self, desk):
        s, store, clock, make = desk
        quiet = [bar(ts(9, 45) + timedelta(minutes=5 * i), 101.5, 101.7, 101.4, 101.6) for i in range(69)]  # to 15:25
        runner, _ = make({"AAA": _day_bars(quiet)})
        runner.tick()
        assert "AAA" in store.get_control()[STATE_KEY]["positions"]
        clock["now"] = ts(15, 10) + timedelta(seconds=10)  # several calls were missed; the 15:05 bar has closed
        runner.tick()
        st = store.get_control()[STATE_KEY]
        assert not st["positions"] and store.select("trades")[0]["exit_reason"] == "eod_flatten"
        clock["now"] = ts(15, 35)
        assert runner.tick()["intraday"] == "day closed"
        control = store.get_control()
        assert control[STATE_KEY]["finalized"] and control[HISTORY_KEY][-1]["day"] == DAY.isoformat()
        assert control[HISTORY_KEY][-1]["trades"] == 1 and control["ai_memory"]["last_review"]["numbers"]["trades"] == 1
        assert runner.tick() == {"intraday": "closed"}

    def test_daily_loss_halts_the_desk(self, desk):
        s, store, clock, make = desk
        store.set_control("settings_overrides", {"max_daily_loss_pct": 0.1})
        crash = [bar(ts(9, 45), 101.5, 101.5, 99.0, 99.2)]
        runner, _ = make({"AAA": _day_bars(crash)})
        runner.tick()
        clock["now"] = ts(9, 50) + timedelta(seconds=10)
        out = runner.tick()
        st = store.get_control()[STATE_KEY]
        assert out["intraday"] == "halted" and st["risk"]["halted"] and st["losses"] == 1
        assert any(e["kind"] == "halt" for e in store.select("events"))

    def test_queues_training_when_there_is_no_model(self, desk):
        s, store, clock, make = desk
        store.set_control("ai_model", None)
        runner, _ = make({"AAA": _day_bars([])})
        runner.tick()
        runner.tick()
        assert len(store.select("jobs", {"kind": "train"})) == 1
