"""Two corrections for trying many settings on the same history.

**Deflated Sharpe ratio** (Bailey and Lopez de Prado, 2014). Try enough settings and one will look good
by luck. If ``N`` settings were tried and their Sharpe ratios vary with variance ``V``, the best of
``N`` *skill-less* settings is expected to reach about::

    SR0 = sqrt(V) * ( (1 - g) * Z(1 - 1/N) + g * Z(1 - 1/(N e)) )        g = 0.5772..., Z = normal quantile

The deflated Sharpe ratio is the probability that a setting's true Sharpe is above that bar, given
its ``T`` returns, their skewness ``g3`` and kurtosis ``g4``::

    DSR = Phi( (SR - SR0) * sqrt(T - 1) / sqrt(1 - g3 * SR + (g4 - 1)/4 * SR^2) )

All Sharpe ratios here are per period (per day), not annualised. A setting is worth a second look
when DSR is at least 0.95.

**Probability of backtest overfitting** by combinatorially symmetric cross-validation (Bailey, Borwein,
Lopez de Prado and Zhu). Cut the days into ``S`` blocks. For every way of choosing half the blocks as
"in sample", pick the setting that did best there and see where it ranks on the other half. The
probability of overfitting is the share of splits in which the in-sample winner landed in the bottom
half out of sample. Near 0 the winner keeps winning; near 0.5 picking the winner is no better than
picking at random; above 0.5 it is worse.
"""

from __future__ import annotations

import itertools
import math
from statistics import NormalDist

EULER = 0.5772156649015329
_N = NormalDist()


def moments(returns: list[float]) -> tuple[float, float, float, float]:
    """Mean, standard deviation, skewness and kurtosis (3 for a normal distribution) of ``returns``."""
    n = len(returns)
    if n == 0:
        return 0.0, 0.0, 0.0, 3.0
    mean = sum(returns) / n
    m2 = sum((r - mean) ** 2 for r in returns) / n
    if m2 <= 0:
        return mean, 0.0, 0.0, 3.0
    sd = math.sqrt(m2)
    m3 = sum((r - mean) ** 3 for r in returns) / n
    m4 = sum((r - mean) ** 4 for r in returns) / n
    return mean, sd, m3 / sd ** 3, m4 / m2 ** 2


def sharpe(returns: list[float]) -> float:
    """Per-period Sharpe ratio: mean over standard deviation. 0 when the returns do not vary."""
    mean, sd, _, _ = moments(returns)
    return mean / sd if sd > 0 else 0.0


def expected_max_sharpe(trials: int, variance: float) -> float:
    """The Sharpe ratio the best of ``trials`` skill-less settings is expected to show."""
    if trials <= 1 or variance <= 0:
        return 0.0
    return math.sqrt(variance) * ((1 - EULER) * _N.inv_cdf(1 - 1 / trials) + EULER * _N.inv_cdf(1 - 1 / (trials * math.e)))


def probabilistic_sharpe(sr: float, benchmark: float, n: int, skew: float, kurt: float) -> float | None:
    """The probability that the true Sharpe is above ``benchmark``. None with fewer than two returns."""
    if n < 2:
        return None
    denom = 1 - skew * sr + (kurt - 1) / 4 * sr * sr
    if denom <= 0:
        return None
    return _N.cdf((sr - benchmark) * math.sqrt(n - 1) / math.sqrt(denom))


def deflated_sharpe(returns: list[float], trials: int, sharpe_variance: float) -> float | None:
    """The deflated Sharpe ratio of one setting's returns, given how many settings were tried in all
    and how much their Sharpe ratios varied."""
    _, sd, skew, kurt = moments(returns)
    if sd <= 0:
        return 0.0 if len(returns) >= 2 else None
    return probabilistic_sharpe(sharpe(returns), expected_max_sharpe(trials, sharpe_variance), len(returns), skew, kurt)


def blocks_for(days: int, wanted: int = 8, min_per_block: int = 4) -> int:
    """The largest even number of blocks up to ``wanted`` that leaves ``min_per_block`` days in each. 0 if none."""
    s = wanted - wanted % 2
    while s >= 4 and days // s < min_per_block:
        s -= 2
    return s if s >= 4 else 0


def pbo(matrix: list[list[float]], blocks: int = 8) -> dict[str, float | int] | None:
    """Probability of backtest overfitting for a days-by-settings matrix of returns.

    Returns ``{"pbo", "splits", "blocks", "median_logit"}``, or None when there are fewer than two
    settings or too few days to cut into four blocks.
    """
    days = len(matrix)
    n = len(matrix[0]) if days else 0
    s = blocks_for(days, blocks)
    if n < 2 or s == 0:
        return None
    size = days // s  # any days left over at the end are dropped, as in the paper
    cols = [[row[j] for row in matrix[: size * s]] for j in range(n)]
    chunk = [[col[b * size:(b + 1) * size] for b in range(s)] for col in cols]  # chunk[setting][block]

    def score(j: int, picks: tuple[int, ...]) -> float:
        return sharpe([r for b in picks for r in chunk[j][b]])

    logits = []
    for ins in itertools.combinations(range(s), s // 2):
        out = tuple(b for b in range(s) if b not in ins)
        best = max(range(n), key=lambda j: score(j, ins))
        oos = [score(j, out) for j in range(n)]
        # Rank of the in-sample winner out of sample, 1 = worst; ties share the middle rank.
        below = sum(1 for x in oos if x < oos[best])
        equal = sum(1 for x in oos if x == oos[best])
        w = (below + (equal + 1) / 2) / (n + 1)
        logits.append(math.log(w / (1 - w)))
    logits.sort()
    return {"pbo": sum(1 for x in logits if x <= 0) / len(logits), "splits": len(logits), "blocks": s,
            "median_logit": logits[len(logits) // 2]}
