"""Optional reviewer for the daily strategies' rebalances.

What it is for. The evidence (see reports/) does not support an LLM forecasting prices for a small
account, so this reviewer makes no market calls. It reads the orders a mechanical rule is about to
place and the prices behind them, and looks for the things rules miss: a price series that looks
broken, an order list that does not match the stated target, a rebalance that sells nearly everything
on a single odd print. It may approve the plan or postpone it by one session. It cannot change,
add or enlarge an order, and after ``max_delays`` postponements the rule runs regardless, so a
confused or unavailable model can never keep the account out of the market for long.

Every verdict is journalled with its prompt, so its postponements can be scored later against what
the rule would have earned without them.

The prompt is a file in the harness (``roles/rebalance_reviewer.md``); every call goes through
``llm.adapter``.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from ..config import Settings

log = logging.getLogger(__name__)

@dataclass
class RebalanceContext:
    """Everything the reviewer is shown. Point-in-time data only."""

    strategy: str
    mode: str
    as_of: str
    target: dict[str, float]
    orders: list[dict[str, Any]]
    facts: dict[str, dict[str, Any]]
    portfolio_value: float
    delays_used: int = 0
    max_delays: int = 2


@dataclass
class RebalanceVerdict:
    approve: bool
    confidence: float
    rationale: str
    risk_flags: list[str] = field(default_factory=list)
    model: str = ""
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    error: str | None = None
    prompt: str = ""
    role: str = "rebalance_reviewer"
    harness_id: str = ""  # the harness the reviewer ran under
    cost_inr: float = 0.0  # what the call cost, from the prices in the harness's policy

    @classmethod
    def failed(cls, error: str, model: str, prompt: str = "") -> "RebalanceVerdict":
        # A reviewer that cannot answer approves: the mechanical rule is the system, the review is an extra.
        return cls(True, 0.0, f"review unavailable ({error}); the rule proceeds", ["llm_error"], model=model,
                   error=error, prompt=prompt)


def build_user_message(ctx: RebalanceContext) -> str:
    payload = {
        "as_of": ctx.as_of, "strategy": ctx.strategy, "mode": ctx.mode,
        "portfolio_value_inr": ctx.portfolio_value,
        "target_weights": {s: round(w, 4) for s, w in ctx.target.items()},
        "orders": ctx.orders,
        "price_facts": ctx.facts,
        "postponements_used": f"{ctx.delays_used} of {ctx.max_delays}",
    }
    return "Review this rebalance.\n\n" + json.dumps(payload, indent=1, default=str)


class RebalanceReviewer:
    """Asks the rebalance role through the one adapter. A reviewer that cannot answer approves, because
    the mechanical rule is the system and the review is an extra."""

    def __init__(self, settings: Settings, client: Any | None = None, family: str | None = None) -> None:
        from .adapter import ModelAdapter

        self.s = settings
        self.adapter = ModelAdapter(settings, client, family)
        self.client = self.adapter.client

    @property
    def label(self) -> str:
        return self.adapter.model

    def review(self, ctx: RebalanceContext) -> RebalanceVerdict:
        reply = self.adapter.ask("rebalance_reviewer", build_user_message(ctx))
        if reply.data is None:
            v = RebalanceVerdict.failed(reply.error or "no reply", self.adapter.model, reply.prompt)
            v.harness_id = reply.harness_id
            return v
        out = reply.data
        return RebalanceVerdict(
            approve=out["approve"], confidence=out["confidence"], rationale=out["rationale"], risk_flags=out["risk_flags"],
            model=reply.model, latency_ms=reply.latency_ms, input_tokens=reply.input_tokens, output_tokens=reply.output_tokens,
            prompt=reply.prompt, harness_id=reply.harness_id, cost_inr=reply.cost_inr,
        )


class ClaudeRebalanceReviewer(RebalanceReviewer):
    """The review through Anthropic's API."""

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        super().__init__(settings, client, family="anthropic")


class ChatRebalanceReviewer(RebalanceReviewer):
    """The same review through any OpenAI-compatible chat endpoint (xAI Grok, Groq, OpenAI, Gemini,
    OpenRouter, a local server). Same prompt, same contract: approve or postpone."""

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        super().__init__(settings, client, family="chat")


def build_rebalance_reviewer(settings: Settings) -> RebalanceReviewer | None:
    """The configured LLM when it is enabled: an OpenAI-compatible endpoint, or Claude when an Anthropic
    credential and the SDK are present. Otherwise no reviewer."""
    import os

    if not settings.llm_enabled:
        return None
    if settings.chat_llm:
        return ChatRebalanceReviewer(settings)
    if not (settings.anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        log.warning("the LLM is enabled but no key is configured; rebalance review is off")
        return None
    try:
        return ClaudeRebalanceReviewer(settings)
    except ImportError:
        log.warning("TB_LLM_ENABLED is set but the anthropic package is not installed; rebalance review is off")
        return None


def __getattr__(name: str) -> Any:
    # The prompt lives in the harness now (roles/rebalance_reviewer.md); the old names still read it.
    if name == "SYSTEM_PROMPT":
        from .. import harness

        return harness.current().prompt("rebalance_reviewer")
    if name == "JSON_REPLY":
        from .adapter import CONTRACTS

        return CONTRACTS["rebalance_reviewer"].json_hint
    raise AttributeError(name)
