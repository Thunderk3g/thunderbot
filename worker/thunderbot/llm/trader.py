"""The LLM as the desk's trader: it takes or skips each setup the model let through, and may shrink it.

Works with any OpenAI-compatible chat-completions endpoint (xAI Grok, Groq, OpenAI, OpenRouter, a local
server), using ``requests`` only. Configure LLM_API_KEY, LLM_BASE_URL and LLM_MODEL.

The contract is the same as the Claude reviewer's: the reply can approve or reject a signal and set a
size multiplier between 0 and 1. It never sets a price, never creates a trade, never enlarges one, and
``RiskManager`` runs after it. Its prompt and reply are journalled with every decision.
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any

from ..config import Settings
from .types import LLMDecision, ReviewContext

log = logging.getLogger(__name__)

TRADER_PROMPT = """\
You are the trader on a small intraday desk in India's NSE cash market. Positions are intraday only (MIS)
and are closed by the desk at 15:05 IST whatever happens.

A quant engine proposes one setup at a time with a fixed entry, stop and target. A machine-learning model
has scored it: "ml.prob" is its estimate that the trade ends in profit after costs, "ml.expected_r" its
expected result in units of risk, and "ml.track_record" says how setups it scored like this one actually
did on days it had not seen. You decide whether the desk takes the trade and at what share of normal size.

Reply with one JSON object and nothing else:
{"decision": "take" or "skip", "size_multiplier": 0.0 to 1.0, "confidence": 0.0 to 1.0,
 "rationale": "two to four plain sentences naming the figures that decided it",
 "risk_flags": ["short_snake_case_tags"]}

What you control: take or skip, and size from 0 to 1 (1 = the desk's normal size; you cannot go above it).
What you do not control: entry, stop, target, order type and timing. Hard limits on daily loss, number of
positions and position size run after you and override you.

How to judge:
- Use only the data in the message. Do not use anything you may know about what this stock or the market
  did after the time shown, and do not assume news that is not shown.
- Charges and slippage cost roughly 0.2% of the position on every round trip. A setup needs a real reason
  to beat that. The track record tells you how often these have; weigh it honestly, including when it is poor.
- For breakouts and momentum, prefer trades in the direction of the market so far today ("market"), with
  volume clearly above normal ("rvol"), not stretched far from VWAP, and with time left before 15:05.
- For reversion setups, prefer a quiet or choppy market and avoid fading a strong one-way day.
- Look at "account_today": after losses today, or with positions already open in the same direction, be
  more selective.
- "lessons" are notes this desk wrote after earlier sessions. Use them when they apply.
- Skip when the picture is mixed. Most days deserve few trades. When a setup is good but has one clear
  concern, take it at reduced size and name the concern in risk_flags.
"""


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


class ChatSignalFilter:
    enabled = True

    def __init__(self, settings: Settings, client: ChatClient | None = None) -> None:
        self.s = settings
        self.client = client or ChatClient(settings.llm_api_key or "", settings.llm_base_url or "",
                                           settings.llm_chat_model or "", timeout=min(settings.llm_timeout_seconds, 45.0))

    @property
    def label(self) -> str:
        return self.client.model

    def review(self, ctx: ReviewContext) -> LLMDecision:
        prompt = build_trader_message(ctx)
        model = self.client.model
        started = time.monotonic()
        try:
            text, raw = self.client.complete(TRADER_PROMPT, prompt)
            out = extract_json(text)
            decision = str(out.get("decision", "")).strip().lower()
            if decision not in ("take", "skip", "approve", "reject"):
                raise ValueError(f"decision must be take or skip, got {decision!r}")
            approve = decision in ("take", "approve")
            size = min(max(float(out.get("size_multiplier", 1.0 if approve else 0.0)), 0.0), 1.0)
            confidence = min(max(float(out.get("confidence", 0.5)), 0.0), 1.0)
            flags = out.get("risk_flags") or []
            flags = [str(x).strip() for x in (flags if isinstance(flags, list) else [flags]) if str(x).strip()][:10]
            rationale = str(out.get("rationale", "")).strip() or "(no rationale given)"
        except Exception as e:
            log.warning("LLM trader failed: %s", e)
            d = LLMDecision.failed(f"{type(e).__name__}: {e}"[:300], self.s.llm_fail_mode, model, prompt)
            d.latency_ms = int((time.monotonic() - started) * 1000)
            return d
        usage = raw.get("usage") or {}
        return LLMDecision(
            approve=approve, size_multiplier=size if approve else 0.0, confidence=confidence, rationale=rationale[:1200],
            risk_flags=flags, model=str(raw.get("model") or model), latency_ms=int((time.monotonic() - started) * 1000),
            input_tokens=int(usage.get("prompt_tokens") or 0), output_tokens=int(usage.get("completion_tokens") or 0),
            request_id=raw.get("id"), prompt=prompt,
        )
