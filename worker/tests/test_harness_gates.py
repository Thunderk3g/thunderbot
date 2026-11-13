"""How an LLM role earns authority and loses it (thunderbot/harness/gates.py)."""

from __future__ import annotations

import random
from types import SimpleNamespace

import pytest

from thunderbot import harness
from thunderbot.harness import gates
from thunderbot.store import CompositeStore, SQLiteStore

GATE = {"r_bounds": [-2.0, 4.0], "max_call_cost_r": 0.5}


@pytest.fixture
def store(tmp_path):
    return CompositeStore(SQLiteStore(tmp_path / "j.sqlite3"))


def outcome(i: int, w: float, net_r: float, *, role="trader", hid=None, cost=0.0, mode="paper", risk=1000.0) -> dict:
    return {"id": f"o{i:05d}", "created_at": f"2026-11-{1 + i // 2000:02d}T10:{(i // 60) % 60:02d}:{i % 60:02d}.{i:06d}+05:30",
            "signal_id": f"s{i}", "symbol": "AAA", "llm_role": role, "harness_id": hid or harness.current_id(), "llm_w": w,
            "net_r": net_r, "llm_cost_inr": cost, "risk_inr": risk, "mode": mode, "llm_decision": "approve" if w else "reject"}


def trader(state: dict) -> dict:
    return next(r for r in state["roles"] if r["role"] == "trader" and r["harness_id"] == harness.current_id())


class TestDelta:
    """delta = (w - 1) * R - c: what the role's answer was worth against leaving the setup alone."""

    @pytest.mark.parametrize("w, r, cost, expected", [
        (0.0, -1.0, 0.0, 1.0),    # vetoed a loser: saved 1R
        (0.0, 2.0, 0.0, -2.0),    # vetoed a winner: gave up 2R
        (1.0, 2.0, 0.01, -0.01),  # left it alone: only the call's cost
        (0.5, -1.0, 0.0, 0.5),    # halved a loser: saved half
        (0.5, 2.0, 0.02, -1.02),  # halved a winner, and paid for the call
        (0.0, 9.0, 0.0, -4.0),    # R is clipped to the range in gates.toml
        (1.0, 1.0, 3.0, -0.5),    # and a call's cost is capped
    ])
    def test_examples(self, w, r, cost, expected):
        assert gates.delta(w, r, cost, GATE) == pytest.approx(expected)

    def test_vetoing_small_winners_is_a_loss_even_when_approvals_do_better(self):
        # The flaw in comparing averages: approved setups make +0.35R, vetoed ones +0.15R, so "approved >
        # vetoed" looks like skill. Every veto still gave up +0.15R.
        deltas = [gates.delta(1.0, 0.35, 0.0, GATE)] * 50 + [gates.delta(0.0, 0.15, 0.0, GATE)] * 50
        assert sum(deltas) / len(deltas) == pytest.approx(-0.075)

    def test_bounds_and_the_weight_the_engine_would_apply(self):
        assert gates.delta_bounds(GATE) == (-4.5, 2.0)
        d = SimpleNamespace(approve=True, confidence=0.9, size_multiplier=0.4)
        assert gates.asked_weight(d, 0.5) == 0.4
        assert gates.asked_weight(SimpleNamespace(approve=True, confidence=0.3, size_multiplier=1.0), 0.5) == 0.0  # too unsure
        assert gates.asked_weight(SimpleNamespace(approve=False, confidence=0.9, size_multiplier=1.0), 0.5) == 0.0


class TestStages:
    def test_defaults_come_from_the_harness_and_do_not_survive_an_edit(self):
        hid = harness.current_id()
        assert gates.stage_of({}, "trader") == "shadow" and gates.stage_of({}, "rebalance_reviewer") == "active"
        assert gates.stage_of({}, None) == "active"  # the rule-based baseline is not a harness role
        held = {gates.STAGES_KEY: {"trader": {"stage": "active", "harness_id": hid}}}
        assert gates.stage_of(held, "trader") == "active"
        held[gates.STAGES_KEY]["trader"]["harness_id"] = "some-other-harness"
        assert gates.stage_of(held, "trader") == "shadow"

    def test_a_role_that_avoids_losers_is_promoted_once_there_is_enough_evidence(self, store):
        rng = random.Random(1)
        rows = []
        for i in range(160):  # it vetoes most losers and leaves winners alone
            loser = rng.random() < 0.6
            rows.append(outcome(i, 0.0 if loser and rng.random() < 0.9 else 1.0, -1.1 if loser else 1.6))
        for row in rows[:60]:
            store.insert("signal_outcomes", row)
        first = trader(gates.evaluate(store))
        assert first["n"] == 60 and first["stage"] == "shadow" and first["verdict"] == "too_few" and first["needs"] == 40
        assert first["mean"] > 0.3  # promising, and still not enough: n_min is 100

        for row in rows[60:]:
            store.insert("signal_outcomes", row)
        second = trader(gates.evaluate(store))
        assert second["n"] == 160 and second["lower"] > 0 and second["verdict"] == "proven" and second["stage"] == "active"
        assert second["last_change"]["from"] == "shadow" and second["last_change"]["to"] == "active"
        assert gates.stage_of(store.get_control(), "trader") == "active"
        event = next(e for e in store.select("events") if e["kind"] == "role_stage")
        assert "shadow to active" in event["message"] and event["data"]["n"] == 160
        assert second["vetoes"] > 60 and second["series"][-1]["n"] == 160 and len(second["series"]) <= gates.MAX_POINTS + 1

        again = trader(gates.evaluate(store))  # nothing new: each outcome is counted once
        assert again["n"] == 160 and again["cum"] == second["cum"]

    def test_a_role_that_vetoes_winners_is_demoted(self, store):
        store.set_control(gates.STAGES_KEY, {"trader": {"stage": "active", "harness_id": harness.current_id()}})
        for i in range(150):
            store.insert("signal_outcomes", outcome(i, 0.0, 1.2, cost=5.0))  # every veto gave up 1.2R and cost Rs 5
        got = trader(gates.evaluate(store))
        assert got["stage"] == "shadow" and got["upper"] < 0 and got["verdict"] == "drag"
        assert got["cum"] == pytest.approx(150 * (-1.2 - 0.005)) and got["cost_r"] == pytest.approx(0.75)
        assert "below zero" in got["last_change"]["why"]

    def test_running_total_demotes_before_the_bound_does(self, store):
        store.set_control(gates.STAGES_KEY, {"trader": {"stage": "active", "harness_id": harness.current_id()}})
        for i in range(3):
            store.insert("signal_outcomes", outcome(i, 0.0, 2.0))  # three vetoed winners: -6R, far too few to prove a drag
        got = trader(gates.evaluate(store))
        assert got["n"] == 3 and got["upper"] > 0 and got["stage"] == "shadow" and "-6.00R in total" in got["last_change"]["why"]

    def test_only_forward_scored_rows_count_and_harnesses_are_kept_apart(self, store):
        rows = [
            outcome(1, 0.0, -1.0),
            outcome(2, 0.0, -1.0, mode="replay"),                 # history a model may have read: never counted
            outcome(3, 0.0, -1.0, role="rebalance_reviewer"),     # not scored in R
            {**outcome(4, 0.0, -1.0), "llm_role": None},          # nobody was asked
            {**outcome(5, 0.0, -1.0), "net_r": None},             # could not have been filled
            outcome(6, 0.0, 2.0, hid="older-harness"),
            outcome(7, 1.0, 2.0, hid="older-harness"),
            outcome(8, 1.0, 1.0, role="signal_reviewer", cost=50.0, risk=500.0),
        ]
        for r in rows:
            store.insert("signal_outcomes", r)
        state = gates.evaluate(store)
        assert trader(state)["n"] == 1 and trader(state)["cum"] == pytest.approx(1.0)
        reviewer = next(r for r in state["roles"] if r["role"] == "signal_reviewer")
        assert reviewer["n"] == 1 and reviewer["cum"] == pytest.approx(-0.1)  # left alone: -c, and c = 50/500 R
        older = next(r for r in state["roles"] if r["harness_id"] == "older-harness")
        assert older["role"] == "trader" and older["n"] == 2 and older["cum"] == pytest.approx(-2.0) and older["stage"] == "shadow"
        assert "replays and backtests never are" in state["note"]
        assert store.get_control()[gates.GATES_KEY]["roles"] == state["roles"]

    def test_too_few_setups_never_promote_however_good(self, store):
        for i in range(99):
            store.insert("signal_outcomes", outcome(i, 0.0, -2.0))  # 99 perfect vetoes
        got = trader(gates.evaluate(store))
        assert got["lower"] > 0 and got["stage"] == "shadow" and got["verdict"] == "too_few" and got["needs"] == 1


class TestPublish:
    def test_the_dashboard_gets_the_harness_and_the_plan_is_seeded_once(self, store):
        gates.publish(store)
        control = store.get_control()
        view = control[gates.HARNESS_KEY]
        h = harness.current()
        assert view["id"] == h.id and view["source"] == "built-in" and view["valid"] and view["memory_mode"] == "journal_only"
        assert [r["name"] for r in view["roles"]] == ["trader", "signal_reviewer", "rebalance_reviewer"]
        assert {r["name"]: r["stage"] for r in view["roles"]} == {"trader": "shadow", "signal_reviewer": "shadow", "rebalance_reviewer": "active"}
        assert {r["may"] for r in view["roles"]} <= {"veto", "shrink", "postpone"}
        assert view["ceilings"]["risk_per_trade_pct"] == 2.0 and view["ceilings"]["max_daily_loss_pct"] == 10.0
        assert any(f["path"] == "roles/day_reviewer.md" and f["kind"] == "prompt" for f in view["files"])
        assert view["previous_ids"] == []
        assert control["invest_settings"] == {"strategy": "core_mix", "params": {}}

        store.set_control("invest_settings", {"strategy": "etf_trend", "params": {}})
        gates.publish(store)
        assert store.get_control()["invest_settings"]["strategy"] == "etf_trend"  # the owner's choice is left alone

    def test_an_earlier_harness_is_remembered(self, store, tmp_path, monkeypatch):
        import shutil

        gates.publish(store)
        first = harness.current_id()
        copy = tmp_path / "h"
        shutil.copytree(harness.DEFAULT_DIR, copy)
        (copy / "roles" / "trader.md").write_text((copy / "roles" / "trader.md").read_text() + "\nBe stricter after 14:00.\n")
        monkeypatch.setenv("TB_HARNESS_DIR", str(copy))
        try:
            harness.reload()
            gates.publish(store)
            view = store.get_control()[gates.HARNESS_KEY]
            assert view["id"] != first and view["source"] == "directory" and [p["id"] for p in view["previous_ids"]] == [first]
            assert any(e["kind"] == "harness" and first in e["message"] for e in store.select("events"))
        finally:
            monkeypatch.delenv("TB_HARNESS_DIR")
            harness.reload()
