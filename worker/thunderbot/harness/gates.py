"""How an LLM role earns authority, and how it loses it.

A role is in one of two stages. In **shadow** it is asked and its answer is written down, and the
engine carries on as if it had said "take at full size". In **active** its answer is applied. A role
starts where ``gates.toml`` says (shadow, for the roles scored here) and moves on evidence alone.

Every setup a role was asked about is followed to its outcome whether or not it was traded, so its
marginal value can be computed exactly, setup by setup, against doing nothing::

    delta_i = (w_i - 1) * R_i - c_i

- ``w_i`` is the share of normal size the role asked for: 1 to leave the trade alone, 0 for a veto
  (or for an approval below the confidence the engine requires, or a failed call that skips the trade).
- ``R_i`` is what the setup went on to make in units of risk, after charges and slippage, at the size
  the risk limits would have given it. It is clipped to the range in ``gates.toml``.
- ``c_i`` is what the call cost, in the same units, capped as ``gates.toml`` says.

Vetoing a loser of -1R scores +1R; vetoing a winner of +2R scores -2R; leaving a setup alone scores
-c. The average of ``delta`` is what the role is worth per setup. It is wrapped in a confidence
sequence (``stats.confseq``) that stays valid however often it is looked at, so the stage can change
the moment a bound crosses zero without the usual penalty for peeking.

- shadow -> active when there are at least ``n_min`` scored setups and the lower bound is above zero.
- active -> shadow when the upper bound is below zero, or the running total is below ``demote_cum_r``.

Only forward paper and live decisions are scored. Replays and backtests never are: a model has read
the past. Scores are kept per ``(role, harness_id)``, so editing a prompt starts a new record and two
harnesses can be compared on the same days.
"""

from __future__ import annotations

import logging
from typing import Any

from ..clock import now_ist
from ..stats.confseq import ConfidenceSequence
from . import DECISION_ROLES, Harness, current

log = logging.getLogger(__name__)

STAGES_KEY, STATE_KEY, GATES_KEY, HARNESS_KEY, HISTORY_KEY = "role_stages", "gate_state", "gates", "harness", "harness_history"
MAX_POINTS = 160  # points kept per role for the dashboard's chart
SCAN = 1000  # outcome rows read per evaluation (the newest); evaluated daily, a day has a few dozen


def _event(store: Any, kind: str, message: str, **data: Any) -> None:
    emit = getattr(store, "event", None)
    if emit is not None:
        emit(kind, message, **data)
    else:
        store.insert("events", {"kind": kind, "message": message, "data": data})


def stage_of(control: dict[str, Any], role: str | None, h: Harness | None = None) -> str:
    """The stage a role is in. A role that is not a harness role (the rule-based baseline) is always applied."""
    if role not in DECISION_ROLES:
        return "active"
    h = h or current()
    held = (control.get(STAGES_KEY) or {}).get(role) or {}
    if held.get("harness_id") == h.id and held.get("stage") in ("shadow", "active"):
        return held["stage"]
    return str(h.gate(role)["stage"])  # a new or edited harness has earned nothing yet


def asked_weight(decision: Any, min_confidence: float) -> float:
    """The share of normal size a role's answer amounts to once the engine's own rules are applied to it."""
    if not decision.approve or decision.confidence < min_confidence:
        return 0.0
    return min(max(float(decision.size_multiplier), 0.0), 1.0)


def delta(w: float, net_r: float, cost_r: float, gate: dict[str, Any]) -> float:
    lo, hi = gate["r_bounds"]
    r = min(max(net_r, lo), hi)
    c = min(max(cost_r, 0.0), float(gate["max_call_cost_r"]))
    return (min(max(w, 0.0), 1.0) - 1.0) * r - c


def delta_bounds(gate: dict[str, Any]) -> tuple[float, float]:
    lo, hi = gate["r_bounds"]
    return -float(hi) - float(gate["max_call_cost_r"]), -float(lo)


def _fresh(role: str, harness_id: str, gate: dict[str, Any]) -> dict[str, Any]:
    lo, hi = delta_bounds(gate)
    return {"role": role, "harness_id": harness_id, "cs": ConfidenceSequence(lo, hi, float(gate["alpha"])).state(),
            "cum": 0.0, "cost_r": 0.0, "vetoes": 0, "shrinks": 0, "series": [], "watermark": "", "seen": [],
            "first": None, "last": None}


def _thin(series: list[dict[str, float]]) -> list[dict[str, float]]:
    if len(series) <= MAX_POINTS:
        return series
    keep = series[::2]
    return keep if keep[-1] is series[-1] else keep + [series[-1]]


def _verdict(n: int, n_min: int, mean: float, lower: float, upper: float) -> tuple[str, str, int | None]:
    if n and upper < 0:
        return "drag", (f"Net drag: over {n} setups this role cost {mean:+.2f}R a setup, and even the upper bound "
                        f"({upper:+.2f}R) is below zero. It is kept in shadow."), None
    if n < n_min:
        left = n_min - n
        return "too_few", (f"Too few to judge: {n} of the {n_min} scored setups needed, so {left} more to go."
                           if n else f"Nothing scored yet. It needs {n_min} setups it was asked about."), left
    if lower > 0:
        return "proven", (f"Proven: over {n} setups this role added {mean:+.2f}R a setup after its own cost, and the "
                          f"lower bound ({lower:+.2f}R) is above zero."), None
    return "inconclusive", (f"Inconclusive after {n} setups: the average is {mean:+.2f}R a setup, but the range runs from "
                            f"{lower:+.2f}R to {upper:+.2f}R and still includes zero."), None


def _view(st: dict[str, Any], h: Harness, stage: str, change: dict[str, Any] | None) -> dict[str, Any]:
    role = st["role"]
    gate = h.gate(role)
    b = ConfidenceSequence.from_state(st["cs"]).bound
    n = b.n
    verdict, text, needs = _verdict(n, int(gate["n_min"]), b.mean, b.lower, b.upper)
    return {
        "role": role, "label": h.roles[role].label, "harness_id": st["harness_id"], "stage": stage, "n": n,
        "n_min": int(gate["n_min"]), "alpha": float(gate["alpha"]),
        "mean": round(b.mean, 4) if n else None, "lower": round(b.lower, 4) if n else None, "upper": round(b.upper, 4) if n else None,
        "cum": round(st["cum"], 3), "cost_r": round(st["cost_r"], 4), "vetoes": st["vetoes"], "shrinks": st["shrinks"],
        "verdict": verdict, "verdict_text": text, "needs": needs, "series": st["series"], "last_change": change,
    }


def evaluate(store: Any, h: Harness | None = None) -> dict[str, Any]:
    """Score every outcome not yet scored, move stages where the evidence says so, and publish the result.

    Safe to call as often as you like: each outcome row is counted once.
    """
    h = h or current()
    control = store.get_control()
    states: dict[str, dict[str, Any]] = dict(control.get(STATE_KEY) or {})
    stages: dict[str, dict[str, Any]] = dict(control.get(STAGES_KEY) or {})
    rows = store.select("signal_outcomes", None, order="created_at", desc=True, limit=SCAN)
    rows = sorted(rows, key=lambda r: (str(r.get("created_at") or ""), str(r.get("id") or "")))
    touched = False
    for row in rows:
        role, hid = row.get("llm_role"), row.get("harness_id")
        if role not in DECISION_ROLES or not hid or row.get("mode") == "replay":
            continue
        if row.get("net_r") is None or row.get("llm_w") is None:
            continue  # it could not have been filled at any size, so there is nothing to compare
        key = f"{role}:{hid}"
        gate = h.gate(role)
        if not gate.get("scored"):
            continue
        st = states.get(key) or _fresh(role, hid, gate)
        at, rid = str(row.get("created_at") or ""), str(row.get("id") or "")
        if at < st["watermark"] or rid in st["seen"]:
            continue
        risk = float(row.get("risk_inr") or 0)
        cost_r = float(row.get("llm_cost_inr") or 0) / risk if risk > 0 else 0.0
        w = float(row["llm_w"])
        d = delta(w, float(row["net_r"]), cost_r, gate)
        cs = ConfidenceSequence.from_state(st["cs"])
        b = cs.add(d)
        st["cs"] = cs.state()
        st["cum"] += d
        st["cost_r"] += min(max(cost_r, 0.0), float(gate["max_call_cost_r"]))
        st["vetoes"] += w == 0
        st["shrinks"] += 0 < w < 1
        st["series"] = _thin(st["series"] + [{"n": b.n, "mean": round(b.mean, 4), "lower": round(b.lower, 4), "upper": round(b.upper, 4)}])
        st["seen"] = (st["seen"] if at == st["watermark"] else []) + [rid]
        st["watermark"] = at
        st["first"] = st["first"] or at
        st["last"] = at
        states[key] = st
        touched = True

    out_roles = []
    for role in DECISION_ROLES:
        gate = h.gate(role)
        if not gate.get("scored"):
            continue
        key = f"{role}:{h.id}"
        st = states.get(key) or _fresh(role, h.id, gate)
        stage = stage_of({STAGES_KEY: stages}, role, h)
        b = ConfidenceSequence.from_state(st["cs"]).bound
        new, why = stage, ""
        if stage == "shadow" and b.n >= int(gate["n_min"]) and b.lower > 0:
            new, why = "active", (f"{b.n} scored setups, lower bound {b.lower:+.3f}R above zero "
                                  f"(average {b.mean:+.3f}R a setup after its own cost)")
        elif stage == "active" and b.n and b.upper < 0:
            new, why = "shadow", f"upper bound {b.upper:+.3f}R below zero after {b.n} scored setups"
        elif stage == "active" and st["cum"] < float(gate["demote_cum_r"]):
            new, why = "shadow", f"it has cost {st['cum']:+.2f}R in total, past the limit of {float(gate['demote_cum_r']):+.1f}R"
        change = (stages.get(role) or {}).get("change") if (stages.get(role) or {}).get("harness_id") == h.id else None
        if new != stage:
            change = {"at": now_ist().isoformat(), "from": stage, "to": new, "why": why}
            stages[role] = {"stage": new, "harness_id": h.id, "change": change}
            store.set_control(STAGES_KEY, stages)
            _event(store, "role_stage", f"{h.roles[role].label} moved from {stage} to {new}: {why}", role=role,
                        harness_id=h.id, n=b.n, mean=round(b.mean, 4), lower=round(b.lower, 4), upper=round(b.upper, 4),
                        cum=round(st["cum"], 3))
            stage = new
        out_roles.append(_view(st, h, stage, change))
    # Earlier harnesses that were scored, newest first, so two can be compared on their own forward days.
    earlier = sorted((s for k, s in states.items() if s["harness_id"] != h.id and s["role"] in h.roles and s["cs"]["n"]),
                     key=lambda s: str(s.get("last") or ""), reverse=True)[:6]
    out_roles += [_view(s, h, "shadow", None) for s in earlier]
    if touched:
        store.set_control(STATE_KEY, states)
    lo, hi = h.gate("trader")["r_bounds"]
    result = {
        "updated_at": now_ist().isoformat(), "roles": out_roles,
        "note": (f"Only forward paper and live decisions are scored; replays and backtests never are. Before scoring, R is "
                 f"clipped to {lo:g} to {hi:g} and a call's cost is capped at {h.gate('trader')['max_call_cost_r']:g}R. "
                 "The range is valid at every look, so checking it daily does not weaken it."),
    }
    previous = control.get(GATES_KEY) or {}
    if touched or previous.get("roles") != out_roles:
        store.set_control(GATES_KEY, result)
    return result


def harness_view(h: Harness, control: dict[str, Any]) -> dict[str, Any]:
    """What the dashboard's Harness page shows. Roles that only write notes are listed under ``files``."""
    from ..config import (
        HARD_MAX_DAILY_LOSS_PCT,
        HARD_MAX_LEVERAGE,
        HARD_MAX_ORDERS_PER_SECOND,
        HARD_MAX_RISK_PER_TRADE_PCT,
    )

    history = control.get(HISTORY_KEY) or {}
    counts: dict[str, int] = {}
    for st in (control.get(STATE_KEY) or {}).values():
        counts[st["harness_id"]] = counts.get(st["harness_id"], 0) + int(st["cs"]["n"])
    roles = [{"name": name, "label": r.label, "purpose": r.purpose, "may": r.may, "reads": list(r.reads),
              "on_failure": r.on_failure, "stage": stage_of(control, name, h), "scored": bool(h.gate(name)["scored"]),
              "prompt_path": r.prompt_path} for name, r in h.roles.items() if name in DECISION_ROLES]
    return {
        "id": h.id, "source": h.source, "path": h.path, "loaded_at": h.loaded_at, "valid": h.valid, "problems": list(h.problems),
        "memory_mode": h.memory_mode, "files": [dict(f) for f in h.files], "roles": roles,
        "ceilings": {"risk_per_trade_pct": HARD_MAX_RISK_PER_TRADE_PCT, "max_daily_loss_pct": HARD_MAX_DAILY_LOSS_PCT,
                     "max_leverage": HARD_MAX_LEVERAGE, "orders_per_second": HARD_MAX_ORDERS_PER_SECOND},
        "previous_ids": [{"id": k, "first_seen": v.get("first_seen"), "last_seen": v.get("last_seen"), "decisions": counts.get(k, 0)}
                         for k, v in sorted(history.items(), key=lambda kv: str(kv[1].get("last_seen") or ""), reverse=True)
                         if k != h.id][:12],
    }


def publish(store: Any, control: dict[str, Any] | None = None, h: Harness | None = None) -> None:
    """Keep the dashboard's copy of the harness current. Cheap: writes only when something changed.

    Also sets the investing plan from ``plans/investing.toml`` when none has been chosen yet.
    """
    h = h or current()
    control = store.get_control() if control is None else control
    history = dict(control.get(HISTORY_KEY) or {})
    now = now_ist().isoformat()
    seen = history.get(h.id)
    if seen is None or str(seen.get("last_seen", ""))[:10] != now[:10]:
        history[h.id] = {"first_seen": (seen or {}).get("first_seen", now), "last_seen": now}
        store.set_control(HISTORY_KEY, history)
        control = {**control, HISTORY_KEY: history}
    view = harness_view(h, control)
    held = control.get(HARNESS_KEY) or {}
    if {k: v for k, v in held.items() if k != "loaded_at"} != {k: v for k, v in view.items() if k != "loaded_at"}:
        store.set_control(HARNESS_KEY, view)
        if held.get("id") and held.get("id") != h.id:
            _event(store, "harness", f"harness changed from {held['id']} to {h.id}; scored roles start again in shadow",
                        previous=held["id"], current=h.id)
        if h.problems:
            _event(store, "error", f"the harness in TB_HARNESS_DIR was not used: {'; '.join(h.problems)}"[:900])
    plan = h.plans.get("investing")
    if plan and not control.get("invest_settings"):
        store.set_control("invest_settings", {"strategy": plan["plan"], "params": dict(plan.get("params") or {})})
