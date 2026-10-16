"""LLM review layer: filters, ranks and explains signals from the quant engine.

The LLM can only approve or veto a signal and suggest a size multiplier in
[0, 1]. It never sees order controls and never sets prices. ``RiskManager``
clamps its output and has the final say.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Protocol

from ..config import Settings
from .types import LLMDecision, ReviewContext

log = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are the risk reviewer for a small, rules-based intraday trading system on India's NSE cash market.
A deterministic strategy has already produced a trade signal with a fixed entry, stop and target.
Your job is to decide whether to let it through, and if so how much of the normal size to use.

What you control:
- decision: "approve" or "reject".
- size_multiplier: a number from 0.0 to 1.0. 1.0 means normal size. You can never increase size.
- confidence: a number from 0.0 to 1.0 for how sure you are of your decision.
- rationale: two to four plain sentences a human can audit later.
- risk_flags: short snake_case tags for concerns, e.g. "late_session", "low_volume", "extended_from_vwap",
  "against_index_trend", "wide_stop", "event_risk". Empty list if none.

What you do not control: entry, stop, target, order type, timing. Hard risk limits run after you and
override you, so do not reason about account-level limits beyond what is shown.

How to judge:
- Use only the data in the message. Do not use any knowledge of what this stock did after the signal
  time, and do not guess at news that is not provided.
- Reject when the setup is weak on the data shown: breakout bar with poor volume, price far extended
  from VWAP relative to the stop distance, choppy bars that repeatedly crossed the range, a reward that
  does not justify the stop, or context notes that point clearly against the trade.
- Reduce size, rather than reject, when the setup is valid but has one notable concern.
- Approve at 1.0 only for clean setups. When in doubt, prefer a smaller size over a rejection, and a
  rejection over a large size.
"""


class SignalFilter(Protocol):
    enabled: bool

    def review(self, ctx: ReviewContext) -> LLMDecision: ...


class PassThroughFilter:
    """Used when the LLM layer is disabled (and by default in backtests)."""

    enabled = False
    label = "none"

    def review(self, ctx: ReviewContext) -> LLMDecision:
        return LLMDecision.passthrough()


class HeuristicFilter:
    """A rule-based reviewer with the same contract as the LLM: veto or shrink, never enlarge.

    It costs nothing and is a baseline. If Claude's reviews can't beat these rules in
    the signal-outcome journal, the LLM isn't earning its cost. Decisions are labelled
    ``model="heuristic"`` so they are never mistaken for LLM output.
    """

    enabled = True
    label = "heuristic"

    def __init__(self, settings: Settings | None = None) -> None:
        self.s = settings

    def review(self, ctx: ReviewContext) -> LLMDecision:
        sig = ctx.signal
        flags: list[str] = []
        stop_pct = sig.risk_per_share / sig.entry * 100 if sig.entry else 0.0
        vol = sig.features.get("volume_ratio")
        if sig.ts.hour * 60 + sig.ts.minute >= 13 * 60 + 30:
            flags.append("late_session")
        if vol is not None and vol < 1.5:
            flags.append("low_volume")
        if sig.reward_risk < 1.2:
            flags.append("poor_reward")
        if stop_pct > 1.5:
            flags.append("wide_stop")
        hard = {"late_session", "low_volume", "poor_reward"} & set(flags)
        if hard:
            return LLMDecision(False, 0.0, 0.7, f"Rule veto: {', '.join(sorted(hard))}.", flags, model="heuristic")
        mult = 0.5 if "wide_stop" in flags else 1.0
        return LLMDecision(True, mult, 0.7, "Rules passed" + (" (half size: wide stop)." if mult < 1 else "."),
                           flags, model="heuristic")


def build_user_message(ctx: ReviewContext) -> str:
    sig = ctx.signal
    payload: dict[str, Any] = {
        "signal": {
            "symbol": sig.symbol,
            "side": sig.side.value,
            "product": sig.product.value,
            "strategy": sig.strategy,
            "time_ist": sig.ts.isoformat(),
            "entry": sig.entry,
            "stop": sig.stop,
            "target": sig.target,
            "risk_per_share": round(sig.risk_per_share, 2),
            "stop_distance_pct": round(sig.risk_per_share / sig.entry * 100, 3),
            "reward_to_risk": round(sig.reward_risk, 2),
            "strategy_reason": sig.reason,
            "features": sig.features,
        },
        "recent_bars": [
            {
                "t": b.ts.strftime("%H:%M"),
                "o": round(b.open, 2),
                "h": round(b.high, 2),
                "l": round(b.low, 2),
                "c": round(b.close, 2),
                "v": int(b.volume),
            }
            for b in ctx.recent_bars
        ],
        "account_today": {
            "realized_pnl": round(ctx.day_realized_pnl, 2),
            "trades_opened": ctx.trades_today,
            "open_positions": ctx.open_positions,
        },
        "context_notes": ctx.market_notes,
    }
    return "Review this signal.\n\n" + json.dumps(payload, indent=1, default=str)


class ClaudeSignalFilter:
    enabled = True

    @property
    def label(self) -> str:
        return self.s.llm_model

    def __init__(self, settings: Settings, client: Any | None = None) -> None:
        self.s = settings
        if client is None:
            import anthropic

            client = anthropic.Anthropic(timeout=settings.llm_timeout_seconds, max_retries=2)
        self.client = client
        self._output_model = _review_output_model()

    def review(self, ctx: ReviewContext) -> LLMDecision:
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
            return LLMDecision.failed(f"rate_limited: {e.message}", self.s.llm_fail_mode, model, prompt)
        except anthropic.APIStatusError as e:
            return LLMDecision.failed(f"api_error_{e.status_code}: {e.message}", self.s.llm_fail_mode, model, prompt)
        except anthropic.APIConnectionError as e:
            return LLMDecision.failed(f"connection_error: {e}", self.s.llm_fail_mode, model, prompt)
        except Exception as e:  # validation errors from parse, etc.
            log.exception("LLM review failed")
            return LLMDecision.failed(f"{type(e).__name__}: {e}", self.s.llm_fail_mode, model, prompt)

        latency_ms = int((time.monotonic() - started) * 1000)
        usage = getattr(response, "usage", None)
        common = dict(
            model=getattr(response, "model", model),
            latency_ms=latency_ms,
            input_tokens=getattr(usage, "input_tokens", 0) or 0,
            output_tokens=getattr(usage, "output_tokens", 0) or 0,
            request_id=getattr(response, "_request_id", None),
            prompt=prompt,
        )

        if response.stop_reason == "refusal":
            details = getattr(response, "stop_details", None)
            category = getattr(details, "category", None)
            d = LLMDecision.failed(f"refusal ({category})", self.s.llm_fail_mode, model, prompt)
            d.latency_ms, d.request_id = latency_ms, common["request_id"]
            return d
        out = response.parsed_output
        if out is None:
            d = LLMDecision.failed(f"no parsed output (stop_reason={response.stop_reason})", self.s.llm_fail_mode, model, prompt)
            d.latency_ms, d.request_id = latency_ms, common["request_id"]
            return d

        return LLMDecision(
            approve=out.decision == "approve",
            size_multiplier=min(max(float(out.size_multiplier), 0.0), 1.0),
            confidence=min(max(float(out.confidence), 0.0), 1.0),
            rationale=out.rationale.strip(),
            risk_flags=[f.strip() for f in out.risk_flags if f.strip()][:10],
            **common,
        )


def _review_output_model():
    from typing import Literal

    from pydantic import BaseModel

    class ReviewOutput(BaseModel):
        decision: Literal["approve", "reject"]
        size_multiplier: float
        confidence: float
        rationale: str
        risk_flags: list[str]

    return ReviewOutput


def build_filter(settings: Settings, reviewer: str = "auto") -> SignalFilter:
    """``auto``: Claude when TB_LLM_ENABLED, else none. ``heuristic``: the free rule-based baseline."""
    if reviewer == "heuristic":
        return HeuristicFilter(settings)
    if reviewer == "none" or not settings.llm_enabled:
        return PassThroughFilter()
    return ClaudeSignalFilter(settings)
