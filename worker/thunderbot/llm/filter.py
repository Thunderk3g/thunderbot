"""LLM review layer: filters, ranks and explains signals from the quant engine.

The LLM can only approve or veto a signal and suggest a size multiplier in
[0, 1]. It never sees order controls and never sets prices. ``RiskManager``
clamps its output and has the final say.

The prompts are files in the harness (``roles/signal_reviewer.md``, ``roles/trader.md``); every call
goes through ``llm.adapter``.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Protocol

from ..config import Settings
from .types import LLMDecision, ReviewContext

log = logging.getLogger(__name__)

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


class RoleFilter:
    """An LLM role reviewing signals: it builds the message, asks through the one adapter, and turns the
    checked reply into an ``LLMDecision``. A call that fails follows ``llm_fail_mode`` (skip by default).

    ``role`` is "trader" (the desk's prompt, with the model's score and the market so far) or
    "signal_reviewer" (the long-running engine's prompt). Either works with either client.
    """

    enabled = True

    def __init__(self, settings: Settings, role: str, client: Any | None = None, family: str | None = None) -> None:
        from .adapter import ModelAdapter

        self.s = settings
        self.role = role
        self.adapter = ModelAdapter(settings, client, family)
        self.client = self.adapter.client

    @property
    def label(self) -> str:
        return self.adapter.model

    def _message(self, ctx: ReviewContext) -> str:
        if self.role == "trader":
            from .trader import build_trader_message

            return build_trader_message(ctx)
        return build_user_message(ctx)

    def review(self, ctx: ReviewContext) -> LLMDecision:
        self.adapter.s = self.s  # the engine swaps settings in place when the dashboard changes them
        reply = self.adapter.ask(self.role, self._message(ctx))
        common = dict(model=reply.model, latency_ms=reply.latency_ms, input_tokens=reply.input_tokens,
                      output_tokens=reply.output_tokens, request_id=reply.request_id, prompt=reply.prompt,
                      role=self.role, harness_id=reply.harness_id, cost_inr=reply.cost_inr)
        if reply.data is None:
            d = LLMDecision.failed(reply.error or "no reply", self.s.llm_fail_mode, self.adapter.model, reply.prompt)
            d.latency_ms, d.request_id, d.role, d.harness_id = reply.latency_ms, reply.request_id, self.role, reply.harness_id
            return d
        out = reply.data
        return LLMDecision(approve=out["approve"], size_multiplier=out["size_multiplier"], confidence=out["confidence"],
                           rationale=out["rationale"], risk_flags=out["risk_flags"], **common)


class ClaudeSignalFilter(RoleFilter):
    """The signal reviewer through Anthropic's API."""

    def __init__(self, settings: Settings, client: Any | None = None, role: str = "signal_reviewer") -> None:
        super().__init__(settings, role, client, family="anthropic")


def build_filter(settings: Settings, reviewer: str = "auto", role: str | None = None) -> SignalFilter:
    """``auto``: the configured LLM when it is enabled (an OpenAI-compatible endpoint, or Claude through
    Anthropic's API), else none. ``heuristic``: the free rule-based baseline. Which key and model are in
    use is settled before this is called (``credentials.apply_credentials``).

    ``role`` names the harness role to ask. Left out, it is what each client was always given: the
    trader's prompt on an OpenAI-compatible endpoint, the signal reviewer's on Anthropic.
    """
    if reviewer == "heuristic":
        return HeuristicFilter(settings)
    if reviewer == "none" or not settings.llm_enabled:
        return PassThroughFilter()
    if settings.chat_llm:
        from .trader import ChatSignalFilter

        return ChatSignalFilter(settings, role=role or "trader")
    return ClaudeSignalFilter(settings, role=role or "signal_reviewer")


def __getattr__(name: str) -> Any:
    # The prompt lives in the harness now (roles/signal_reviewer.md); the old name still reads it.
    if name == "SYSTEM_PROMPT":
        from .. import harness

        return harness.current().prompt("signal_reviewer")
    raise AttributeError(name)
