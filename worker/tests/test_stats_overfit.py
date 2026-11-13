"""Deflated Sharpe ratio and probability of backtest overfitting (thunderbot/stats/overfit.py)."""

from __future__ import annotations

import math
import random
from statistics import NormalDist

import pytest

from thunderbot.stats import overfit


def test_deflated_sharpe_matches_a_worked_example():
    # Returns alternate +1.1% and -0.9%: mean 0.1%, standard deviation 1.0%, so the per-day Sharpe is 0.1.
    # A two-point symmetric series has skewness 0 and kurtosis 1, so the denominator
    #   sqrt(1 - g3*SR + (g4 - 1)/4 * SR^2) is exactly 1, and with T = 100 returns
    #   DSR = Phi((SR - SR0) * sqrt(99)).
    returns = [0.011, -0.009] * 50
    mean, sd, skew, kurt = overfit.moments(returns)
    assert (mean, sd, skew, kurt) == pytest.approx((0.001, 0.01, 0.0, 1.0))
    assert overfit.sharpe(returns) == pytest.approx(0.1)

    # One trial: nothing to deflate, SR0 = 0, DSR = Phi(0.1 * 9.949874) = Phi(0.994987) = 0.840129.
    assert overfit.deflated_sharpe(returns, 1, 0.0) == pytest.approx(0.840129, abs=1e-6)

    # Ten trials whose Sharpe ratios have variance 0.0025 (standard deviation 0.05):
    #   Z(1 - 1/10) = 1.281552,  Z(1 - 1/(10e)) = Z(0.963212) = 1.789242,  gamma = 0.577216
    #   SR0 = 0.05 * (0.422784 * 1.281552 + 0.577216 * 1.789242) = 0.05 * 1.574598 = 0.078730
    #   DSR = Phi((0.1 - 0.078730) * 9.949874) = Phi(0.211634) = 0.583804
    assert overfit.expected_max_sharpe(10, 0.0025) == pytest.approx(0.078730, abs=1e-6)
    assert overfit.deflated_sharpe(returns, 10, 0.0025) == pytest.approx(0.583804, abs=1e-6)


def test_more_trials_always_deflate_more():
    returns = [0.011, -0.009] * 50
    scores = [overfit.deflated_sharpe(returns, n, 0.0025) for n in (1, 2, 10, 60, 600)]
    assert scores == sorted(scores, reverse=True) and scores[-1] < 0.3
    assert overfit.expected_max_sharpe(1, 0.01) == 0.0 and overfit.expected_max_sharpe(50, 0.0) == 0.0


def test_skew_and_fat_tails_are_charged_for():
    # Same Sharpe, but returns that lose rarely and badly are less certain to be good.
    base = overfit.probabilistic_sharpe(0.1, 0.0, 100, 0.0, 3.0)
    assert base == pytest.approx(NormalDist().cdf(0.1 * math.sqrt(99) / math.sqrt(1 + 0.5 * 0.01)))
    assert overfit.probabilistic_sharpe(0.1, 0.0, 100, -2.0, 12.0) < base
    assert overfit.probabilistic_sharpe(0.1, 0.0, 1, 0.0, 3.0) is None


def test_degenerate_returns():
    assert overfit.deflated_sharpe([0.0] * 30, 10, 0.01) == 0.0  # never traded: no evidence of anything
    assert overfit.deflated_sharpe([], 10, 0.01) is None
    assert overfit.sharpe([0.01] * 5) == 0.0


def test_pbo_is_high_for_noise_and_low_for_a_real_edge():
    rng = random.Random(7)
    noise = [[rng.gauss(0, 0.01) for _ in range(12)] for _ in range(240)]
    out = overfit.pbo(noise, blocks=8)
    assert out["blocks"] == 8 and out["splits"] == 70  # 8 choose 4
    # With no edge anywhere, whichever setting won one half of the days did so by luck, and luck in one
    # half is paid back in the other, so the winner lands in the bottom half at least as often as not.
    assert out["pbo"] >= 0.4

    # One setting with a real, steady edge among eleven with none: the in-sample winner keeps winning.
    edge = [[rng.gauss(0.004 if j == 0 else 0.0, 0.01) for j in range(12)] for _ in range(240)]
    assert overfit.pbo(edge, blocks=8)["pbo"] <= 0.05


def test_pbo_needs_enough_days_and_settings():
    rng = random.Random(1)
    assert overfit.pbo([[rng.random()] for _ in range(100)]) is None  # one setting: nothing to pick between
    assert overfit.pbo([[rng.random(), rng.random()] for _ in range(10)]) is None  # too few days for four blocks
    assert overfit.blocks_for(40) == 8 and overfit.blocks_for(20) == 4 and overfit.blocks_for(25) == 6
    assert overfit.blocks_for(15) == 0
    small = overfit.pbo([[rng.gauss(0, 1), rng.gauss(0, 1)] for _ in range(20)])
    assert small["blocks"] == 4 and small["splits"] == 6
