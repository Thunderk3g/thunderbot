"""Credential setup checks. Uses fabricated keys only; never real credentials."""

from __future__ import annotations

import base64
import json
import os

import pytest

from thunderbot.broker.base import BrokerError
from thunderbot.broker.groww import GrowwSession, is_base32, key_role
from thunderbot.cli import load_dotenv


def fake_key(role: str) -> str:
    def b64(obj) -> str:
        return base64.urlsafe_b64encode(json.dumps(obj).encode()).decode().rstrip("=")
    return f"{b64({'alg': 'ES256'})}.{b64({'sub': json.dumps({'role': role})})}.c2ln"


def test_key_role_decodes_without_network():
    assert key_role(fake_key("auth-totp")) == "auth-totp"
    assert key_role("not-a-jwt") is None


def test_base32_detection():
    assert is_base32("JBSWY3DPEHPK3PXP")
    assert is_base32("jbsw y3dp ehpk 3pxp")
    assert not is_base32("Xq7mzT3w-not-base32!")


def test_totp_key_rejects_non_base32_secret_with_clear_message():
    with pytest.raises(BrokerError, match="base32"):
        GrowwSession(fake_key("auth-totp"), totp_secret="not&a@totp-secret")
    with pytest.raises(BrokerError, match="TOTP-type key"):
        GrowwSession(fake_key("auth-totp"), api_secret="some-api-secret")


def test_totp_key_with_valid_secret_uses_totp_only():
    s = GrowwSession(fake_key("auth-totp"), totp_secret="JBSWY3DPEHPK3PXP", api_secret="ignored")
    assert s.api_secret is None and s.totp_secret == "JBSWY3DPEHPK3PXP"


def test_approval_key_accepts_api_secret():
    s = GrowwSession(fake_key("auth-approval"), api_secret="s3cret&@")
    assert s.api_secret == "s3cret&@"


def test_dotenv_loads_without_overriding(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# comment\nexport TB_FAKE_A="quoted&@value"\nTB_FAKE_B=plain\nTB_FAKE_C=from-file\n')
    monkeypatch.setenv("TB_FAKE_C", "from-env")
    monkeypatch.delenv("TB_FAKE_A", raising=False)
    monkeypatch.delenv("TB_FAKE_B", raising=False)
    loaded = load_dotenv(env)
    assert os.environ["TB_FAKE_A"] == "quoted&@value" and os.environ["TB_FAKE_B"] == "plain"
    assert os.environ["TB_FAKE_C"] == "from-env" and "TB_FAKE_C" not in loaded
    for k in loaded:
        monkeypatch.delenv(k)


class TestGrowwLink:
    class Session:
        def __init__(self, tokens):
            self.tokens = tokens

        def token(self):
            t = self.tokens.pop(0)
            if isinstance(t, Exception):
                raise t
            return t

    class Client:
        def __init__(self, token):
            self.token = token

        def get_ltp(self, **kw):
            return {"NSE_AAA": 1.0}

    def test_connects_lazily_and_swaps_tokens(self):
        from thunderbot.broker.groww import GrowwLink

        session = self.Session([("t1", True), ("t1", False), ("t2", True)])
        fresh = []
        link = GrowwLink(lambda: session, on_fresh_token=lambda: fresh.append(1), client_factory=self.Client)
        assert link.status()["ok"] is False
        assert link.ensure() is None and link.client.token == "t1"
        assert link.get_ltp() == {"NSE_AAA": 1.0}
        link.ensure()
        link.ensure()
        assert link.client.token == "t2" and len(fresh) == 2
        assert link.status() == {"source": "groww", "ok": True, "message": "connected"}

    def test_login_failure_is_reported_and_retried_after_backoff(self):
        from thunderbot.broker.base import BrokerError
        from thunderbot.broker.groww import GrowwLink

        clock = [0.0]
        attempts = []

        def factory():
            attempts.append(1)
            raise BrokerError("GROWW_TOTP_SECRET is not a valid TOTP secret")

        link = GrowwLink(factory, retry_seconds=300, client_factory=self.Client, monotonic=lambda: clock[0])
        assert "not a valid TOTP secret" in link.ensure()
        assert link.ensure() and len(attempts) == 1  # inside the backoff window: no new attempt
        with pytest.raises(BrokerError):
            link.get_ltp()
        clock[0] = 301
        link.ensure()
        assert len(attempts) == 2
        assert link.status()["ok"] is False and "TOTP" in link.status()["message"]
