"""The confidence sequence the LLM gates rest on (thunderbot/stats/confseq.py)."""

from __future__ import annotations

import math
import random

import pytest

from thunderbot.stats.confseq import ConfidenceSequence, sequence


def test_matches_a_hand_computed_sequence():
    # alpha = 0.05, observations 1.0 then 0.0 on [0, 1]. By the formulas in the module docstring:
    #   log(2/alpha) = log 40 = 3.688879
    #   t=1: sigma2_0 = 1/4, so lambda_1 = min(sqrt(2*3.688879 / (0.25*1*log 2)), 1/2) = 1/2
    #        v_1 = 4*(1 - 1/2)^2 = 1,  psi_E(1/2) = (log 2 - 1/2)/4 = 0.0482868
    #        centre = 1.0,  radius = (3.688879 + 0.0482868) / 0.5 = 7.474332
    #   then mu_1 = (1/2 + 1)/2 = 0.75 and sigma2_1 = (1/4 + (1 - 0.75)^2)/2 = 0.15625
    #   t=2: lambda_2 = min(sqrt(2*3.688879 / (0.15625*2*log 3)), 1/2) = 1/2
    #        v_2 = 4*(0 - 0.75)^2 = 2.25
    #        centre = (0.5*1 + 0.5*0)/1 = 0.5
    #        radius = (3.688879 + 1*0.0482868 + 2.25*0.0482868) / 1.0 = 3.845812
    first, second = sequence([1.0, 0.0], 0.0, 1.0, alpha=0.05)
    assert first.centre == pytest.approx(1.0) and first.radius == pytest.approx(7.474332, abs=1e-5)
    assert second.centre == pytest.approx(0.5) and second.radius == pytest.approx(3.845812, abs=1e-5)
    assert (second.lower, second.upper) == (0.0, 1.0)  # nothing is known yet: the whole range
    assert second.mean == pytest.approx(0.5) and second.n == 2


def test_true_mean_stays_inside_the_whole_path():
    """Valid at every look: over many simulated paths the truth is inside *every* interval of a path
    at least 95% of the time, however the data are distributed."""
    rng = random.Random(11)
    paths, steps, missed = 400, 400, 0
    for _ in range(paths):
        a, b = rng.choice([(2, 5), (5, 2), (0.5, 0.5), (8, 8)])
        mu = a / (a + b)
        cs = ConfidenceSequence(0.0, 1.0, alpha=0.05)
        inside = True
        for _ in range(steps):
            bound = cs.add(rng.betavariate(a, b))
            inside = inside and bound.lower <= mu <= bound.upper
        missed += not inside
    assert missed / paths <= 0.05


def test_tightens_with_more_observations_and_never_widens():
    rng = random.Random(3)
    bounds = sequence([rng.uniform(0.3, 0.9) for _ in range(600)], 0.0, 1.0)
    widths = [b.upper - b.lower for b in bounds]
    assert all(later <= earlier + 1e-12 for earlier, later in zip(widths, widths[1:], strict=False))  # running intersection
    assert widths[599] < widths[99] < widths[9]
    assert widths[599] < 0.15 and bounds[-1].lower <= 0.6 <= bounds[-1].upper


def test_other_ranges_are_rescaled_and_values_outside_are_clipped():
    values = [-1.0, 0.5, 2.0, 0.0]
    scaled = sequence([(v + 2) / 6 for v in values], 0.0, 1.0)
    for a, b in zip(sequence(values, -2.0, 4.0), scaled, strict=True):
        assert a.lower == pytest.approx(-2 + 6 * b.lower) and a.upper == pytest.approx(-2 + 6 * b.upper)
    assert sequence([99.0], -2.0, 4.0)[0].mean == 4.0  # clipped to the range it promised


def test_can_be_saved_and_carried_on():
    rng = random.Random(5)
    values = [rng.random() for _ in range(80)]
    whole = sequence(values, 0.0, 1.0)[-1]
    first = ConfidenceSequence(0.0, 1.0)
    for v in values[:30]:
        first.add(v)
    resumed = ConfidenceSequence.from_state(first.state())
    for v in values[30:]:
        last = resumed.add(v)
    assert (last.lower, last.upper, last.mean, last.n) == pytest.approx((whole.lower, whole.upper, whole.mean, whole.n))
    fresh = ConfidenceSequence.from_state(ConfidenceSequence(0.0, 1.0).state())
    assert math.isinf(fresh.bound.radius) and fresh.bound.n == 0


def test_rejects_nonsense():
    with pytest.raises(ValueError):
        ConfidenceSequence(1.0, 1.0)
    with pytest.raises(ValueError):
        ConfidenceSequence(0.0, 1.0, alpha=0.0)
