from __future__ import annotations

import dataclasses
from typing import Any

from .base import Strategy
from .ema_pullback import EMAPullback
from .orb import OpeningRangeBreakout
from .vwap_reversion import VWAPReversion

STRATEGIES: dict[str, type[Strategy]] = {
    cls.name: cls for cls in (OpeningRangeBreakout, VWAPReversion, EMAPullback)
}


def coerce_params(name: str, params: dict[str, Any] | None) -> dict[str, Any]:
    """Validate UI-supplied params against the strategy's spec: known keys only, typed, clamped to [min, max]."""
    cls = STRATEGIES[name]
    out: dict[str, Any] = {}
    specs = {s["name"]: s for s in cls.param_specs}
    for key, value in (params or {}).items():
        spec = specs.get(key)
        if spec is None or value is None or value == "":
            continue
        v = float(value)
        v = min(max(v, spec["min"]), spec["max"])
        out[key] = int(round(v)) if spec["type"] == "int" else v
    return out


def build_strategy(name: str, params: dict[str, Any] | None = None, allow_short: bool = True) -> Strategy:
    if name not in STRATEGIES:
        raise ValueError(f"unknown strategy {name!r}; choose from {sorted(STRATEGIES)}")
    cls = STRATEGIES[name]
    kwargs = coerce_params(name, params)
    if "allow_short" in {f.name for f in dataclasses.fields(cls.params_cls)}:
        kwargs["allow_short"] = allow_short
    return cls(cls.params_cls(**kwargs))


def catalog() -> list[dict[str, Any]]:
    """Strategy metadata for the dashboard: names, descriptions, param specs with defaults."""
    out = []
    for cls in STRATEGIES.values():
        defaults = cls.params_cls()
        out.append({
            "name": cls.name,
            "label": cls.label,
            "description": cls.description,
            "params": [{**spec, "default": getattr(defaults, spec["name"])} for spec in cls.param_specs],
        })
    return out


__all__ = ["Strategy", "OpeningRangeBreakout", "VWAPReversion", "EMAPullback", "STRATEGIES",
           "build_strategy", "catalog", "coerce_params"]
