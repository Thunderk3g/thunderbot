"""End-of-day review: what the desk did, what the skipped setups would have done, and a few lessons.

The lessons are kept in the control row ``ai_memory`` and shown to the LLM trader on later days. With
no LLM configured the review is the numbers alone and no lessons are written.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from ..config import Settings

log = logging.getLogger(__name__)

MAX_LESSONS = 8

REVIEW_PROMPT = """\
You are reviewing one day of a small intraday paper-trading desk on India's NSE. Each setup below was either
taken or skipped; "r" is what it made in units of risk if followed mechanically from signal to stop, target
or the close (before costs), and "pnl" is the rupee result after costs for trades that were taken.

Write for the trader who will sit at this desk tomorrow. Reply with one JSON object and nothing else:
{"summary": "two or three plain sentences on how the day went and why",
 "lessons": ["up to four short, specific, testable rules of thumb drawn from today's evidence"]}

Rules for lessons: base each one on something visible in the data (a kind of setup, a time of day, the
market's direction, a pattern in what was skipped). Do not write generic trading advice. One day is thin
evidence, so word lessons as things to watch, and write none if the day shows nothing clear.
"""


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


def review_day(store: Any, s: Settings, st: dict[str, Any], control: dict[str, Any]) -> dict[str, Any]:
    numbers = day_numbers(st)
    memory = dict(control.get("ai_memory") or {})
    review: dict[str, Any] = {"day": st["day"], "numbers": numbers, "summary": "", "by": "none"}
    if s.llm_enabled and s.chat_llm and st["decisions"]:
        from ..llm.trader import ChatClient, extract_json

        rows = [{k: d.get(k) for k in ("t", "symbol", "side", "kind", "prob", "verdict", "by", "r", "outcome", "pnl", "exit")}
                for d in st["decisions"]]
        user = json.dumps({"numbers": numbers, "market_at_close": (control.get("ai_desk") or {}).get("market"),
                           "setups": rows, "earlier_lessons": memory.get("lessons") or []}, indent=1, default=str)
        client = ChatClient(s.llm_api_key or "", s.llm_base_url or "", s.llm_chat_model or "", timeout=45.0)
        text, _ = client.complete(REVIEW_PROMPT, user, max_tokens=600)
        out = extract_json(text)
        review["summary"] = str(out.get("summary", "")).strip()[:900]
        review["by"] = client.model
        fresh = [str(x).strip()[:240] for x in (out.get("lessons") or []) if str(x).strip()][:4]
        dated = [{"day": st["day"], "text": x} for x in fresh]
        memory["lessons"] = ((memory.get("lessons") or []) + dated)[-MAX_LESSONS:]
    memory["last_review"] = review
    store.set_control("ai_memory", memory)
    took = f"{numbers['trades']} trade{'s' if numbers['trades'] != 1 else ''}"
    store.event("ai_review", f"AI desk closed {st['day']}: {took}, net {numbers['net_pnl']:+.2f}. {review['summary']}".strip(),
                **numbers)
    return review
