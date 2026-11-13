"""A confidence sequence for the mean of bounded observations that is valid at every look.

An ordinary confidence interval is valid at one sample size chosen in advance. Checking a result every
day and stopping when it looks good breaks that promise. A confidence sequence does not have the
problem: with probability at least ``1 - alpha`` the true mean lies inside *every* interval of the
sequence at once, so the owner may look as often as they like and act the moment a bound crosses zero.

This is the predictable plug-in empirical-Bernstein confidence sequence of Waudby-Smith and Ramdas,
"Estimating means of bounded random variables by betting" (JRSS-B 2024, Theorem 2), which builds on
Howard, Ramdas, McAuliffe and Sekhon (2021). For observations ``X_1, X_2, ...`` in ``[0, 1]``::

    mu_hat_t    = (1/2 + sum_{i<=t} X_i) / (t + 1)
    sigma2_hat_t = (1/4 + sum_{i<=t} (X_i - mu_hat_i)^2) / (t + 1)
    lambda_t    = min( sqrt( 2 log(2/alpha) / (sigma2_hat_{t-1} * t * log(t + 1)) ), c )      c = 1/2
    v_i         = 4 (X_i - mu_hat_{i-1})^2
    psi_E(l)    = (-log(1 - l) - l) / 4

    C_t = sum_i lambda_i X_i / sum_i lambda_i  +/-  ( log(2/alpha) + sum_i v_i psi_E(lambda_i) ) / sum_i lambda_i

with ``mu_hat_0 = 1/2`` and ``sigma2_hat_0 = 1/4``. ``lambda_t`` uses only observations before ``t``,
which is what makes the bound valid. The running intersection of the ``C_t`` is taken, since the truth
lies in all of them. Observations in another range ``[lo, hi]`` are rescaled to ``[0, 1]`` and the
bounds mapped back.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

CAP = 0.5  # the largest bet; any value in (0, 1) is valid


@dataclass(frozen=True)
class Bound:
    n: int
    mean: float  # the plain average of the observations so far
    lower: float
    upper: float
    centre: float  # the lambda-weighted average the interval is built around
    radius: float  # its half-width before the running intersection


class ConfidenceSequence:
    """Feed observations one at a time with ``add``; read ``bound`` whenever you like."""

    def __init__(self, lo: float, hi: float, alpha: float = 0.05) -> None:
        if not hi > lo:
            raise ValueError("hi must be above lo")
        if not 0 < alpha < 1:
            raise ValueError("alpha must be between 0 and 1")
        self.lo, self.hi, self.alpha = lo, hi, alpha
        self.n = 0
        self._sum = 0.0  # of the rescaled observations
        self._sq = 0.0  # of (X_i - mu_hat_i)^2
        self._mu = 0.5  # mu_hat_{t-1}
        self._var = 0.25  # sigma2_hat_{t-1}
        self._lam_sum = 0.0
        self._lam_x = 0.0
        self._v_psi = 0.0
        self._lower, self._upper = 0.0, 1.0  # running intersection, in [0, 1]
        self._centre, self._radius = 0.5, math.inf

    def add(self, value: float) -> Bound:
        x = (min(max(value, self.lo), self.hi) - self.lo) / (self.hi - self.lo)
        t = self.n + 1
        lam = min(math.sqrt(2 * math.log(2 / self.alpha) / (self._var * t * math.log(t + 1))), CAP)
        self._lam_sum += lam
        self._lam_x += lam * x
        self._v_psi += 4 * (x - self._mu) ** 2 * ((-math.log(1 - lam) - lam) / 4)
        self._centre = self._lam_x / self._lam_sum
        self._radius = (math.log(2 / self.alpha) + self._v_psi) / self._lam_sum
        self._lower = max(self._lower, self._centre - self._radius)
        self._upper = min(self._upper, self._centre + self._radius)
        # Now bring the plug-in estimates up to date for the next observation.
        self.n = t
        self._sum += x
        self._mu = (0.5 + self._sum) / (t + 1)
        self._sq += (x - self._mu) ** 2
        self._var = (0.25 + self._sq) / (t + 1)
        return self.bound

    def state(self) -> dict[str, float]:
        """Everything needed to carry on later from where this sequence stopped."""
        return {"lo": self.lo, "hi": self.hi, "alpha": self.alpha, "n": self.n, "sum": self._sum, "sq": self._sq,
                "mu": self._mu, "var": self._var, "lam_sum": self._lam_sum, "lam_x": self._lam_x, "v_psi": self._v_psi,
                "lower": self._lower, "upper": self._upper, "centre": self._centre,
                "radius": self._radius if math.isfinite(self._radius) else -1.0}

    @classmethod
    def from_state(cls, st: dict[str, float]) -> "ConfidenceSequence":
        cs = cls(float(st["lo"]), float(st["hi"]), float(st["alpha"]))
        cs.n = int(st["n"])
        cs._sum, cs._sq, cs._mu, cs._var = float(st["sum"]), float(st["sq"]), float(st["mu"]), float(st["var"])
        cs._lam_sum, cs._lam_x, cs._v_psi = float(st["lam_sum"]), float(st["lam_x"]), float(st["v_psi"])
        cs._lower, cs._upper, cs._centre = float(st["lower"]), float(st["upper"]), float(st["centre"])
        cs._radius = float(st["radius"]) if float(st["radius"]) >= 0 else math.inf
        return cs

    @property
    def bound(self) -> Bound:
        span = self.hi - self.lo
        mean = self.lo + span * (self._sum / self.n) if self.n else (self.lo + self.hi) / 2
        lower, upper = self._lower, self._upper
        if lower > upper:  # can only happen on the alpha-probability event; report the crossing point
            lower = upper = (lower + upper) / 2
        return Bound(self.n, mean, self.lo + span * lower, self.lo + span * upper, self.lo + span * self._centre,
                     span * self._radius)


def sequence(values: list[float], lo: float, hi: float, alpha: float = 0.05) -> list[Bound]:
    cs = ConfidenceSequence(lo, hi, alpha)
    return [cs.add(v) for v in values]
