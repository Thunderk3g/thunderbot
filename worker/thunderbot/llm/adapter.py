"""One way to ask a model anything, for every role.

A role is a prompt file in the harness plus a contract kept here in code: which decisions it may
return and what shape the reply must have. The adapter takes a role and a message, sends it through
one of two clients (Anthropic's SDK, or any OpenAI-compatible chat endpoint), checks the reply against
the contract, and returns it with the model's own id, the tokens used, the time taken, what the call
cost and the harness it ran under. There is no routing library and no third client.

What a role may *do* with its reply is not decided here. A trade role's answer is clamped again by
``RiskManager``; the rebalance role can only postpone. The contract only makes sure a reply that
reaches them is well formed, and that a role limited to "veto" in its file cannot shrink.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from .. import harness as harness_mod

log = logging.getLogger(__name__)

ANTHROPIC, CHAT = "anthropic", "chat"


@dataclass(frozen=True)
class Contract:
    role: str
    decisions: tuple[str, ...]  # the words the role may answer with; () for a role that makes no decision
    aliases: dict[str, str] = field(default_factory=dict)
    yes: str = ""  # the decision that lets the trade or plan through
    has_size: bool = False
    # Appended to the prompt for chat endpoints when the prompt file does not itself ask for JSON.
    # The Anthropic path does not need it: the reply's shape is enforced by the API.
    json_hint: str = ""
    chat_max_tokens: int | None = None

    def describe(self) -> str:
        return " or ".join(self.decisions)


_REVIEW_HINT = """

Reply with one JSON object and nothing else:
{"decision": "approve" or "reject", "size_multiplier": 0.0 to 1.0, "confidence": 0.0 to 1.0,
 "rationale": "two to four plain sentences", "risk_flags": ["short_snake_case_tags"]}
"""
_REBALANCE_HINT = """

Reply with one JSON object and nothing else:
{"decision": "approve" or "postpone", "confidence": 0.0 to 1.0,
 "rationale": "two to four plain sentences", "risk_flags": ["short_snake_case_tags"]}
"""

CONTRACTS: dict[str, Contract] = {
    "trader": Contract("trader", ("take", "skip"), {"approve": "take", "reject": "skip"}, yes="take", has_size=True),
    "signal_reviewer": Contract("signal_reviewer", ("approve", "reject"), {"take": "approve", "skip": "reject"},
                                yes="approve", has_size=True, json_hint=_REVIEW_HINT),
    "rebalance_reviewer": Contract("rebalance_reviewer", ("approve", "postpone"), yes="approve", json_hint=_REBALANCE_HINT),
    "day_reviewer": Contract("day_reviewer", (), chat_max_tokens=600),
}


@dataclass
class Reply:
    """What came back from one call. ``data`` is None when the call failed; ``error`` then says why."""

    role: str
    data: dict[str, Any] | None
    model: str
    prompt: str
    harness_id: str
    error: str | None = None
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    request_id: str | None = None
    cost_inr: float = 0.0

    @property
    def ok(self) -> bool:
        return self.data is not None


def _clamp01(value: Any, default: float) -> float:
    return min(max(float(default if value is None else value), 0.0), 1.0)


def _flags(value: Any) -> list[str]:
    items = value if isinstance(value, list) else [value] if value else []
    return [str(x).strip() for x in items if str(x).strip()][:10]


def validate(contract: Contract, raw: dict[str, Any], may: str) -> dict[str, Any]:
    """Check a reply against its role's contract and return it in one fixed shape. Raises ValueError."""
    if not contract.decisions:  # the end-of-day reviewer: free text only
        return {"summary": str(raw.get("summary", "")).strip()[:900],
                "lessons": [str(x).strip()[:240] for x in (raw.get("lessons") or []) if str(x).strip()][:4]}
    decision = str(raw.get("decision", "")).strip().lower()
    decision = contract.aliases.get(decision, decision)
    if decision not in contract.decisions:
        raise ValueError(f"decision must be {contract.describe()}, got {str(raw.get('decision', '')).strip().lower()!r}")
    approve = decision == contract.yes
    out: dict[str, Any] = {
        "decision": decision, "approve": approve, "confidence": _clamp01(raw.get("confidence"), 0.5),
        "rationale": (str(raw.get("rationale") or "").strip() or "(no rationale given)")[:1200],
        "risk_flags": _flags(raw.get("risk_flags")),
    }
    if contract.has_size:
        size = _clamp01(raw.get("size_multiplier"), 1.0 if approve else 0.0) if approve else 0.0
        if approve and may == "veto":
            size = 1.0  # this role's file limits it to take-or-skip
        out["size_multiplier"] = size
    return out


def _output_model(contract: Contract):
    """The reply's shape for Anthropic's structured output."""
    from typing import Literal

    from pydantic import BaseModel

    if not contract.decisions:
        class DayReview(BaseModel):
            summary: str
            lessons: list[str]

        return DayReview
    words = Literal[contract.decisions]  # type: ignore[valid-type]
    if contract.has_size:
        class ReviewOutput(BaseModel):
            decision: words  # type: ignore[valid-type]
            size_multiplier: float
            confidence: float
            rationale: str
            risk_flags: list[str]

        return ReviewOutput

    class RebalanceReview(BaseModel):
        decision: words  # type: ignore[valid-type]
        confidence: float
        rationale: str
        risk_flags: list[str]

    return RebalanceReview


class ModelAdapter:
    """Asks the configured model on behalf of a role. ``family`` picks the client; by default it is the
    OpenAI-compatible endpoint when one is fully configured, else Anthropic's API."""

    def __init__(self, settings: Any, client: Any | None = None, family: str | None = None) -> None:
        self.s = settings
        self.family = family or (CHAT if settings.chat_llm else ANTHROPIC)
        if client is None:
            if self.family == CHAT:
                from .trader import ChatClient

                client = ChatClient(settings.llm_api_key or "", settings.llm_base_url or "", settings.llm_chat_model or "",
                                    timeout=min(settings.llm_timeout_seconds, 45.0))
            else:
                from .provider import anthropic_client

                client = anthropic_client(settings)
        self.client = client
        self._models: dict[str, Any] = {}

    @property
    def model(self) -> str:
        """The model asked for. The id the provider answers with is on each ``Reply``."""
        return self.client.model if self.family == CHAT else self.s.llm_model

    def ask(self, role: str, user: str) -> Reply:
        h = harness_mod.current()
        contract = CONTRACTS[role]
        system = h.prompt(role)
        started = time.monotonic()
        reply = self._chat(contract, system, user, h) if self.family == CHAT else self._anthropic(contract, system, user, h)
        reply.latency_ms = reply.latency_ms or int((time.monotonic() - started) * 1000)
        reply.cost_inr = h.cost_inr(reply.input_tokens, reply.output_tokens)
        return reply

    # The two clients

    def _chat(self, contract: Contract, system: str, user: str, h: Any) -> Reply:
        from .trader import extract_json

        model = self.client.model
        reply = Reply(contract.role, None, model, user, h.id)
        raw: dict[str, Any] = {}
        try:
            kwargs = {"max_tokens": contract.chat_max_tokens} if contract.chat_max_tokens else {}
            text, raw = self.client.complete(system + contract.json_hint, user, **kwargs)
            reply.data = validate(contract, extract_json(text), h.may(contract.role))
        except Exception as e:
            log.warning("%s: the model call failed: %s", contract.role, e)
            reply.error = f"{type(e).__name__}: {e}"[:300]
        usage = (raw or {}).get("usage") or {}
        reply.model = str((raw or {}).get("model") or model)
        reply.input_tokens = int(usage.get("prompt_tokens") or 0)
        reply.output_tokens = int(usage.get("completion_tokens") or 0)
        reply.request_id = (raw or {}).get("id")
        return reply

    def _anthropic(self, contract: Contract, system: str, user: str, h: Any) -> Reply:
        import anthropic

        model = self.s.llm_model
        reply = Reply(contract.role, None, model, user, h.id)
        if contract.role not in self._models:
            self._models[contract.role] = _output_model(contract)
        started = time.monotonic()
        try:
            response = self.client.beta.messages.parse(
                model=model,
                max_tokens=16000,
                system=system,
                messages=[{"role": "user", "content": user}],
                output_format=self._models[contract.role],
                output_config={"effort": self.s.llm_effort},
                # On a safety decline, re-run on Anthropic's recommended fallback model.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except anthropic.RateLimitError as e:
            reply.error = f"rate_limited: {e.message}"
            return reply
        except anthropic.APIStatusError as e:
            reply.error = f"api_error_{e.status_code}: {e.message}"
            return reply
        except anthropic.APIConnectionError as e:
            reply.error = f"connection_error: {e}"
            return reply
        except Exception as e:  # validation errors from parse, etc.
            log.exception("%s: the model call failed", contract.role)
            reply.error = f"{type(e).__name__}: {e}"
            return reply
        reply.latency_ms = int((time.monotonic() - started) * 1000)
        usage = getattr(response, "usage", None)
        reply.request_id = getattr(response, "_request_id", None)
        reply.input_tokens = getattr(usage, "input_tokens", 0) or 0
        reply.output_tokens = getattr(usage, "output_tokens", 0) or 0
        if response.stop_reason == "refusal":
            category = getattr(getattr(response, "stop_details", None), "category", None)
            reply.error = f"refusal ({category})"
            return reply
        out = response.parsed_output
        if out is None:
            reply.error = f"no parsed output (stop_reason={response.stop_reason})"
            return reply
        served = getattr(response, "model", model)
        reply.model = served if isinstance(served, str) and served else model
        fields = ("summary", "lessons") if not contract.decisions else ("decision", "size_multiplier", "confidence", "rationale", "risk_flags")
        try:
            reply.data = validate(contract, {k: getattr(out, k) for k in fields if hasattr(out, k)}, h.may(contract.role))
        except Exception as e:
            reply.error = f"{type(e).__name__}: {e}"
        return reply


def configured(settings: Any) -> bool:
    """True when a model can be asked: the LLM is switched on and one of the two clients has a key."""
    return bool(settings.llm_enabled and (settings.chat_llm or settings.has_anthropic_key))
