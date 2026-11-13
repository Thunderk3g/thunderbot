"""Which LLM the worker uses, and where that choice came from.

Two families cover every provider: Anthropic's own API (through the ``anthropic`` SDK) and the
OpenAI-compatible chat-completions protocol (xAI Grok, Groq, OpenAI, Gemini, OpenRouter, a local
server), reached with ``ChatClient``. A key saved from the dashboard's setup screen wins over the
environment (``LLM_API_KEY`` / ``LLM_BASE_URL`` / ``LLM_MODEL``, or ``ANTHROPIC_API_KEY`` with
``TB_LLM_MODEL``). ``TB_LLM_ENABLED=false`` switches every LLM role off whichever key is present.

Model names are never hardcoded here: the setup screen lists them from the provider.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

ANTHROPIC = "anthropic"
OPENAI_COMPATIBLE = "openai_compatible"

# Base URLs for the setup screen's presets; mirrored in dashboard/lib/setup.ts.
PRESETS: dict[str, tuple[str, str]] = {
    "anthropic": (ANTHROPIC, "https://api.anthropic.com"),
    "xai": (OPENAI_COMPATIBLE, "https://api.x.ai/v1"),
    "groq": (OPENAI_COMPATIBLE, "https://api.groq.com/openai/v1"),
    "openai": (OPENAI_COMPATIBLE, "https://api.openai.com/v1"),
    "gemini": (OPENAI_COMPATIBLE, "https://generativelanguage.googleapis.com/v1beta/openai"),
    "openrouter": (OPENAI_COMPATIBLE, "https://openrouter.ai/api/v1"),
    "custom": (OPENAI_COMPATIBLE, ""),
}


def _truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes", "on")


def stored_llm_fields(secret: Mapping[str, Any] | None, env: Mapping[str, str]) -> dict[str, Any] | None:
    """Settings fields for a saved ``llm`` secret, or None when it is absent or incomplete.

    Only the LLM fields are returned, whatever else the secret contains.
    """
    if not isinstance(secret, Mapping):
        return None
    provider = str(secret.get("provider") or "").strip()
    key = str(secret.get("api_key") or "").strip()
    model = str(secret.get("model") or "").strip()
    preset = str(secret.get("preset") or "").strip() or ("anthropic" if provider == ANTHROPIC else "custom")
    if not key or not model or provider not in (ANTHROPIC, OPENAI_COMPATIBLE):
        return None
    switch = (env.get("TB_LLM_ENABLED") or "").strip()
    enabled = _truthy(switch) if switch else True  # a saved key turns the LLM on unless the off switch is set
    if provider == ANTHROPIC:
        return {"llm_enabled": enabled, "llm_model": model, "anthropic_api_key": key, "llm_api_key": None,
                "llm_base_url": None, "llm_chat_model": None, "llm_source": "dashboard", "llm_preset": preset}
    base_url = str(secret.get("base_url") or "").strip() or PRESETS.get(preset, ("", ""))[1]
    if not base_url:
        return None
    return {"llm_enabled": enabled, "llm_api_key": key, "llm_base_url": base_url, "llm_chat_model": model,
            "llm_source": "dashboard", "llm_preset": preset}


def anthropic_client(settings: Any):
    """An Anthropic SDK client. A key saved from the dashboard is passed explicitly; otherwise the SDK
    finds its own credential (``ANTHROPIC_API_KEY`` and the rest of its usual chain)."""
    import anthropic

    return anthropic.Anthropic(api_key=settings.anthropic_api_key or None, timeout=settings.llm_timeout_seconds,
                               max_retries=2)
