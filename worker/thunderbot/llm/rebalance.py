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
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from ..config import Settings

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You review the orders of a small, rules-based investing account on India's NSE before they are placed.
A mechanical strategy trades a few exchange-traded funds (index, gold and liquid ETFs) about once a
month. It has already decided its target holdings and the whole-share orders that reach them.

Your job is quality control, not forecasting. Studies of language models trading on their own
predictions show no dependable edge, so your opinion of where markets are heading is not wanted and
must not affect your decision. What a careful human checker would catch is wanted:
- a price that looks like a data error rather than a market move (an ETF down 90% in a day is an
  unadjusted unit split, not a crash; a price identical for many sessions is a stale feed),
- orders that do not match the stated target weights or the portfolio value,
- a plan that turns over most of the account when the facts shown give no reason for the rule to do so,
- anything internally inconsistent in the numbers you are given.

What you control: "approve" lets the orders go ahead exactly as listed. "postpone" delays the whole
rebalance to the next session, when the rule decides again on fresh prices. You cannot change, add or
remove an order. Postponing has a cost (the account stays in yesterday's holdings), so use it only for
a specific problem you can point to in the data. A falling or rising market, by itself, is the reason
the rule trades and is never a reason to postpone. If nothing is wrong, approve.

Use only the data in the message. Do not use knowledge of events after the "as_of" time, and do not
assume news that is not shown.

Reply with: decision ("approve" or "postpone"), confidence (0.0 to 1.0), rationale (two to four plain
sentences a human can audit later, naming the exact figures that drove a postponement), and risk_flags
(short snake_case tags such as "possible_split", "stale_price", "orders_mismatch"; empty if none).
"""


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


class ClaudeRebalanceReviewer:
    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.s = settings
        if client is None:
            import anthropic

            client = anthropic.Anthropic(timeout=settings.llm_timeout_seconds, max_retries=2)
        self.client = client
        self._output_model = _output_model()

    @property
    def label(self) -> str:
        return self.s.llm_model

    def review(self, ctx: RebalanceContext) -> RebalanceVerdict:
        import anthropic

        prompt = build_user_message(ctx)
        model = self.s.llm_model
        started = time.monotonic()
        try:
            response = self.client.beta.messages.parse(
                model=model,
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": prompt}],
                output_format=self._output_model,
                output_config={"effort": self.s.llm_effort},
                # On a safety decline, re-run on Anthropic's recommended fallback model.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except anthropic.RateLimitError as e:
            return RebalanceVerdict.failed(f"rate_limited: {e.message}", model, prompt)
        except anthropic.APIStatusError as e:
            return RebalanceVerdict.failed(f"api_error_{e.status_code}: {e.message}", model, prompt)
        except anthropic.APIConnectionError as e:
            return RebalanceVerdict.failed(f"connection_error: {e}", model, prompt)
        except Exception as e:  # validation errors from parse, etc.
            log.exception("rebalance review failed")
            return RebalanceVerdict.failed(f"{type(e).__name__}: {e}", model, prompt)
        latency_ms = int((time.monotonic() - started) * 1000)
        if response.stop_reason == "refusal":
            category = getattr(getattr(response, "stop_details", None), "category", None)
            return RebalanceVerdict.failed(f"refusal ({category})", model, prompt)
        out = response.parsed_output
        if out is None:
            return RebalanceVerdict.failed(f"no parsed output (stop_reason={response.stop_reason})", model, prompt)
        usage = getattr(response, "usage", None)
        return RebalanceVerdict(
            approve=out.decision == "approve",
            confidence=min(max(float(out.confidence), 0.0), 1.0),
            rationale=out.rationale.strip(),
            risk_flags=[f.strip() for f in out.risk_flags if f.strip()][:10],
            model=getattr(response, "model", model), latency_ms=latency_ms,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0, prompt=prompt,
        )


def _output_model():
    from typing import Literal

    from pydantic import BaseModel

    class RebalanceReview(BaseModel):
        decision: Literal["approve", "postpone"]
        confidence: float
        rationale: str
        risk_flags: list[str]

    return RebalanceReview


def build_rebalance_reviewer(settings: Settings) -> ClaudeRebalanceReviewer | None:
    """Claude when TB_LLM_ENABLED and the SDK and a key are present; otherwise no reviewer."""
    import os

    if not settings.llm_enabled:
        return None
    if not (os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")):
        log.warning("TB_LLM_ENABLED is set but no Anthropic credential is configured; rebalance review is off")
        return None
    try:
        return ClaudeRebalanceReviewer(settings)
    except ImportError:
        log.warning("TB_LLM_ENABLED is set but the anthropic package is not installed; rebalance review is off")
        return None
