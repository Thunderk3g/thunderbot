"""End-of-day review: what the desk did, what the skipped setups would have done, and a few lessons.

The review and its lessons are kept in the control row ``ai_memory`` and shown on the dashboard. Whether
the trader also sees the lessons before its next decisions is the harness's memory mode: "journal_only"
(the default) keeps them out of the prompt, because one day of trades is thin evidence and a prompt that
changes overnight is a different, unscored harness; "inject" puts them in. With no LLM configured the
review is the numbers alone and no lessons are written.

The prompt is a file in the harness (``roles/day_reviewer.md``).
"""

from __future__ import annotations

import json
import logging
from typing import Any

from .. import harness
from ..config import Settings
from ..llm.adapter import ModelAdapter, configured

log = logging.getLogger(__name__)

MAX_LESSONS = 8

def lessons_for_prompt(control: dict[str, Any]) -> list[dict[str, Any]]:
    """The lessons the trader is shown: none unless the harness's memory mode is "inject"."""
    if harness.current().memory_mode != "inject":
        return []
    return [{"day": x.get("day"), "text": x.get("text")} for x in (control.get("ai_memory") or {}).get("lessons") or []]


def __getattr__(name: str) -> Any:
    # The prompt lives in the harness now; the old name still reads it.
    if name == "REVIEW_PROMPT":
        return harness.current().prompt("day_reviewer")
    raise AttributeError(name)


def day_numbers(st: dict[str, Any]) -> dict[str, Any]:
    taken = [d for d in st["decisions"] if d.get("verdict") == "take"]
    skipped = [d for d in st["decisions"] if d.get("verdict") == "skip" and d.get("r") is not None]
    r_taken = [d["r"] for d in taken if d.get("r") is not None]
    r_skipped = [d["r"] for d in skipped]

    def avg(xs: list[float]) -> float | None:
        return round(sum(xs) / len(xs), 2) if xs else None

    return {"day": st["day"], "net_pnl": st["risk"]["realized_pnl"], "trades": st["wins"] + st["losses"], "wins": st["wins"],
            "costs": st["costs"], "setups": len(st["decisions"]), "taken_avg_r": avg(r_taken), "skipped_avg_r": avg(r_skipped),
            "halted": st["risk"]["halted"]}


def review_day(store: Any, s: Settings, st: dict[str, Any], control: dict[str, Any], adapter: Any | None = None) -> dict[str, Any]:
    numbers = day_numbers(st)
    memory = dict(control.get("ai_memory") or {})
    review: dict[str, Any] = {"day": st["day"], "numbers": numbers, "summary": "", "by": "none"}
    if configured(s) and st["decisions"]:
        rows = [{k: d.get(k) for k in ("t", "symbol", "side", "kind", "prob", "verdict", "by", "r", "outcome", "pnl", "exit")}
                for d in st["decisions"]]
        user = json.dumps({"numbers": numbers, "market_at_close": (control.get("ai_desk") or {}).get("market"),
                           "setups": rows, "earlier_lessons": memory.get("lessons") or []}, indent=1, default=str)
        adapter = adapter or ModelAdapter(s)
        reply = adapter.ask("day_reviewer", user)
        if reply.data is None:
            raise RuntimeError(reply.error or "the review call failed")
        review["summary"] = reply.data["summary"]
        review["by"] = reply.model
        review["harness_id"], review["cost_inr"] = reply.harness_id, reply.cost_inr
        dated = [{"day": st["day"], "text": x, "harness_id": reply.harness_id} for x in reply.data["lessons"]]
        memory["lessons"] = ((memory.get("lessons") or []) + dated)[-MAX_LESSONS:]
    memory["mode"] = harness.current().memory_mode
    memory["last_review"] = review
    store.set_control("ai_memory", memory)
    took = f"{numbers['trades']} trade{'s' if numbers['trades'] != 1 else ''}"
    store.event("ai_review", f"AI desk closed {st['day']}: {took}, net {numbers['net_pnl']:+.2f}. {review['summary']}".strip(),
                **numbers)
    return review
