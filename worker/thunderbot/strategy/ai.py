"""The AI ensemble: four rule-based setup generators, each setup scored by the trained model.

A generator proposes a trade with fixed entry, stop and target. The model estimates the chance that
it ends in profit after costs, from features of that bar. Setups below ``min_prob`` are dropped (and
remembered in ``last_candidates`` so the desk can journal what would have happened to them). What
passes goes to the LLM trader and then the risk manager, like any other signal.

Without a model every setup passes with no score; the LLM and the risk limits still apply.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Any

from ..ai import INDEX, features
from ..ai.gbm import predict_one
from ..models import Candle, Signal
from .base import Strategy
from .ema_pullback import EMAPullback, EMAPullbackParams
from .momentum import MomentumBurst, MomentumParams
from .orb import OpeningRangeBreakout, ORBParams
from .vwap_reversion import VWAPReversion, VWAPReversionParams


@dataclass
class AIParams:
    # 0 = paper learning: take the best-scored setups even though history says they lose after costs,
    # so there is a record to learn from. 1 = take a setup only when the model expects it to make money.
    strict: int = 0
    min_prob: float = 0.0  # an explicit probability floor; 0 leaves the floor to the model's own report
    # Stops closer than this are widened (target moved to keep the same reward-to-risk). Charges and
    # slippage are about 0.2% of a position, so a 0.3% stop loses most of its risk to costs alone.
    min_stop_pct: float = 0.8
    allow_short: bool = True


def widen(sig: Signal, min_stop_pct: float) -> Signal:
    """The same setup with its stop at least ``min_stop_pct`` away and the target scaled to match."""
    risk = max(sig.risk_per_share, sig.entry * min_stop_pct / 100.0)
    if risk <= sig.risk_per_share + 1e-9:
        return sig
    sign, rr = sig.side.sign, sig.reward_risk
    return replace(sig, stop=round(sig.entry - sign * risk, 2), target=round(sig.entry + sign * rr * risk, 2))


def make_generators(allow_short: bool = True) -> list[Strategy]:
    return [
        OpeningRangeBreakout(ORBParams(allow_short=allow_short)),
        VWAPReversion(VWAPReversionParams(allow_short=allow_short)),
        EMAPullback(EMAPullbackParams(allow_short=allow_short)),
        MomentumBurst(MomentumParams(allow_short=allow_short)),
    ]


@dataclass
class Candidate:
    signal: Signal  # strategy == "ai"; features carry the generator, the score and the model inputs
    generator: str
    prob: float | None
    taken: bool


class AIEnsemble(Strategy):
    name = "ai"
    label = "AI desk (ML-scored setups)"
    description = (
        "Runs four setup generators at once (opening-range breakout, VWAP reversion, EMA pullback, momentum "
        "burst) and scores every setup with a model trained on what such setups did in the last 60 days, "
        "after costs. Only setups above the probability floor go on to the LLM trader and the risk limits."
    )
    params_cls = AIParams
    param_specs = [
        {"name": "strict", "label": "Only trade when the model expects a profit (1 = yes)", "type": "int", "min": 0, "max": 1, "step": 1},
        {"name": "min_prob", "label": "Probability floor (0 = set by the model)", "type": "float", "min": 0.0, "max": 0.9, "step": 0.01},
        {"name": "min_stop_pct", "label": "Minimum stop distance %", "type": "float", "min": 0.0, "max": 3.0, "step": 0.1},
    ]

    def __init__(self, params: AIParams | None = None) -> None:
        self.p = params or AIParams()
        self.generators = make_generators(self.p.allow_short)
        self.model: dict[str, Any] | None = None
        self.model_id: str | None = None
        self._index: list[Candle] = []
        self.last_candidates: list[Candidate] = []

    # Wiring

    def set_model(self, model: dict[str, Any] | None, model_id: str | None = None) -> None:
        self.model = model if model and model.get("trees") else None
        self.model_id = model_id if self.model else None

    def refresh(self, store: Any) -> None:
        """Load the active model from the journal (called at start and at each new day by the engine)."""
        from ..ai.train import load_active_model

        try:
            row = load_active_model(store)
        except Exception:
            row = None
        if row:
            self.set_model(row.get("model"), row.get("id"))

    def observe_index(self, bars: Sequence[Candle]) -> None:
        self._index = list(bars)

    def reset_day(self) -> None:
        for g in self.generators:
            g.reset_day()
        self._index = []
        self.last_candidates = []

    @property
    def _fired(self) -> set[str]:  # the engine carries this across a mid-day strategy switch
        return set().union(*(getattr(g, "_fired", set()) for g in self.generators))

    @_fired.setter
    def _fired(self, value: set[str]) -> None:
        for g in self.generators:
            if hasattr(g, "_fired"):
                g._fired = set(value)

    # Scoring

    @property
    def min_stop_pct(self) -> float:
        """The model was trained on setups widened to its own minimum; trade the same shape."""
        if self.model is not None:
            return float((self.model.get("setup") or {}).get("min_stop_pct", self.p.min_stop_pct))
        return self.p.min_stop_pct

    @property
    def floor(self) -> float | None:
        """The probability a setup must reach. None means nothing passes (strict, and no group is profitable)."""
        if self.model is None:
            return 0.0
        if self.p.min_prob > 0:
            return self.p.min_prob
        policy = self.model.get("policy") or {}
        return policy.get("strict") if self.p.strict else policy.get("learn", 0.0)

    def score(self, feats: dict[str, float]) -> float | None:
        if self.model is None:
            return None
        return predict_one(self.model, features.vector(feats, self.model["features"]))

    def expected_r(self, prob: float | None) -> float | None:
        ev = (self.model or {}).get("policy", {}).get("ev") if prob is not None else None
        return None if not ev else round(ev[0] + ev[1] * prob, 3)

    def candidates(self, symbol: str, session_bars: Sequence[Candle], prior_bars: Sequence[Candle] = ()) -> list[Candidate]:
        out: list[Candidate] = []
        for g in self.generators:
            sig = g.on_bar(symbol, session_bars, prior_bars)
            if sig is None:
                continue
            sig = widen(sig, self.min_stop_pct)
            feats = features.build(sig, session_bars, prior_bars, self._index, generator=g.name)
            prob = self.score(feats)
            ai_sig = replace(sig, strategy=self.name, features={
                **{k: v for k, v in sig.features.items() if v is not None},
                "generator": g.name, "ml_prob": None if prob is None else round(prob, 4),
                "ml_expected_r": self.expected_r(prob), "ml_model": self.model_id, "x": feats,
            })
            floor = self.floor
            out.append(Candidate(ai_sig, g.name, prob, taken=prob is None or (floor is not None and prob >= floor)))
        return out

    def on_bar(self, symbol: str, session_bars: Sequence[Candle], prior_bars: Sequence[Candle] = ()) -> Signal | None:
        if symbol == INDEX:
            self.observe_index(session_bars)
            return None
        cands = self.candidates(symbol, session_bars, prior_bars)
        if not cands:
            return None
        # One trade per symbol per bar: the highest-scored setup stands for the bar, the rest are journaled.
        cands.sort(key=lambda c: -(c.prob if c.prob is not None else 0.0))
        best = cands[0]
        for c in cands[1:]:
            c.taken = False
        self.last_candidates.extend(cands)
        return best.signal if best.taken else None
