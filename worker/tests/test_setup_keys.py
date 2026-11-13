"""Keys saved from the dashboard's setup screen: encryption, precedence over the environment, the
reviewers on either provider family, the read-only Groww check, and the rule that nothing saved can
turn on real orders. Fabricated keys only."""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

import thunderbot.secrets as vault
from thunderbot.broker.base import BrokerError
from thunderbot.broker.check import login_check
from thunderbot.config import OVERRIDABLE, Settings
from thunderbot.credentials import CREDENTIAL_FIELDS, apply_credentials
from thunderbot.jobs import JobRunner
from thunderbot.llm.filter import ClaudeSignalFilter, PassThroughFilter, build_filter
from thunderbot.llm.rebalance import (
    ChatRebalanceReviewer,
    ClaudeRebalanceReviewer,
    RebalanceContext,
    build_rebalance_reviewer,
)
from thunderbot.llm.trader import ChatClient, ChatSignalFilter
from thunderbot.server import LocalAPI, make_handler
from thunderbot.store import CompositeStore, SQLiteStore

MASTER = "test-master-key-for-vectors"
# Produced once by dashboard/lib/secrets.ts (Node) with MASTER and the IV 00 01 .. 0b.
NODE_IV = bytes(range(12))
NODE_OBJECT = {"provider": "openai_compatible", "preset": "groq", "base_url": "https://api.groq.com/openai/v1",
               "api_key": "gsk_test_₹_key", "model": "m-1"}
NODE_BLOB = ("v1:AAECAwQFBgcICQoL59YCapZkfIQZZfsqZkK5l8t0BYMQhwWSbEGeP9rRJ4J1PaapATasjdBG7bVv9N1tQJ02zzOzd94z1B/POHM0U2yXpa8ldZKA"
             "gqf28VHjdu8N/s15ED35PqCvxMwjN1gxau0jbpwQf29wn7gCKpbmKn0VFA2kxmiCJX1jeUAAV4y0C2AAQ7MmahQNAkPK2Uw61dc+6zalJg==")

ENV = {"TB_SECRET_KEY": MASTER}
GROQ = {"provider": "openai_compatible", "preset": "groq", "base_url": "https://api.groq.com/openai/v1",
        "api_key": "gsk_saved_in_dashboard", "model": "some-groq-model"}
CLAUDE = {"provider": "anthropic", "preset": "anthropic", "base_url": "https://api.anthropic.com",
          "api_key": "sk-ant-saved-in-dashboard", "model": "claude-test-model"}


@pytest.fixture(autouse=True)
def _fresh_vault(monkeypatch):
    monkeypatch.setattr(vault, "_warned", set())
    monkeypatch.setattr(vault, "_table_down_until", 0.0)
    for name in ("TB_SECRET_KEY", "SUPABASE_SERVICE_ROLE_KEY", "TB_LOCAL_API_KEY", "TB_LLM_ENABLED", "ANTHROPIC_API_KEY",
                 "ANTHROPIC_AUTH_TOKEN"):
        monkeypatch.delenv(name, raising=False)


def store_with(tmp_path, **secrets) -> SQLiteStore:
    store = SQLiteStore(tmp_path / "journal.sqlite3")  # the file a local worker opens under TB_DATA_DIR
    for name, obj in secrets.items():
        store.insert("secrets", {"id": name, "name": name, "ciphertext": vault.encrypt(obj, MASTER), "hint": "…", "meta": {},
                                 "updated_at": "2026-11-13T10:00:00+05:30"})
    return store


def fake_groww_key(role: str) -> str:
    def b64(obj) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")
    return f"{b64({'alg': 'ES256'})}.{b64({'sub': json.dumps({'role': role})})}.c2ln"


# Encryption


def test_round_trip_and_wrong_key():
    blob = vault.encrypt({"api_key": "k", "n": 1}, MASTER)
    assert blob.startswith("v1:") and "k" not in blob[3:10]
    assert vault.decrypt(blob, MASTER) == {"api_key": "k", "n": 1}
    assert vault.encrypt({"api_key": "k"}, MASTER) != vault.encrypt({"api_key": "k"}, MASTER)  # a fresh IV each time
    with pytest.raises(vault.SecretError, match="wrong key"):
        vault.decrypt(blob, MASTER + "x")
    tampered = blob[:-6] + ("A" if blob[-6] != "A" else "B") + blob[-5:]
    with pytest.raises(vault.SecretError):
        vault.decrypt(tampered, MASTER)
    for bad in ("", "v2:abcd", "v1:", "v1:!!!", "v1:" + base64.b64encode(b"short").decode()):
        with pytest.raises(vault.SecretError):
            vault.decrypt(bad, MASTER)


def test_reads_what_the_dashboard_wrote_and_writes_the_same_bytes():
    assert vault.decrypt(NODE_BLOB, MASTER) == NODE_OBJECT
    assert vault.encrypt(NODE_OBJECT, MASTER, iv=NODE_IV) == NODE_BLOB


def test_live_round_trip_with_the_dashboard_code():
    """Runs the real dashboard/lib/secrets.ts under Node, when Node and the dashboard's packages are there."""
    dashboard = Path(__file__).resolve().parents[2] / "dashboard"
    if not shutil.which("node") or not (dashboard / "node_modules" / "server-only").is_dir():
        pytest.skip("node or the dashboard's node_modules are not available")
    obj = {"api_key": "sk-from-python-₹", "model": "m"}
    run = subprocess.run(
        ["node", "--conditions=react-server", "--experimental-strip-types", str(Path(__file__).with_name("secrets_vector.mjs")),
         str(dashboard / "lib" / "secrets.ts"), MASTER, vault.encrypt(obj, MASTER)],
        capture_output=True, text=True, timeout=60, cwd=dashboard)
    if run.returncode != 0 and "strip-types" in run.stderr:
        pytest.skip("this Node cannot run TypeScript directly")
    assert run.returncode == 0, run.stderr[-500:]
    out = json.loads(run.stdout.strip().splitlines()[-1])
    assert out["fromPython"] == obj
    assert vault.decrypt(out["blob"], MASTER) == obj


def test_master_key_order():
    assert vault.master_key({}) == (None, None)
    assert vault.master_key({"TB_LOCAL_API_KEY": "local"}) == ("local", "service_key")
    assert vault.master_key({"TB_LOCAL_API_KEY": "local", "SUPABASE_SERVICE_ROLE_KEY": "svc"}) == ("svc", "service_key")
    assert vault.master_key({"SUPABASE_SERVICE_ROLE_KEY": "svc", "TB_SECRET_KEY": " own "}) == ("own", "TB_SECRET_KEY")


def test_unreadable_secrets_are_ignored_not_fatal(tmp_path, monkeypatch, caplog):
    store = store_with(tmp_path, llm=GROQ)
    assert vault.read_secret(store, "llm", ENV) == GROQ
    assert vault.read_secret(store, "groww", ENV) is None
    assert vault.read_secret(store, "llm", {}) is None  # no key to decrypt with
    assert vault.read_secret(store, "llm", {"TB_SECRET_KEY": "another"}) is None

    def no_package(master):
        raise vault.SecretError("the 'cryptography' package is not installed (pip install 'thunderbot[secrets]')")

    monkeypatch.setattr(vault, "_aesgcm", no_package)
    with caplog.at_level("WARNING"):
        s = apply_credentials(Settings(data_dir=str(tmp_path), llm_api_key="env-key", llm_base_url="https://api.x.ai/v1",
                                       llm_chat_model="env-model", llm_enabled=True), store, ENV)
    assert s.llm_api_key == "env-key" and s.llm_source_view == "environment"  # the environment still works
    assert "cryptography" in caplog.text and GROQ["api_key"] not in caplog.text

    class NoTable:
        calls = 0

        def select(self, *a, **k):
            NoTable.calls += 1
            raise RuntimeError("404 relation does not exist")

    assert vault.read_secret(NoTable(), "llm", ENV) is None and vault.read_secret(NoTable(), "groww", ENV) is None
    assert NoTable.calls == 1  # a missing table is not asked for again on every pass


# Which key wins


def test_saved_key_wins_over_the_environment(tmp_path):
    env_chat = Settings(data_dir=str(tmp_path), llm_api_key="env-key", llm_base_url="https://api.x.ai/v1",
                        llm_chat_model="env-model", llm_enabled=True, llm_source="environment")
    assert apply_credentials(env_chat, store_with(tmp_path), ENV).llm_api_key == "env-key"  # nothing saved

    s = apply_credentials(env_chat, store_with(tmp_path, llm=GROQ), ENV)
    assert (s.llm_api_key, s.llm_base_url, s.llm_chat_model) == (GROQ["api_key"], GROQ["base_url"], GROQ["model"])
    assert s.llm_enabled and s.llm_source == "dashboard" and s.llm_provider == "Groq"
    assert isinstance(build_filter(s), ChatSignalFilter) and isinstance(build_rebalance_reviewer(s), ChatRebalanceReviewer)
    assert build_filter(s).client.api_key == GROQ["api_key"]

    # A saved Anthropic key replaces an OpenAI-compatible endpoint from the environment.
    s = apply_credentials(env_chat, store_with(tmp_path / "b", llm=CLAUDE), ENV)
    assert not s.chat_llm and s.anthropic_api_key == CLAUDE["api_key"] and s.llm_model == CLAUDE["model"]
    assert s.llm_provider == "Anthropic" and s.llm_enabled
    view = s.public_view()["env_only"]
    assert view["llm_source"] == "dashboard" and view["llm_model"] == CLAUDE["model"] and view["llm_configured"]
    assert CLAUDE["api_key"] not in json.dumps(s.public_view()) and CLAUDE["api_key"] not in repr(s)


def test_saved_anthropic_key_reaches_the_sdk_client(tmp_path):
    pytest.importorskip("anthropic")
    s = apply_credentials(Settings(data_dir=str(tmp_path)), store_with(tmp_path, llm=CLAUDE), ENV)
    f = build_filter(s)
    assert isinstance(f, ClaudeSignalFilter) and f.client.api_key == CLAUDE["api_key"] and f.label == CLAUDE["model"]
    r = build_rebalance_reviewer(s)
    assert isinstance(r, ClaudeRebalanceReviewer) and r.client.api_key == CLAUDE["api_key"]


def test_off_switch_and_clearing(tmp_path):
    base = Settings(data_dir=str(tmp_path))
    store = store_with(tmp_path, llm=GROQ)
    off = apply_credentials(base, store, {**ENV, "TB_LLM_ENABLED": "false"})
    assert off.llm_api_key == GROQ["api_key"] and not off.llm_enabled
    assert isinstance(build_filter(off), PassThroughFilter) and build_rebalance_reviewer(off) is None

    on = apply_credentials(base, store, ENV)
    assert on.llm_enabled and on.env_credentials["llm_api_key"] is None
    # The dashboard's own LLM switch still applies on top.
    assert not on.with_overrides({"llm_enabled": False})[0].llm_enabled

    # Applying again starts from the environment, so a key removed in the dashboard stops being used.
    store.delete("secrets", ["llm"])
    cleared = apply_credentials(on, store, ENV)
    assert cleared.llm_api_key is None and not cleared.llm_enabled and cleared.llm_source_view is None
    assert apply_credentials(apply_credentials(base, store_with(tmp_path / "c", llm=GROQ), ENV),
                             store_with(tmp_path / "c2", llm=CLAUDE), ENV).anthropic_api_key == CLAUDE["api_key"]


def test_incomplete_saved_llm_is_ignored(tmp_path):
    for bad in ({"provider": "openai_compatible", "preset": "custom", "api_key": "k", "model": "m"},  # no base URL
                {"provider": "anthropic", "api_key": "k"},  # no model
                {"provider": "something-else", "api_key": "k", "model": "m"},
                {"provider": "anthropic", "model": "m"}):
        s = apply_credentials(Settings(data_dir=str(tmp_path)), store_with(tmp_path / str(id(bad)), llm=bad), ENV)
        assert s.llm_source_view is None and not s.llm_enabled


def test_groww_key_from_the_dashboard(tmp_path):
    env = Settings(data_dir=str(tmp_path), groww_api_key="env-key", groww_api_secret="env-secret", groww_source="environment")
    assert env.public_view()["env_only"]["groww_source"] == "environment"
    saved = {"api_key": fake_groww_key("auth-totp"), "totp_secret": "JBSWY3DPEHPK3PXP"}
    s = apply_credentials(env, store_with(tmp_path, groww=saved), ENV)
    assert s.groww_api_key == saved["api_key"] and s.groww_totp_secret == "JBSWY3DPEHPK3PXP" and s.groww_api_secret is None
    view = s.public_view()["env_only"]
    assert view["groww_source"] == "dashboard" and view["groww_auth"] == "totp" and view["groww_configured"]
    assert saved["api_key"] not in json.dumps(s.public_view()) and "JBSWY3DPEHPK3PXP" not in repr(s)


def test_nothing_saved_can_turn_on_real_orders(tmp_path):
    forbidden = ("live_trading_enabled", "expected_static_ip", "allow_mtf_api", "require_login_confirmation",
                 "max_leverage", "orders_per_second")
    assert not set(forbidden[:4]) & set(CREDENTIAL_FIELDS) and not set(forbidden[:4]) & set(OVERRIDABLE)
    smuggle = {"live_trading_enabled": True, "expected_static_ip": "1.2.3.4", "allow_mtf_api": True,
               "require_login_confirmation": False, "max_leverage": 50, "orders_per_second": 99}
    store = store_with(tmp_path, llm={**GROQ, **smuggle}, groww={"api_key": "k", "api_secret": "s", **smuggle},
                       live=smuggle, settings=smuggle)
    base = Settings(data_dir=str(tmp_path))
    s = apply_credentials(base, store, ENV)
    assert s.groww_api_key == "k" and s.llm_api_key == GROQ["api_key"]  # the secrets were read
    for name in forbidden:
        assert getattr(s, name) == getattr(base, name), name
    assert s.live_trading_enabled is False and s.expected_static_ip is None and s.allow_mtf_api is False
    changed = {f for f in base.__dataclass_fields__ if getattr(s, f) != getattr(base, f)}
    assert changed <= set(CREDENTIAL_FIELDS) | {"env_credentials"}

    # The dashboard's settings route cannot do it either.
    _, rejected = s.with_overrides({"live_trading_enabled": True, "expected_static_ip": "1.2.3.4", "allow_mtf_api": True})
    assert set(rejected) == {"live_trading_enabled", "expected_static_ip", "allow_mtf_api"}

    # And the live commands still refuse on the environment alone.
    from thunderbot.cli import main

    assert main(["live", "--i-understand-the-risks"]) == 2
    assert main(["invest", "--live", "--i-understand-the-risks"]) == 2


# The rebalance reviewer on an OpenAI-compatible endpoint


def _ctx() -> RebalanceContext:
    return RebalanceContext(strategy="etf_trend", mode="paper", as_of="2026-11-13T15:10:00+05:30", target={"NIFTYBEES": 1.0},
                            orders=[{"symbol": "NIFTYBEES", "side": "BUY", "qty": 10}],
                            facts={"GOLDBEES": {"price": 8.1, "change_1d_pct": -90.0}}, portfolio_value=500_000.0)


def _chat(reply, status: int = 200):
    calls = []

    def post(url, body):
        calls.append(body)
        if status != 200:
            return status, {"error": {"message": "upstream is down"}}
        text = reply if isinstance(reply, str) else json.dumps(reply)
        return 200, {"id": "r1", "model": "served-model", "choices": [{"message": {"content": text}}],
                     "usage": {"prompt_tokens": 800, "completion_tokens": 40}}

    return ChatClient("k", "https://api.groq.com/openai/v1", "m", post=post), calls


def test_chat_rebalance_reviewer_approves_and_postpones(tmp_path, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    s = Settings(data_dir=str(tmp_path), llm_enabled=True)
    client, calls = _chat({"decision": "approve", "confidence": 0.9, "rationale": "Orders match the target.", "risk_flags": []})
    v = ChatRebalanceReviewer(s, client).review(_ctx())
    assert v.approve and v.error is None and v.model == "served-model" and v.input_tokens == 800
    system = calls[0]["messages"][0]["content"]
    assert "quality control, not forecasting" in system and '"decision": "approve" or "postpone"' in system
    assert '"change_1d_pct": -90.0' in calls[0]["messages"][1]["content"]

    client, _ = _chat('```json\n{"decision": "postpone", "confidence": 2, "rationale": "GOLDBEES fell 90% in a day: a unit '
                      'split, not a crash.", "risk_flags": "possible_split"}\n```')
    v = ChatRebalanceReviewer(s, client).review(_ctx())
    assert v.approve is False and v.confidence == 1.0 and v.risk_flags == ["possible_split"] and v.rationale.startswith("GOLDBEES")


def test_chat_rebalance_reviewer_failure_lets_the_rule_proceed(tmp_path, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda s: None)
    s = Settings(data_dir=str(tmp_path), llm_enabled=True)
    for client, _ in (_chat("", status=500), _chat("no json here"), _chat({"decision": "sell everything"})):
        v = ChatRebalanceReviewer(s, client).review(_ctx())
        assert v.approve is True and v.error and "llm_error" in v.risk_flags and "the rule proceeds" in v.rationale


# The read-only Groww check


class FakeSession:
    def __init__(self, api_key, totp_secret=None, api_secret=None, cache_path=None):
        self.args = (api_key, totp_secret, api_secret)

    def token(self, force_refresh=False):
        FakeSession.fresh = force_refresh
        return "access-token-value", True


class FakeGroww:
    placed = 0

    def __init__(self, token):
        self.token = token

    def get_user_profile(self):
        return {"ucc": "X"}

    def get_ltp(self, exchange_trading_symbols, segment):
        return {"NSE_RELIANCE": 1234.5}

    def place_order(self, **kw):  # must never be reached
        FakeGroww.placed += 1


def _runner(tmp_path, **secrets) -> JobRunner:
    return JobRunner(CompositeStore(store_with(tmp_path, **secrets)), Settings(data_dir=str(tmp_path / "var")))


def test_groww_check_job_ok(tmp_path, monkeypatch):
    monkeypatch.setenv("TB_SECRET_KEY", MASTER)
    key = fake_groww_key("auth-totp")
    r = _runner(tmp_path, groww={"api_key": key, "totp_secret": "JBSWY3DPEHPK3PXP"})
    r.store.insert("jobs", {"id": "g1", "kind": "groww_check", "status": "queued", "params": {"fresh": True}})
    result = r.groww_check({"fresh": True}, lambda p: None, session_factory=FakeSession, client_factory=FakeGroww,
                           missing=lambda: [], public_ip=lambda: "203.0.113.9")
    assert result["ok"] and [s["name"] for s in result["steps"]] == ["Key", "SDK", "Login", "Profile", "Live data"]
    assert all(s["ok"] for s in result["steps"]) and FakeSession.fresh is True and FakeGroww.placed == 0
    assert result["ip"] == {"observed": "203.0.113.9", "expected": None, "ok": False}
    assert r.store.get_control()["groww_check"] == result
    dumped = json.dumps(result)
    assert key not in dumped and "JBSWY3DPEHPK3PXP" not in dumped and "access-token-value" not in dumped


def test_groww_check_runs_through_the_job_queue(tmp_path, monkeypatch):
    monkeypatch.setenv("TB_SECRET_KEY", MASTER)
    r = _runner(tmp_path)  # nothing saved, nothing in the environment
    r.store.insert("jobs", {"id": "g2", "kind": "groww_check", "status": "queued", "params": {}})
    monkeypatch.setattr("thunderbot.compliance.public_ip", lambda timeout=5.0: None)
    assert r.run_once() == "g2"
    job = r.store.select("jobs", {"id": "g2"})[0]
    assert job["status"] == "done" and job["result"]["ok"] is False and job["result"]["ip"] is None
    assert job["result"]["steps"] == [{"name": "Key", "ok": False, "detail": "No Groww API key is saved in Setup or set as GROWW_API_KEY."}]


def test_groww_check_bad_totp_and_missing_package():
    key = fake_groww_key("auth-totp")
    bad = login_check(key, "this-is-an-api-secret!", None, public_ip=lambda: None, missing=lambda: [])
    assert not bad["ok"] and bad["steps"][0]["name"] == "Key" and "base32" in bad["steps"][0]["detail"]
    assert len(bad["steps"]) == 1

    absent = login_check(key, "JBSWY3DPEHPK3PXP", None, public_ip=lambda: None, missing=lambda: ["growwapi", "pyotp"],
                         session_factory=FakeSession)
    assert not absent["ok"] and [s["name"] for s in absent["steps"]] == ["Key", "SDK"]
    assert "not installed" in absent["steps"][1]["detail"] and "static IP" in absent["steps"][1]["detail"]


def test_groww_check_reports_login_failure_without_leaking(tmp_path):
    key, secret = fake_groww_key("auth-approval"), "api-secret-value-123"

    class Refused(FakeSession):
        def token(self, force_refresh=False):
            raise RuntimeError(f"401 for key {key} secret {secret}")

    out = login_check(key, None, secret, session_factory=Refused, missing=lambda: [], public_ip=lambda: "198.51.100.7",
                      expected_ip="198.51.100.7, 198.51.100.8")
    assert not out["ok"] and out["steps"][-1]["name"] == "Login" and "[hidden]" in out["steps"][-1]["detail"]
    assert key not in json.dumps(out) and secret not in json.dumps(out)
    assert out["ip"] == {"observed": "198.51.100.7", "expected": "198.51.100.7, 198.51.100.8", "ok": True}

    class ShapeProblem(FakeSession):
        def __init__(self, *a, **k):
            raise BrokerError("set GROWW_TOTP_SECRET (TOTP flow) or GROWW_API_SECRET (daily-approval flow)")

    assert login_check(key, None, None, session_factory=ShapeProblem, public_ip=lambda: None)["steps"][0]["ok"] is False

    class NoData(FakeGroww):
        def get_ltp(self, exchange_trading_symbols, segment):
            raise RuntimeError("subscription required")

    partial = login_check(key, None, secret, session_factory=FakeSession, client_factory=NoData, missing=lambda: [],
                          public_ip=lambda: None)
    assert partial["ok"] and partial["steps"][-1] == {"name": "Live data", "ok": False, "detail": partial["steps"][-1]["detail"]}


def test_token_cache_is_tied_to_the_key(tmp_path):
    from thunderbot.broker.groww import GrowwSession
    from thunderbot.clock import now_ist

    cache = tmp_path / "groww_token.json"
    old = GrowwSession(fake_groww_key("auth-approval"), api_secret="s", cache_path=cache)
    cache.write_text(json.dumps({"token": "tok-old", "issued_at": now_ist().isoformat(), "key": old._fingerprint()}))
    assert old._load_cached(now_ist()) == "tok-old"
    new = GrowwSession(fake_groww_key("auth-approval") + "x", api_secret="s", cache_path=cache)
    assert new._load_cached(now_ist()) is None  # a token issued for another key is not reused
    cache.write_text(json.dumps({"token": "tok-legacy", "issued_at": now_ist().isoformat()}))
    assert new._load_cached(now_ist()) == "tok-legacy"  # caches written before this field existed still work


# The local API


@pytest.fixture
def server(tmp_path, monkeypatch):
    from http.server import ThreadingHTTPServer

    monkeypatch.setenv("TB_SECRET_KEY", MASTER)
    store = SQLiteStore(tmp_path / "j.sqlite3")
    api = LocalAPI(store, Settings(data_dir=str(tmp_path)), "k3y")
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(api))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}", store
    httpd.shutdown()


def _call(base, method, path, body=None, key="k3y", prefer=None):
    headers = {"apikey": key, "Content-Type": "application/json", **({"Prefer": prefer} if prefer else {})}
    req = urllib.request.Request(base + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as e:
        return e.code, None


def test_local_api_serves_secrets_only_with_the_key(server):
    base, store = server
    row = {"name": "llm", "ciphertext": vault.encrypt(GROQ, MASTER), "hint": "gsk_…oard",
           "meta": {"preset": "groq", "model": GROQ["model"]}, "updated_at": "2026-11-13T10:00:00+05:30"}
    upsert = "return=minimal,resolution=merge-duplicates"
    assert _call(base, "POST", "/rest/v1/secrets", row, key="wrong", prefer=upsert)[0] == 401
    assert _call(base, "GET", "/rest/v1/secrets?select=*", key="")[0] == 401
    assert _call(base, "POST", "/rest/v1/secrets", {"name": "llm"}, prefer=upsert)[0] == 400  # no ciphertext
    assert _call(base, "POST", "/rest/v1/secrets", row, prefer=upsert)[0] == 201

    listed = _call(base, "GET", "/rest/v1/secrets?select=name,hint,meta,updated_at")[1]
    assert listed == [{"name": "llm", "hint": "gsk_…oard", "meta": row["meta"], "updated_at": row["updated_at"]}]
    one = _call(base, "GET", "/rest/v1/secrets?select=ciphertext&name=eq.llm&limit=1")[1]
    assert vault.decrypt(one[0]["ciphertext"], MASTER) == GROQ

    # Saving again replaces the row; the key is in no other table and not in the control rows.
    newer = {**row, "ciphertext": vault.encrypt({**GROQ, "model": "second"}, MASTER), "updated_at": "2026-11-13T11:00:00+05:30"}
    assert _call(base, "POST", "/rest/v1/secrets", newer, prefer=upsert)[0] == 201
    assert len(_call(base, "GET", "/rest/v1/secrets?select=name")[1]) == 1
    control = _call(base, "GET", "/rest/v1/control?select=key,value")[1]
    assert GROQ["api_key"] not in json.dumps(control) and "ciphertext" not in json.dumps(control)
    effective = next(c["value"] for c in control if c["key"] == "effective_settings")
    assert effective["env_only"]["llm_source"] == "dashboard" and effective["env_only"]["llm_model"] == "second"
    assert effective["env_only"]["llm_provider"] == "Groq" and effective["editable"]["llm_enabled"] is True
    assert effective["env_only"]["live_trading_enabled"] is False

    assert _call(base, "DELETE", "/rest/v1/secrets?name=eq.llm")[0] == 204
    assert _call(base, "GET", "/rest/v1/secrets?select=name")[1] == []
    control = _call(base, "GET", "/rest/v1/control?select=key,value")[1]
    effective = next(c["value"] for c in control if c["key"] == "effective_settings")
    assert effective["env_only"]["llm_source"] is None and effective["editable"]["llm_enabled"] is False
    assert store.rows("secrets") == []


# Where saved keys are picked up


def test_the_ai_desk_and_the_cli_pick_up_saved_keys(tmp_path, monkeypatch, capsys):
    from thunderbot.ai.runner import IntradayRunner
    from thunderbot.cli import _stored, main

    monkeypatch.setenv("TB_SECRET_KEY", MASTER)
    monkeypatch.setenv("TB_DATA_DIR", str(tmp_path))
    store = store_with(tmp_path, llm=GROQ)  # the journal a local worker reads
    base = Settings(data_dir=str(tmp_path))

    desk = IntradayRunner(base, CompositeStore(store))
    assert desk._settings({}).llm_api_key == GROQ["api_key"] and desk._settings({}).strategy == "ai"
    assert desk._settings({"settings_overrides": {"llm_enabled": False}}).llm_enabled is False
    store.delete("secrets", ["llm"])
    assert desk._settings({}).llm_api_key is None  # read afresh on every bar

    store.insert("secrets", {"id": "groww", "name": "groww", "updated_at": "2026-11-13T10:00:00+05:30", "hint": "…", "meta": {},
                             "ciphertext": vault.encrypt({"api_key": fake_groww_key("auth-totp"), "totp_secret": "not base32!"}, MASTER)})
    assert _stored(base).groww_source == "dashboard"
    monkeypatch.setattr("thunderbot.compliance.public_ip", lambda timeout=5.0: None)
    assert main(["login-check"]) == 2  # the saved key is the one checked, and its problem is reported
    out = capsys.readouterr().out
    assert "Key: FAILED" in out and "base32" in out and "No orders were placed" in out


def test_serverless_pass_applies_saved_keys(tmp_path, monkeypatch):
    from thunderbot import serverless

    monkeypatch.setenv("TB_SECRET_KEY", MASTER)
    store = CompositeStore(store_with(tmp_path, llm=GROQ))
    seen = {}

    def fake_runner(settings, store, scheduler="serverless"):
        seen["invest"] = settings

        class R:
            def tick(self):
                return {"did": "nothing"}
        return R()

    monkeypatch.setattr(serverless, "build_runner", fake_runner)
    monkeypatch.setattr(serverless, "run_intraday", lambda s, st: seen.setdefault("desk", s) and {"intraday": "off"})
    monkeypatch.setattr(serverless, "run_jobs", lambda s, st, deadline, job_id=None: [])
    status, body = serverless.handle("tick", settings=Settings(data_dir=str(tmp_path)), store=store)
    assert status == 200 and body["ok"]
    assert seen["invest"].llm_api_key == GROQ["api_key"] and seen["desk"].llm_source == "dashboard"
    published = store.get_control()["effective_settings"]["env_only"]
    assert published["llm_source"] == "dashboard" and published["llm_provider"] == "Groq"
    assert GROQ["api_key"] not in json.dumps(store.get_control())
