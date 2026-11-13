"""The LLM as the desk's trader: it takes or skips each setup the model let through, and may shrink it.

Works with any OpenAI-compatible chat-completions endpoint (xAI Grok, Groq, OpenAI, OpenRouter, a local
server), using ``requests`` only. Configure LLM_API_KEY, LLM_BASE_URL and LLM_MODEL.

The contract is the same as the Claude reviewer's: the reply can approve or reject a signal and set a
size multiplier between 0 and 1. It never sets a price, never creates a trade, never enlarges one, and
``RiskManager`` runs after it. Its prompt and reply are journalled with every decision.

The prompt is a file in the harness (``roles/trader.md``); this module keeps the message the trader is
shown and the HTTP client. Every call goes through ``llm.adapter``.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from ..config import Settings
from .filter import RoleFilter
from .types import ReviewContext

log = logging.getLogger(__name__)

def provider_of(base_url: str | None) -> str:
    host = re.sub(r"^https?://", "", (base_url or "").strip()).split("/")[0].lower()
    for key, name in (("x.ai", "xAI"), ("groq", "Groq"), ("openai", "OpenAI"), ("openrouter", "OpenRouter"),
                      ("anthropic", "Anthropic"), ("googleapis", "Google"), ("deepseek", "DeepSeek"),
                      ("localhost", "local"), ("127.0.0.1", "local")):
        if key in host:
            return name
    return host or "none"


def build_trader_message(ctx: ReviewContext) -> str:
    sig = ctx.signal
    f = dict(sig.features)
    x = f.pop("x", {}) or {}
    payload: dict[str, Any] = {
        "setup": {
            "symbol": sig.symbol, "side": sig.side.value, "kind": f.get("generator", sig.strategy),
            "time_ist": sig.ts.strftime("%Y-%m-%d %H:%M"), "entry": sig.entry, "stop": sig.stop, "target": sig.target,
            "stop_distance_pct": round(sig.risk_per_share / sig.entry * 100, 2) if sig.entry else None,
            "reward_to_risk": round(sig.reward_risk, 2), "why": sig.reason,
        },
        "ml": {"prob": f.get("ml_prob"), "expected_r": f.get("ml_expected_r"), **(ctx.extra.get("ml") or {})},
        "stock_now": {k: x.get(k) for k in ("ret_open", "ret_6", "gap", "vwap_dist_atr", "atr_pct", "range_pos", "rvol",
                                            "cum_rvol", "rsi", "rel_strength", "trend_bars") if k in x},
        "stock_now_note": "returns in %, signed so that positive means in the direction of this trade",
        "market": ctx.extra.get("market") or {},
        "recent_bars": [{"t": b.ts.strftime("%H:%M"), "o": round(b.open, 2), "h": round(b.high, 2), "l": round(b.low, 2),
                         "c": round(b.close, 2), "v": int(b.volume)} for b in ctx.recent_bars],
        "account_today": {"realized_pnl": round(ctx.day_realized_pnl, 2), "trades_opened": ctx.trades_today,
                          "open_positions": ctx.open_positions},
        "lessons": ctx.extra.get("lessons") or [],
        "notes": ctx.market_notes,
    }
    return "Decide on this setup.\n\n" + json.dumps(payload, indent=1, default=str)


def extract_json(text: str) -> dict[str, Any]:
    """The first JSON object in a reply, tolerating code fences and stray prose around it."""
    text = (text or "").strip()
    try:
        out = json.loads(text)
        if isinstance(out, dict):
            return out
    except json.JSONDecodeError:
        pass
    start = text.find("{")
    while start >= 0:
        depth = 0
        for i in range(start, len(text)):
            depth += text[i] == "{"
            depth -= text[i] == "}"
            if depth == 0:
                try:
                    out = json.loads(text[start:i + 1])
                    if isinstance(out, dict):
                        return out
                except json.JSONDecodeError:
                    pass
                break
        start = text.find("{", start + 1)
    raise ValueError("no JSON object in the reply")


class ChatClient:
    """Minimal OpenAI-compatible chat-completions client."""

    def __init__(self, api_key: str, base_url: str, model: str, timeout: float = 30.0, post=None) -> None:
        self.api_key, self.model, self.timeout = api_key, model, timeout
        self.url = base_url.rstrip("/") + ("" if base_url.rstrip("/").endswith("/chat/completions") else "/chat/completions")
        self._post = post

    def _send(self, body: dict[str, Any]) -> tuple[int, dict[str, Any] | str]:
        if self._post is not None:
            return self._post(self.url, body)
        import requests

        r = requests.post(self.url, json=body, timeout=self.timeout,
                          headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"})
        try:
            return r.status_code, r.json()
        except ValueError:
            return r.status_code, r.text[:300]

    def complete(self, system: str, user: str, max_tokens: int = 700) -> tuple[str, dict[str, Any]]:
        """Returns (reply text, raw response). Raises RuntimeError with the provider's message on failure."""
        body: dict[str, Any] = {
            "model": self.model, "temperature": 0.2, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "response_format": {"type": "json_object"},
        }
        last = ""
        for attempt in range(3):
            status, data = self._send(body)
            if status == 200 and isinstance(data, dict):
                choices = data.get("choices") or []
                text = ((choices[0].get("message") or {}).get("content") if choices else None) or ""
                return text, data
            err = data.get("error") if isinstance(data, dict) else data
            last = f"HTTP {status}: {(err.get('message') if isinstance(err, dict) else err) or 'no message'}"
            if status == 400 and "response_format" in body:
                body.pop("response_format")  # some servers do not offer JSON mode; the prompt asks for JSON anyway
                continue
            if status == 400 and "max_tokens" in body:
                body["max_completion_tokens"] = body.pop("max_tokens")  # newer OpenAI models renamed it
                body.pop("temperature", None)
                continue
            if status in (429, 500, 502, 503, 504) and attempt < 2:
                time.sleep(1.5 * (attempt + 1))
                continue
            break
        raise RuntimeError(last)


class ChatSignalFilter(RoleFilter):
    """The desk's trader through any OpenAI-compatible chat endpoint."""

    def __init__(self, settings: Settings, client: ChatClient | None = None, role: str = "trader") -> None:
        super().__init__(settings, role, client, family="chat")


def __getattr__(name: str) -> Any:
    # The prompt lives in the harness now (roles/trader.md); the old name still reads it.
    if name == "TRADER_PROMPT":
        from .. import harness

        return harness.current().prompt("trader")
    raise AttributeError(name)
