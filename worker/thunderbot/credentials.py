"""Apply the keys saved from the dashboard on top of the environment.

``apply_credentials`` is called wherever a worker starts a pass. Saved keys win over environment
keys; with nothing saved the environment is used as before. It can be called again on its own
result: it always starts from the environment's values, so a key cleared in the dashboard stops
being used on the next pass.

What a saved secret can change is an explicit list: the LLM provider, key and model, and the Groww
login credentials. It cannot turn on real orders. ``TB_LIVE_TRADING_ENABLED``,
``TB_EXPECTED_STATIC_IP``, ``TB_ALLOW_MTF_API`` and the ``--i-understand-the-risks`` flag are read
from the worker's own environment and command line and nowhere else.
"""

from __future__ import annotations

import dataclasses
import os
from collections.abc import Mapping
from typing import Any

from .config import Settings
from .llm.provider import stored_llm_fields
from .secrets import read_secret

# The only Settings fields a saved secret may set.
LLM_FIELDS = ("llm_enabled", "llm_model", "llm_api_key", "llm_base_url", "llm_chat_model", "anthropic_api_key",
              "llm_source", "llm_preset")
GROWW_FIELDS = ("groww_api_key", "groww_totp_secret", "groww_api_secret", "groww_source")
CREDENTIAL_FIELDS = LLM_FIELDS + GROWW_FIELDS


def stored_groww_fields(secret: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(secret, Mapping):
        return None
    key = str(secret.get("api_key") or "").strip()
    if not key:
        return None
    return {"groww_api_key": key, "groww_totp_secret": str(secret.get("totp_secret") or "").strip() or None,
            "groww_api_secret": str(secret.get("api_secret") or "").strip() or None, "groww_source": "dashboard"}


def apply_credentials(settings: Settings, store: Any, env: Mapping[str, str] | None = None) -> Settings:
    """A copy of ``settings`` with saved LLM and Groww keys applied. Never raises: an unreadable secret
    is logged (without its contents) and the environment's value stands."""
    env = os.environ if env is None else env
    base = settings.env_credentials or {k: getattr(settings, k) for k in CREDENTIAL_FIELDS}
    changes: dict[str, Any] = dict(base)
    llm = stored_llm_fields(read_secret(store, "llm", env), env)
    if llm:
        changes.update({k: v for k, v in llm.items() if k in LLM_FIELDS})
    groww = stored_groww_fields(read_secret(store, "groww", env))
    if groww:
        changes.update({k: v for k, v in groww.items() if k in GROWW_FIELDS})
    return dataclasses.replace(settings, **changes, env_credentials=dict(base))
