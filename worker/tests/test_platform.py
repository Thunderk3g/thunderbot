"""Tests for the dashboard-facing platform: overrides, strategies, jobs, replay, local API, outcomes."""

from __future__ import annotations

import json
import threading
import urllib.request
from datetime import date

import pytest

from thunderbot.config import Settings
from thunderbot.data import synthetic_history
from thunderbot.jobs import JobError, JobRunner
from thunderbot.llm.filter import HeuristicFilter
from thunderbot.llm.types import ReviewContext
from thunderbot.models import Product, Side, Signal
from thunderbot.replay import run_replay
from thunderbot.server import LocalAPI, make_handler, query_rows
from thunderbot.store import CompositeStore, SQLiteStore
from thunderbot.strategy import STRATEGIES, build_strategy, catalog, coerce_params

from .conftest import breakout_session, ts
from .test_backtest_and_engine import Harness


class TestOverrides:
    def test_env_only_keys_cannot_be_overridden(self):
        s = Settings()
        new, rejected = s.with_overrides({"live_trading_enabled": True, "allow_mtf_api": True,
                                          "expected_static_ip": "1.1.1.1", "groww_api_key": "x"})
        assert not new.live_trading_enabled and not new.allow_mtf_api and new.expected_static_ip is None
        assert set(rejected) == {"live_trading_enabled", "allow_mtf_api", "expected_static_ip", "groww_api_key"}

    def test_bounds_and_types(self):
        s = Settings()
        new, rejected = s.with_overrides({"max_open_positions": "4", "max_leverage": 9, "flatten_at": "15:10",
                                          "entry_start": "14:00", "entry_end": "10:00", "llm_effort": "turbo"})
        assert new.max_open_positions == 4 and new.flatten_at == "15:10"
        assert "max_leverage" in rejected and "entry_window" in rejected and "llm_effort" in rejected
        assert (new.entry_start, new.entry_end) == (s.entry_start, s.entry_end)

    def test_overrides_never_accumulate(self):
        s = Settings()
        a, _ = s.with_overrides({"max_open_positions": 7})
        b, _ = s.with_overrides({})
        assert a.max_open_positions == 7 and b.max_open_positions == s.max_open_positions

    def test_public_view_has_no_secrets(self):
        s = Settings(groww_api_key="SECRET", groww_totp_secret="TOTP", supabase_service_key="SVC")
        blob = json.dumps(s.public_view(), default=str)
        assert "SECRET" not in blob and "TOTP" not in blob and "SVC" not in blob


class TestStrategies:
    def test_catalog_and_params(self):
        names = {c["name"] for c in catalog()}
        assert names == {"orb", "vwap_reversion", "ema_pullback"}
        for c in catalog():
            for p in c["params"]:
                assert p["min"] <= p["default"] <= p["max"]

    def test_coerce_clamps_and_drops_unknown(self):
        assert coerce_params("ema_pullback", {"fast": "4.6", "slow": 999, "nope": 1}) == {"fast": 5, "slow": 80}

    @pytest.mark.parametrize("name", sorted(STRATEGIES))
    def test_strategies_produce_valid_signals_on_synthetic_data(self, name):
        data = synthetic_history(["X"], date(2026, 1, 5), 15, seed=3)["X"]
        strat = build_strategy(name)
        n = 0
        days = sorted({c.ts.date() for c in data})
        for d in days:
            strat.reset_day()
            session = [c for c in data if c.ts.date() == d]
            prior = [c for c in data if c.ts.date() < d][-400:]
            for i in range(len(session)):
                sig = strat.on_bar("X", session[: i + 1], prior)
                if sig:
                    n += 1
                    assert sig.product is Product.MIS
                    if sig.side is Side.BUY:
                        assert sig.stop < sig.entry < sig.target
                    else:
                        assert sig.target < sig.entry < sig.stop
        assert n > 0


class TestHeuristicReviewer:
    def test_vetoes_low_volume_and_shrinks_wide_stops(self):
        f = HeuristicFilter()
        weak = Signal("A", Side.BUY, Product.MIS, 100, 99, 102, "orb", ts(10, 0), features={"volume_ratio": 1.2})
        d = f.review(ReviewContext(weak, breakout_session()))
        assert not d.approve and "low_volume" in d.risk_flags and d.model == "heuristic"
        wide = Signal("A", Side.BUY, Product.MIS, 100, 98, 104, "orb", ts(10, 0), features={"volume_ratio": 2})
        d = f.review(ReviewContext(wide, breakout_session()))
        assert d.approve and d.size_multiplier == 0.5


class TestEngineExtras:
    def test_dashboard_overrides_apply_live(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.store.set_control("settings_overrides", {"max_open_positions": 1, "strategy": "vwap_reversion",
                                                   "live_trading_enabled": True})
        h.tick(9, 45, 101.5)
        assert h.engine.s.max_open_positions == 1 and h.engine.risk.s.max_open_positions == 1
        assert h.engine.strategy.name == "vwap_reversion"
        eff = h.store.get_control()["effective_settings"]
        assert eff["rejected"] == {"live_trading_enabled": "not editable from the dashboard"}
        assert eff["env_only"]["live_trading_enabled"] is False

    def test_signal_outcomes_recorded_for_vetoed_signals(self, settings, tmp_path):
        class Veto:
            enabled = True

            def review(self, ctx):
                from thunderbot.llm.types import LLMDecision
                return LLMDecision(False, 0.0, 0.9, "no", model="fake")

        h = Harness(settings, tmp_path, signal_filter=Veto())
        h.tick(9, 45, 101.5)
        assert h.engine.positions == {}
        h.tick(9, 50, 106.6)  # the vetoed trade would have hit its target
        out = h.rows("signal_outcomes")
        assert len(out) == 1 and out[0]["outcome"] == "target" and out[0]["llm_decision"] == "reject"
        assert out[0]["r_multiple"] == pytest.approx(2.0)

    def test_heartbeat_has_live_positions_and_equity_snapshots(self, settings, tmp_path):
        h = Harness(settings, tmp_path)
        h.tick(9, 45, 101.5)
        h.tick(9, 50, 102.5)
        hb = h.store.get_control()["heartbeat"]
        assert hb["positions"][0]["symbol"] == "AAA"
        assert hb["unrealized_pnl"] == pytest.approx(400.0)
        assert "wall_at" in hb
        assert len(h.rows("equity")) >= 1


class TestJobs:
    def runner(self, tmp_path):
        s = Settings(data_dir=str(tmp_path), symbols=["S1", "S2"])
        return JobRunner(CompositeStore(SQLiteStore(tmp_path / "j.sqlite3")), s)

    def test_backtest_job_round_trip(self, tmp_path):
        r = self.runner(tmp_path)
        r.store.insert("jobs", {"id": "job1", "kind": "backtest", "status": "queued",
                                "params": {"strategy": "orb", "data": "demo", "start": "2026-01-05", "end": "2026-03-31"}})
        assert r.run_once()
        job = r.store.select("jobs", {"id": "job1"})[0]
        assert job["status"] == "done" and job["progress"] == 1.0
        res = job["result"]
        assert {"metrics", "equity", "trades", "per_symbol", "data_note"} <= set(res)
        assert res["equity"] and "Synthetic" in res["data_note"]
        assert not r.run_once()  # queue empty

    def test_sweep_job_walk_forward(self, tmp_path):
        r = self.runner(tmp_path)
        res = r.execute("sweep", {"strategy": "orb", "data": "demo", "start": "2026-01-05", "end": "2026-04-30",
                                  "grid": {"reward_risk": [1.5, 2, 3], "volume_mult": [1.0, 1.5]}})
        assert len(res["rows"]) == 6
        nets = [row["in_sample"]["net_pnl"] for row in res["rows"]]
        assert nets == sorted(nets, reverse=True)
        assert all("out_of_sample" in row and "robust" in row for row in res["rows"])

    def test_bad_jobs_fail_cleanly(self, tmp_path):
        r = self.runner(tmp_path)
        with pytest.raises(JobError):
            r.execute("sweep", {"strategy": "orb", "data": "demo", "grid": {"not_a_param": [1]}})
        with pytest.raises(JobError):
            r.execute("backtest", {"strategy": "orb", "data": "s3://elsewhere"})
        r.store.insert("jobs", {"id": "j2", "kind": "backtest", "status": "queued", "params": {"strategy": "nope"}})
        r.run_once()
        assert r.store.select("jobs", {"id": "j2"})[0]["status"] == "error"


class TestReplay:
    def test_replay_drives_real_engine(self, tmp_path):
        s = Settings(data_dir=str(tmp_path), symbols=["S1", "S2", "S3"])
        data = synthetic_history(s.symbols, date(2026, 1, 5), 6, seed=11)
        store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
        engine = run_replay(s, data, store, HeuristicFilter(s))
        assert engine.positions == {}  # everything flattened by end of day
        local = store.local
        assert local.rows("signals") and local.rows("signal_outcomes")
        assert len(local.rows("signal_outcomes")) == len(local.rows("signals"))
        assert store.get_control()["heartbeat"]["mode"] == "replay"
        for t in local.rows("trades"):
            assert t["closed_at"][11:16] <= "15:05"


class TestLocalAPI:
    @pytest.fixture
    def server(self, tmp_path):
        from http.server import ThreadingHTTPServer

        store = SQLiteStore(tmp_path / "j.sqlite3")
        api = LocalAPI(store, Settings(data_dir=str(tmp_path)), "k3y")
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(api))
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        yield f"http://127.0.0.1:{httpd.server_address[1]}", store
        httpd.shutdown()

    def call(self, base, method, path, body=None, key="k3y"):
        req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                     headers={"apikey": key, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as e:
            return e.code, None

    def test_auth_required(self, server):
        base, _ = server
        assert self.call(base, "GET", "/rest/v1/trades", key="wrong")[0] == 401
        assert self.call(base, "GET", "/rest/v1/secrets")[0] == 404

    def test_postgrest_subset(self, server):
        base, store = server
        for i, pnl in enumerate([10, -5, 30]):
            store.insert("trades", {"id": f"t{i}", "symbol": "A" if i else "B", "net_pnl": pnl, "closed_at": f"2026-10-1{i}T10:00:00+05:30"})
        code, rows = self.call(base, "GET", "/rest/v1/trades?select=id,net_pnl&order=net_pnl.desc&limit=2")
        assert code == 200 and rows == [{"id": "t2", "net_pnl": 30}, {"id": "t0", "net_pnl": 10}]
        _, rows = self.call(base, "GET", "/rest/v1/trades?symbol=eq.A&closed_at=gte.2026-10-12")
        assert [r["id"] for r in rows] == ["t2"]
        assert self.call(base, "POST", "/rest/v1/jobs", {"id": "j1", "kind": "backtest", "status": "queued"})[0] == 201
        assert self.call(base, "PATCH", "/rest/v1/jobs?id=eq.j1", {"status": "done"})[0] == 204
        assert query_rows(store, "jobs", [("id", "eq.j1")])[0]["status"] == "done"

    def test_settings_overrides_validated_on_write(self, server):
        base, store = server
        self.call(base, "POST", "/rest/v1/control", {"key": "settings_overrides",
                                                     "value": {"max_open_positions": 2, "live_trading_enabled": True}})
        eff = store.get_control()["effective_settings"]
        assert eff["editable"]["max_open_positions"] == 2
        assert "live_trading_enabled" in eff["rejected"]
        _, rows = self.call(base, "GET", "/rest/v1/control?select=key,value")
        assert any(r["key"] == "strategy_catalog" for r in rows)
