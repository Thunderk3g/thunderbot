from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import Candle, Signal


@dataclass
class ReviewContext:
    """Everything the LLM is shown about a signal. Only point-in-time data."""

    signal: Signal
    recent_bars: list[Candle]
    open_positions: list[dict[str, Any]] = field(default_factory=list)
    day_realized_pnl: float = 0.0
    trades_today: int = 0
    market_notes: list[str] = field(default_factory=list)  # e.g. index trend, headlines


@dataclass
class LLMDecision:
    approve: bool
    size_multiplier: float
    confidence: float
    rationale: str
    risk_flags: list[str] = field(default_factory=list)
    model: str = ""
    latency_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    error: str | None = None
    request_id: str | None = None
    prompt: str = ""

    @classmethod
    def passthrough(cls) -> "LLMDecision":
        return cls(approve=True, size_multiplier=1.0, confidence=1.0, rationale="LLM review disabled", model="none")

    @classmethod
    def failed(cls, error: str, fail_mode: str, model: str, prompt: str = "") -> "LLMDecision":
        approve = fail_mode == "pass"
        return cls(
            approve=approve,
            size_multiplier=1.0 if approve else 0.0,
            confidence=1.0 if approve else 0.0,
            rationale=f"LLM review failed ({error}); fail mode '{fail_mode}'",
            risk_flags=["llm_error"],
            model=model,
            error=error,
            prompt=prompt,
        )
