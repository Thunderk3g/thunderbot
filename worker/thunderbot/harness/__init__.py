"""The harness: everything that shapes a decision and is not the engine, as files a person can edit.

A harness is a directory::

    policy.toml             what the owner wants: limits, memory mode, what the LLM costs
    gates.toml              how an LLM role earns authority and loses it
    plans/investing.toml    which daily plan, and its parameters
    plans/desk.toml         the intraday desk's settings
    roles/<name>.toml       what a role is for, what it may affect, what it reads
    roles/<name>.md         the prompt the role is given

The copy that ships with the code is in ``harness/default``. ``TB_HARNESS_DIR`` points at another
complete copy to use in its place. Every value is checked when it is loaded: against the ceilings in
``config.py`` that no setting can exceed, and against what each role is allowed to do. A harness that
fails any check is not used; the built-in one is, and the problem is reported, so a bad edit can never
stop trading or widen what a model may do.

``harness_id`` is a 12-character digest of every file in the bundle. It is stamped on each decision,
so two harnesses can be compared on the same forward days, and an edit to any prompt or limit starts
a new record.
"""

from __future__ import annotations

import hashlib
import logging
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)

DEFAULT_DIR = Path(__file__).parent / "default"
ENV_DIR = "TB_HARNESS_DIR"

# What each role may do at most. A role file can ask for less, never for more, and nothing outside
# this table exists: no role can enlarge a trade, set a price or create an order.
ROLE_MAX: dict[str, str] = {
    "trader": "shrink",
    "signal_reviewer": "shrink",
    "rebalance_reviewer": "postpone",
    "day_reviewer": "notes",
}
ALLOWED_MAY: dict[str, tuple[str, ...]] = {"shrink": ("veto", "shrink"), "postpone": ("postpone",), "notes": ("notes",)}
DECISION_ROLES = ("trader", "signal_reviewer", "rebalance_reviewer")  # roles that can affect a trade
MEMORY_MODES = ("journal_only", "inject")
STAGES = ("shadow", "active")
MIN_N_MIN = 30  # a gate cannot be set to promote on fewer scored setups than this
RISK_KEYS = ("capital", "risk_per_trade_pct", "max_daily_loss_pct", "max_open_positions", "max_trades_per_day",
             "max_leverage", "max_position_notional_pct", "max_stop_distance_pct")
GATE_DEFAULTS: dict[str, Any] = {"alpha": 0.05, "n_min": 100, "r_bounds": [-2.0, 4.0], "max_call_cost_r": 0.5,
                                 "demote_cum_r": -5.0}


class HarnessError(ValueError):
    """Raised with every problem found, each naming the file and key."""

    def __init__(self, problems: list[str]) -> None:
        super().__init__("; ".join(problems))
        self.problems = problems


@dataclass(frozen=True)
class Role:
    name: str
    label: str
    purpose: str
    may: str
    reads: tuple[str, ...]
    on_failure: str
    prompt_path: str
    prompt: str


@dataclass(frozen=True)
class Harness:
    id: str
    source: str  # "built-in" | "directory"
    path: str | None
    policy: dict[str, Any]
    gates: dict[str, Any]
    plans: dict[str, dict[str, Any]]
    roles: dict[str, Role]
    files: tuple[dict[str, str], ...]
    problems: tuple[str, ...] = ()  # why the directory in TB_HARNESS_DIR was not used, if it was not
    loaded_at: str = field(default="", compare=False)

    @property
    def valid(self) -> bool:
        return not self.problems

    @property
    def memory_mode(self) -> str:
        return str((self.policy.get("memory") or {}).get("mode", "journal_only"))

    def prompt(self, role: str) -> str:
        return self.roles[role].prompt

    def may(self, role: str) -> str:
        return self.roles[role].may

    def gate(self, role: str) -> dict[str, Any]:
        """The gate settings for a role: the defaults with the role's own values on top."""
        out = {**GATE_DEFAULTS, **(self.gates.get("defaults") or {})}
        mine = (self.gates.get("roles") or {}).get(role) or {}
        out.update(mine)
        out.setdefault("stage", "shadow")
        out.setdefault("scored", role in ("trader", "signal_reviewer"))
        return out

    def risk_overrides(self) -> dict[str, Any]:
        """The limits the policy asks for, in the form ``Settings.with_overrides`` takes."""
        return {k: v for k, v in (self.policy.get("risk") or {}).items() if k in RISK_KEYS}

    def desk_symbols(self) -> list[str]:
        return [str(s).strip().upper() for s in (self.policy.get("instruments") or {}).get("desk_symbols") or [] if str(s).strip()]

    def cost_inr(self, input_tokens: int, output_tokens: int) -> float:
        """What a call cost in rupees, from the prices in policy.toml. 0 when no price is set."""
        c = self.policy.get("llm_cost") or {}
        usd = (float(c.get("usd_per_mtok_in") or 0) * max(input_tokens, 0)
               + float(c.get("usd_per_mtok_out") or 0) * max(output_tokens, 0)) / 1_000_000
        return round(usd * float(c.get("usd_inr") or 0), 4)

    def stamp(self, row: dict[str, Any]) -> dict[str, Any]:
        row["harness_id"] = self.id
        return row


# Reading and checking


def _read(directory: Path) -> dict[str, str]:
    """Every harness file under ``directory``: {relative posix path: text with \\n line endings}."""
    out: dict[str, str] = {}
    for p in sorted(directory.rglob("*")):
        if p.is_file() and p.suffix in (".toml", ".md") and not any(part.startswith(".") for part in p.relative_to(directory).parts):
            out[p.relative_to(directory).as_posix()] = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    return out


def digest(files: dict[str, str]) -> str:
    h = hashlib.sha256()
    for path in sorted(files):
        h.update(path.encode() + b"\0" + files[path].encode() + b"\0")
    return h.hexdigest()[:12]


def _kind(path: str) -> str:
    if path == "policy.toml":
        return "policy"
    if path == "gates.toml":
        return "gates"
    if path.startswith("plans/"):
        return "plan"
    return "prompt" if path.endswith(".md") else "role"


def _number(problems: list[str], where: str, value: Any, lo: float | None = None, hi: float | None = None,
            why: str = "") -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        problems.append(f"{where}: must be a number")
        return None
    if (lo is not None and value < lo) or (hi is not None and value > hi):
        problems.append(f"{where}: {value} is outside {lo} to {hi}{' (' + why + ')' if why else ''}")
        return None
    return float(value)


def _check_policy(policy: dict[str, Any], problems: list[str]) -> None:
    from ..config import OVERRIDABLE

    mode = (policy.get("memory") or {}).get("mode", "journal_only")
    if mode not in MEMORY_MODES:
        problems.append(f"policy.toml [memory] mode: must be one of {MEMORY_MODES}, got {mode!r}")
    for key, value in (policy.get("risk") or {}).items():
        if key not in RISK_KEYS:
            problems.append(f"policy.toml [risk] {key}: not a limit this file can set; choose from {', '.join(RISK_KEYS)}")
            continue
        _, lo, hi = OVERRIDABLE[key]
        _number(problems, f"policy.toml [risk] {key}", value, lo, hi, "the ceiling is fixed in the code")
    symbols = (policy.get("instruments") or {}).get("desk_symbols", [])
    if not isinstance(symbols, list) or not all(isinstance(s, str) and s.replace("-", "").replace("&", "").isalnum() for s in symbols):
        problems.append("policy.toml [instruments] desk_symbols: must be a list of NSE trading symbols")
    elif len(symbols) > 60:
        problems.append("policy.toml [instruments] desk_symbols: at most 60 symbols")
    for key in ("usd_per_mtok_in", "usd_per_mtok_out", "usd_inr"):
        if key in (policy.get("llm_cost") or {}):
            _number(problems, f"policy.toml [llm_cost] {key}", policy["llm_cost"][key], 0, 1_000_000)


def _check_gates(gates: dict[str, Any], problems: list[str]) -> None:
    def check(where: str, g: dict[str, Any]) -> None:
        if "alpha" in g:
            _number(problems, f"{where} alpha", g["alpha"], 0.001, 0.2)
        if "n_min" in g:
            _number(problems, f"{where} n_min", g["n_min"], MIN_N_MIN, 100_000, f"at least {MIN_N_MIN} scored setups")
        if "max_call_cost_r" in g:
            _number(problems, f"{where} max_call_cost_r", g["max_call_cost_r"], 0, 5)
        if "demote_cum_r" in g:
            _number(problems, f"{where} demote_cum_r", g["demote_cum_r"], -1000, 0)
        if "r_bounds" in g:
            b = g["r_bounds"]
            if not (isinstance(b, list) and len(b) == 2 and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in b)
                    and b[0] < 0 < b[1]):
                problems.append(f"{where} r_bounds: must be [low, high] with low below zero and high above it")
        if "stage" in g and g["stage"] not in STAGES:
            problems.append(f"{where} stage: must be one of {STAGES}, got {g['stage']!r}")
        if "scored" in g and not isinstance(g["scored"], bool):
            problems.append(f"{where} scored: must be true or false")

    check("gates.toml [defaults]", gates.get("defaults") or {})
    for role, g in (gates.get("roles") or {}).items():
        if role not in DECISION_ROLES:
            problems.append(f"gates.toml [roles.{role}]: not a role that can affect a trade; choose from {', '.join(DECISION_ROLES)}")
            continue
        if not isinstance(g, dict):
            problems.append(f"gates.toml [roles.{role}]: must be a table")
            continue
        check(f"gates.toml [roles.{role}]", g)
        if role == "rebalance_reviewer" and g.get("scored"):
            problems.append("gates.toml [roles.rebalance_reviewer] scored: this role only postpones and is not scored in R")


def _check_plans(plans: dict[str, dict[str, Any]], problems: list[str]) -> None:
    from .. import daily
    from ..strategy import STRATEGIES

    inv = plans.get("investing")
    if inv is not None:
        name = inv.get("plan")
        if name not in daily.DAILY_NAMES:
            problems.append(f"plans/investing.toml plan: must be one of {', '.join(daily.DAILY_NAMES)}, got {name!r}")
        elif not isinstance(inv.get("params", {}), dict):
            problems.append("plans/investing.toml [params]: must be a table")
        else:
            spec = {p["name"]: p for c in daily.DAILY_CATALOG if c["name"] == name for p in c["params"]}
            for k, v in inv.get("params", {}).items():
                if k not in spec:
                    problems.append(f"plans/investing.toml [params] {k}: not a parameter of {name}")
                else:
                    _number(problems, f"plans/investing.toml [params] {k}", v, spec[k]["min"], spec[k]["max"])
    desk = plans.get("desk")
    if desk is not None:
        if desk.get("strategy", "ai") not in STRATEGIES:
            problems.append(f"plans/desk.toml strategy: must be one of {', '.join(sorted(STRATEGIES))}")
        p = desk.get("params", {})
        if not isinstance(p, dict):
            problems.append("plans/desk.toml [params]: must be a table")
        else:
            bounds = {"strict": (0, 1), "min_stop_pct": (0.1, 5.0), "min_prob": (0.0, 1.0)}
            for k, v in p.items():
                if k not in bounds:
                    problems.append(f"plans/desk.toml [params] {k}: not a desk setting; choose from {', '.join(bounds)}")
                else:
                    _number(problems, f"plans/desk.toml [params] {k}", v, *bounds[k])


def _check_roles(files: dict[str, str], parsed: dict[str, dict[str, Any]], problems: list[str]) -> dict[str, Role]:
    roles: dict[str, Role] = {}
    for name, most in ROLE_MAX.items():
        path = f"roles/{name}.toml"
        spec = parsed.get(path)
        if spec is None:
            problems.append(f"{path}: missing")
            continue
        may = spec.get("may")
        if may not in ALLOWED_MAY[most]:
            problems.append(f"{path} may: this role may at most {most!r} ({' or '.join(ALLOWED_MAY[most])}), got {may!r}")
        for key in ("label", "purpose", "on_failure"):
            if not isinstance(spec.get(key), str) or not spec[key].strip():
                problems.append(f"{path} {key}: must be a non-empty string")
        reads = spec.get("reads", [])
        if not isinstance(reads, list) or not all(isinstance(r, str) for r in reads):
            problems.append(f"{path} reads: must be a list of strings")
            reads = []
        prompt_name = spec.get("prompt", f"{name}.md")
        prompt_path = f"roles/{prompt_name}"
        if not isinstance(prompt_name, str) or "/" in prompt_name or prompt_path not in files:
            problems.append(f"{path} prompt: the file roles/{prompt_name} does not exist")
            continue
        text = files[prompt_path]
        if len(text.strip()) < 40:
            problems.append(f"{prompt_path}: the prompt is empty or too short to be one")
        if len(text) > 20_000:
            problems.append(f"{prompt_path}: longer than 20,000 characters")
        roles[name] = Role(name, str(spec.get("label", name)), str(spec.get("purpose", "")), str(may), tuple(reads),
                           str(spec.get("on_failure", "")), prompt_path, text)
    for path in parsed:
        if path.startswith("roles/") and path[len("roles/"):-len(".toml")] not in ROLE_MAX:
            problems.append(f"{path}: there is no role of that name; roles are {', '.join(ROLE_MAX)}")
    return roles


def load(directory: Path | str | None = None) -> Harness:
    """Read and check a harness. Raises ``HarnessError`` listing every problem; never returns a bad one."""
    from ..clock import now_ist

    builtin = directory is None
    root = DEFAULT_DIR if builtin else Path(directory)
    if not root.is_dir():
        raise HarnessError([f"{root}: not a directory"])
    files = _read(root)
    problems: list[str] = []
    parsed: dict[str, dict[str, Any]] = {}
    for path, text in files.items():
        if path.endswith(".toml"):
            try:
                parsed[path] = tomllib.loads(text)
            except tomllib.TOMLDecodeError as e:
                problems.append(f"{path}: not valid TOML ({e})")
    for required in ("policy.toml", "gates.toml"):
        if required not in files:
            problems.append(f"{required}: missing")
    policy, gates = parsed.get("policy.toml", {}), parsed.get("gates.toml", {})
    plans = {p[len("plans/"):-len(".toml")]: v for p, v in parsed.items() if p.startswith("plans/")}
    _check_policy(policy, problems)
    _check_gates(gates, problems)
    _check_plans(plans, problems)
    roles = _check_roles(files, parsed, problems)
    if problems:
        raise HarnessError(problems)
    listing = tuple({"path": p, "kind": _kind(p), "digest": hashlib.sha256(t.encode()).hexdigest()[:12], "text": t}
                    for p, t in sorted(files.items()))
    return Harness(digest(files), "built-in" if builtin else "directory", None if builtin else str(root), policy, gates,
                   plans, roles, listing, loaded_at=now_ist().isoformat())


# The harness in use


_cache: tuple[tuple, Harness] | None = None


def _signature() -> tuple:
    """Changes when the directory setting or any file's size or modification time changes."""
    chosen = (os.environ.get(ENV_DIR) or "").strip()
    stamps = []
    for root in ([Path(chosen)] if chosen else []) + [DEFAULT_DIR]:
        try:
            stamps.extend((str(p), p.stat().st_mtime_ns, p.stat().st_size) for p in sorted(root.rglob("*")) if p.is_file())
        except OSError:
            stamps.append((str(root), "unreadable"))
    return (chosen, tuple(stamps))


def current() -> Harness:
    """The harness in use: ``TB_HARNESS_DIR`` when it is set and passes every check, else the built-in one.

    Re-read when a file changes, so an edit takes effect on the worker's next pass.
    """
    global _cache
    sig = _signature()
    if _cache is not None and _cache[0] == sig:
        return _cache[1]
    chosen = sig[0]
    harness: Harness | None = None
    problems: tuple[str, ...] = ()
    if chosen:
        try:
            harness = load(chosen)
        except HarnessError as e:
            problems = tuple(e.problems)
            log.error("the harness in %s was not used (%d problem%s); running the built-in one: %s", chosen,
                      len(problems), "" if len(problems) == 1 else "s", "; ".join(problems))
        except OSError as e:
            problems = (f"{chosen}: could not be read ({e})",)
            log.error("the harness in %s could not be read; running the built-in one: %s", chosen, e)
    if harness is None:
        base = load(None)  # the shipped harness is tested; if it fails, that is a bug worth crashing on
        harness = Harness(base.id, base.source, base.path, base.policy, base.gates, base.plans, base.roles, base.files,
                          problems, base.loaded_at)
    _cache = (sig, harness)
    return harness


def current_id() -> str:
    return current().id


def reload() -> Harness:
    global _cache
    _cache = None
    return current()


def export(directory: Path | str) -> Path:
    """Copy the built-in harness to ``directory`` as a starting point for edits."""
    target = Path(directory)
    for path, text in _read(DEFAULT_DIR).items():
        out = target / path
        out.parent.mkdir(parents=True, exist_ok=True)
        if out.exists():
            raise FileExistsError(f"{out} already exists; export into an empty directory")
        out.write_text(text, encoding="utf-8")
    return target


__all__ = ["DECISION_ROLES", "Harness", "HarnessError", "Role", "ROLE_MAX", "current", "current_id", "digest", "export",
           "load", "reload"]
