"""The harness: files a person can edit, checked before they are used (thunderbot/harness)."""

from __future__ import annotations

import hashlib
import shutil

import pytest

from thunderbot import harness
from thunderbot.harness import DEFAULT_DIR, HarnessError

# The prompts as they were when they lived in the code, by SHA-256. The shipped harness must reproduce them.
ORIGINAL_PROMPTS = {
    "trader": "fc001fe8174cc68b2ecd089a21d3628b258a6236cfc9a99fd69ea3e4f33422c2",
    "signal_reviewer": "09344a54730d186f5eb30b5ad505a121b931a714d0add0429b6f1e32bb7608d8",
    "rebalance_reviewer": "563a03e515b12a7a9f960fac1f01bda18f8c6bb025b2dbe4041ebb4bd4f0a5f5",
    "day_reviewer": "46e6ca7374e32b4665f9a1405beffa7ba9f053e4b62395adc97692431108b2ff",
}


@pytest.fixture
def copy(tmp_path, monkeypatch):
    """A complete copy of the built-in harness in a directory, selected with TB_HARNESS_DIR."""
    target = tmp_path / "harness"
    shutil.copytree(DEFAULT_DIR, target)
    monkeypatch.setenv("TB_HARNESS_DIR", str(target))
    harness.reload()
    yield target
    monkeypatch.delenv("TB_HARNESS_DIR")
    harness.reload()


def edit(path, old: str, new: str) -> None:
    text = path.read_text()
    assert old in text, old
    path.write_text(text.replace(old, new))


def test_the_shipped_harness_loads_and_reproduces_the_original_prompts():
    h = harness.load(None)
    assert h.source == "built-in" and h.valid and len(h.id) == 12
    assert {name: hashlib.sha256(h.prompt(name).encode()).hexdigest() for name in ORIGINAL_PROMPTS} == ORIGINAL_PROMPTS
    assert h.memory_mode == "journal_only"
    assert h.gate("trader")["stage"] == "shadow" and h.gate("signal_reviewer")["stage"] == "shadow"
    assert h.gate("rebalance_reviewer") == {**h.gate("rebalance_reviewer"), "stage": "active", "scored": False}
    assert h.gate("trader")["n_min"] == 100 and h.gate("trader")["alpha"] == 0.05
    assert h.may("trader") == "shrink" and h.may("rebalance_reviewer") == "postpone"
    assert h.risk_overrides() == {} and h.desk_symbols() == []  # nothing is imposed until the owner writes it
    assert h.plans["investing"]["plan"] == "core_mix"
    assert {f["path"] for f in h.files} >= {"policy.toml", "gates.toml", "roles/trader.md", "roles/trader.toml"}


def test_old_prompt_names_still_read_the_harness():
    from thunderbot.ai import reflect
    from thunderbot.llm import filter as review
    from thunderbot.llm import rebalance, trader

    h = harness.current()
    assert trader.TRADER_PROMPT == h.prompt("trader") and review.SYSTEM_PROMPT == h.prompt("signal_reviewer")
    assert rebalance.SYSTEM_PROMPT == h.prompt("rebalance_reviewer") and reflect.REVIEW_PROMPT == h.prompt("day_reviewer")


def test_a_directory_harness_is_used_and_any_edit_changes_its_id(copy):
    first = harness.current()
    assert first.source == "directory" and first.path == str(copy)
    assert first.id == harness.load(None).id  # an untouched copy is the same harness
    edit(copy / "roles" / "trader.md", "Most days deserve few trades.", "Most days deserve no trades at all.")
    second = harness.current()  # re-read because the file changed
    assert second.id != first.id and "no trades at all" in second.prompt("trader")
    edit(copy / "policy.toml", 'mode = "journal_only"', 'mode = "inject"')
    third = harness.current()
    assert third.memory_mode == "inject" and third.id not in (first.id, second.id)


def test_policy_limits_apply_and_cannot_pass_the_ceilings(copy):
    edit(copy / "policy.toml", "# risk_per_trade_pct = 0.5", "risk_per_trade_pct = 0.25")
    edit(copy / "policy.toml", "desk_symbols = []", 'desk_symbols = ["RELIANCE", "tcs"]')
    h = harness.current()
    assert h.valid and h.risk_overrides() == {"risk_per_trade_pct": 0.25} and h.desk_symbols() == ["RELIANCE", "TCS"]

    edit(copy / "policy.toml", "risk_per_trade_pct = 0.25", "risk_per_trade_pct = 5.0")  # the ceiling is 2%
    bad = harness.current()
    assert not bad.valid and bad.source == "built-in" and bad.id == harness.load(None).id  # the built-in one runs
    assert any("policy.toml [risk] risk_per_trade_pct" in p and "5.0" in p for p in bad.problems)
    with pytest.raises(HarnessError) as e:
        harness.load(copy)
    assert "policy.toml [risk] risk_per_trade_pct" in str(e.value)


@pytest.mark.parametrize("path, old, new, names", [
    ("roles/rebalance_reviewer.toml", 'may = "postpone"', 'may = "shrink"', "roles/rebalance_reviewer.toml may"),
    ("roles/trader.toml", 'may = "shrink"', 'may = "enlarge"', "roles/trader.toml may"),
    ("gates.toml", "n_min = 100", "n_min = 5", "gates.toml [defaults] n_min"),
    ("gates.toml", "alpha = 0.05", "alpha = 0.9", "gates.toml [defaults] alpha"),
    ("gates.toml", "r_bounds = [-2.0, 4.0]", "r_bounds = [1.0, 4.0]", "gates.toml [defaults] r_bounds"),
    ("policy.toml", 'mode = "journal_only"', 'mode = "always"', "policy.toml [memory] mode"),
    ("policy.toml", "# max_leverage = 1.0", "max_leverage = 20", "policy.toml [risk] max_leverage"),
    ("policy.toml", "# capital = 100000", "live_trading_enabled = true", "policy.toml [risk] live_trading_enabled"),
    ("plans/investing.toml", 'plan = "core_mix"', 'plan = "yolo"', "plans/investing.toml plan"),
    ("plans/desk.toml", "min_stop_pct = 0.8", "min_stop_pct = 0.0", "plans/desk.toml [params] min_stop_pct"),
])
def test_a_bad_edit_is_refused_by_name(copy, path, old, new, names):
    edit(copy / path, old, new)
    with pytest.raises(HarnessError) as e:
        harness.load(copy)
    assert names in str(e.value)
    assert not harness.current().valid and harness.current().source == "built-in"


def test_a_role_limited_to_veto_cannot_shrink_and_missing_files_are_named(copy):
    edit(copy / "roles" / "trader.toml", 'may = "shrink"', 'may = "veto"')
    assert harness.current().valid and harness.current().may("trader") == "veto"
    (copy / "roles" / "trader.md").unlink()
    (copy / "gates.toml").unlink()
    with pytest.raises(HarnessError) as e:
        harness.load(copy)
    assert "roles/trader.toml prompt" in str(e.value) and "gates.toml: missing" in str(e.value)
    (copy / "policy.toml").write_text("this is = not [toml")
    assert any("policy.toml: not valid TOML" in p for p in harness.current().problems)


def test_a_missing_directory_falls_back(monkeypatch, tmp_path):
    monkeypatch.setenv("TB_HARNESS_DIR", str(tmp_path / "nowhere"))
    h = harness.reload()
    assert h.source == "built-in" and not h.valid and "not a directory" in h.problems[0]
    monkeypatch.delenv("TB_HARNESS_DIR")
    assert harness.reload().valid


def test_cost_comes_only_from_the_owners_prices(copy):
    assert harness.current().cost_inr(10_000, 2_000) == 0.0  # no price is assumed for any provider
    edit(copy / "policy.toml", "usd_per_mtok_in = 0.0", "usd_per_mtok_in = 2.0")
    edit(copy / "policy.toml", "usd_per_mtok_out = 0.0", "usd_per_mtok_out = 10.0")
    edit(copy / "policy.toml", "usd_inr = 0.0", "usd_inr = 90.0")
    # (10,000 * $2 + 2,000 * $10) / 1,000,000 = $0.04, at Rs 90 = Rs 3.60
    assert harness.current().cost_inr(10_000, 2_000) == pytest.approx(3.6)


def test_export_writes_a_copy_that_loads(tmp_path):
    out = harness.export(tmp_path / "mine")
    assert harness.load(out).id == harness.load(None).id
    with pytest.raises(FileExistsError):
        harness.export(out)
