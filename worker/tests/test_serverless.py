import base64

from thunderbot import serverless
from thunderbot.config import Settings
from thunderbot.store import CompositeStore, RemoteStore, SQLiteStore


class FakeRemote:
    """Stands in for SupabaseStore: a unique (kind, day) on daily_runs and conditional updates."""

    def __init__(self):
        self.rows = {"daily_runs": [], "jobs": [], "events": []}
        self.control = {}
        self.fail = 0

    def insert(self, table, row):
        if self.fail:
            self.fail -= 1
            raise ConnectionError("network down")
        self.rows.setdefault(table, []).append(dict(row))

    def insert_new(self, table, row):
        if any(r["kind"] == row["kind"] and r["day"] == row["day"] for r in self.rows[table]):
            return False
        self.rows[table].append(dict(row))
        return True

    def select(self, table, filters=None, order="created_at", desc=True, limit=100):
        return [dict(r) for r in self.rows.get(table, []) if all(str(r.get(k)) == str(v) for k, v in (filters or {}).items())][:limit]

    def update(self, table, row_id, fields):
        for r in self.rows[table]:
            if r["id"] == row_id:
                r.update(fields)

    def update_where(self, table, where, fields):
        hit = []
        for r in self.rows[table]:
            ok = True
            for k, expr in where.items():
                op, _, val = expr.partition(".")
                ok &= (str(r.get(k)) == val) if op == "eq" else (str(r.get(k)) < val)
            if ok:
                r.update(fields)
                hit.append(dict(r))
        return hit

    def delete(self, table, row_id):
        self.rows[table] = [r for r in self.rows[table] if r["id"] != row_id]

    def get_control(self):
        return dict(self.control)

    def set_control(self, key, value):
        self.control[key] = value


def remote_store():
    return RemoteStore(FakeRemote(), sleep=lambda s: None)


def test_run_lock_is_exclusive_until_finished_released_or_stale():
    store = remote_store()
    first = store.claim("invest", "2026-11-11")
    assert first and store.claim("invest", "2026-11-11") is None
    assert store.claim("invest", "2026-11-12")  # another day is another lock
    store.release(first)
    again = store.claim("invest", "2026-11-11")
    assert again
    store.finish(again, "done", {"did": "rebalanced"})
    assert store.claim("invest", "2026-11-11", stale_after_s=0) is None  # finished: never run twice
    crashed = store.claim("invest", "2026-11-13")
    assert store.claim("invest", "2026-11-13") is None
    assert store.claim("invest", "2026-11-13", stale_after_s=-5) == crashed  # a dead run can be taken over


def test_remote_store_retries_then_raises():
    store = remote_store()
    store.remote.fail = 2
    store.event("note", "third attempt works")
    assert len(store.remote.rows["events"]) == 1
    store.remote.fail = 5
    try:
        store.insert("events", {"kind": "x", "message": "y"})
    except RuntimeError as e:
        assert "after 3 attempts" in str(e)
    else:
        raise AssertionError("a lost write must not pass silently")


def test_only_one_runner_gets_a_queued_job():
    store = remote_store()
    store.remote.rows["jobs"].append({"id": "j1", "status": "queued", "kind": "invest", "params": {}})
    assert store.claim_job("j1") is True and store.claim_job("j1") is False


def test_worker_auth_accepts_the_cron_secret_or_dashboard_login_only():
    env = {"CRON_SECRET": "s3cret", "DASHBOARD_USER": "me", "DASHBOARD_PASSWORD": "pw:with:colons"}
    basic = "Basic " + base64.b64encode(b"me:pw:with:colons").decode()
    assert serverless.authorized({"Authorization": "Bearer s3cret"}, env)
    assert serverless.authorized({"authorization": basic}, env)
    assert not serverless.authorized({"Authorization": "Bearer wrong"}, env)
    assert not serverless.authorized({"Authorization": "Basic " + base64.b64encode(b"me:nope").decode()}, env)
    assert not serverless.authorized({}, env)
    assert not serverless.authorized({"Authorization": "Bearer "}, {})  # nothing configured: refuse everyone
    assert not serverless.authorized({"Authorization": "Basic !!!"}, env)


def test_handle_health_tick_and_errors(tmp_path, monkeypatch):
    s = Settings(data_dir=str(tmp_path))
    assert serverless.handle("nope")[0] == 400
    code, body = serverless.handle("health", settings=s)
    assert code == 200 and body["supabase"] is False and body["strategy"] == "core_mix"
    assert serverless.handle("tick", settings=s)[0] == 500  # no Supabase configured: a clear error, not a crash

    class Runner:
        def tick(self):
            return {"did": "idle", "mode": "paper"}

    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    monkeypatch.setattr(serverless, "build_runner", lambda settings, st: Runner())
    code, body = serverless.handle("tick", settings=s, store=store)
    assert code == 200 and body["did"] == "idle" and body["jobs"] == []
    control = store.get_control()
    assert control["daily_catalog"][0]["name"] == "core_mix" and "effective_settings" in control

    def boom(settings, st):
        raise RuntimeError("yahoo down")

    monkeypatch.setattr(serverless, "build_runner", boom)
    code, body = serverless.handle("tick", settings=s, store=store)
    assert code == 500 and "yahoo down" in body["error"]
    assert any("yahoo down" in e["message"] for e in store.local.rows("events"))


def test_job_op_runs_a_queued_invest_backtest(tmp_path, monkeypatch):
    from datetime import timedelta

    from thunderbot import daily
    from thunderbot.clock import now_ist

    def fake_load(symbols, start, end, cache_dir=None, fetch=None, errors=None):
        days, d = [], start
        while d <= end:
            if d.weekday() < 5:
                days.append(d)
            d += timedelta(days=1)
        px = {sym: {d: 100 * (1.0004 + 0.0001 * (i % 3)) ** n for n, d in enumerate(days)} for i, sym in enumerate(symbols) if sym != daily.LIQUID}
        px[daily.LIQUID] = daily.liquid_series(days)
        return px

    monkeypatch.setattr(daily, "load_prices", fake_load)
    s = Settings(data_dir=str(tmp_path))
    store = CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))
    store.insert("jobs", {"id": "job-1", "kind": "invest", "status": "queued", "created_at": now_ist().isoformat(),
                          "params": {"strategy": "etf_trend", "years": 5, "capital": 200_000, "slab_rate_pct": 20}})
    code, body = serverless.handle("job", {"id": "job-1"}, settings=s, store=store)
    assert code == 200 and body["jobs"] == ["job-1"]
    job = store.select("jobs", {"id": "job-1"})[0]
    assert job["status"] == "done", job.get("error")
    r = job["result"]
    assert r["strategy"] == "etf_trend" and r["slab_rate_pct"] == 20 and r["comparators"][0]["label"].startswith("Same ETFs")
    assert r["metrics"]["cagr_after_exit_tax_pct"] is not None and r["allocation"] and "slab rate (20%)" in r["data_note"]
    assert serverless.handle("job", {"id": "job-1"}, settings=s, store=store)[1]["jobs"] == []  # nothing left to run


# The Claude rebalance reviewer: request shape, verdict parsing, and failing open.

def _ctx():
    from thunderbot.llm.rebalance import RebalanceContext

    return RebalanceContext(strategy="etf_trend", mode="paper", as_of="2026-11-30T15:10:00+05:30",
                            target={"NIFTYBEES": 0.5, "LIQUIDCASE": 0.5},
                            orders=[{"symbol": "GOLDBEES", "side": "SELL", "qty": 100, "price": 11.5, "value": 1150.0}],
                            facts={"GOLDBEES": {"price": 11.5, "change_1d_pct": -90.0}}, portfolio_value=500_000.0)


def test_rebalance_reviewer_request_and_verdict(tmp_path):
    from types import SimpleNamespace

    from thunderbot.llm.rebalance import SYSTEM_PROMPT, ClaudeRebalanceReviewer

    seen = {}

    class Messages:
        def parse(self, **kw):
            seen.update(kw)
            out = SimpleNamespace(decision="postpone", confidence=1.4, rationale=" GOLDBEES fell 90% in a day: a unit split. ",
                                  risk_flags=["possible_split", " "])
            return SimpleNamespace(stop_reason="end_turn", parsed_output=out, model="claude-opus-5-5",
                                   usage=SimpleNamespace(input_tokens=900, output_tokens=80))

    client = SimpleNamespace(beta=SimpleNamespace(messages=Messages()))
    s = Settings(data_dir=str(tmp_path), llm_enabled=True, llm_effort="low")
    v = ClaudeRebalanceReviewer(s, client=client).review(_ctx())
    assert v.approve is False and v.confidence == 1.0 and v.risk_flags == ["possible_split"]
    assert v.rationale.startswith("GOLDBEES") and v.input_tokens == 900 and v.error is None
    assert seen["model"] == "claude-opus-5-5" and seen["system"] == SYSTEM_PROMPT
    assert seen["output_config"] == {"effort": "low"} and seen["fallbacks"] == "default"
    assert '"change_1d_pct": -90.0' in seen["messages"][0]["content"] and "postponements_used" in v.prompt


def test_rebalance_reviewer_fails_open_on_refusal_and_errors(tmp_path):
    from types import SimpleNamespace

    from thunderbot.llm.rebalance import (
        ClaudeRebalanceReviewer,
        build_rebalance_reviewer,
    )

    s = Settings(data_dir=str(tmp_path), llm_enabled=True)
    refusal = SimpleNamespace(stop_reason="refusal", stop_details=SimpleNamespace(category="cyber"), parsed_output=None)
    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=lambda **kw: refusal)))
    v = ClaudeRebalanceReviewer(s, client=client).review(_ctx())
    assert v.approve is True and "refusal" in v.error and "llm_error" in v.risk_flags

    def boom(**kw):
        raise ValueError("schema mismatch")

    client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(parse=boom)))
    v = ClaudeRebalanceReviewer(s, client=client).review(_ctx())
    assert v.approve is True and "schema mismatch" in v.error
    assert build_rebalance_reviewer(Settings(data_dir=str(tmp_path), llm_enabled=False)) is None
