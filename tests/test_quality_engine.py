"""Tests for the pure-math quality engine (E9a).

Edge cases named by the roadmap: q=0 / q=100 (clamped, never inf), q=99.99, a
weak-input-through-strong-utility case, a strong-input-through-lossy-utility
case, missing/conflicting components, and a logit(sigmoid) round-trip identity.

Spec under test: docs/knowledge/04_matrx_quality_model.md (cited as "04").
"""

from __future__ import annotations

import math

import pytest

from matrx_utils.quality_engine import (
    DEFAULT_COMPOSITE_WEIGHTS,
    EPSILON,
    QualityVector,
    adjust,
    clamp_q,
    compute_composite_quality,
    derive,
    from_visible_score,
    logit,
    preserve,
    sigmoid,
    to_visible_score,
    weighted_geometric_mean,
)

TOL = 1e-9


# --------------------------------------------------------------------------- #
# 04 §4.1 — clamping at the edges: 0 and 100 must never produce ±inf.          #
# --------------------------------------------------------------------------- #
def test_visible_zero_clamps_not_inf():
    q = from_visible_score(0)
    assert q == EPSILON
    z = logit(q)
    assert math.isfinite(z)
    # 04 §4.1: "0 becomes 0.0001 for math".
    assert q == pytest.approx(0.0001, abs=TOL)


def test_visible_hundred_clamps_not_inf():
    q = from_visible_score(100)
    assert q == 1.0 - EPSILON
    z = logit(q)
    assert math.isfinite(z)
    # 04 §4.1: "100 becomes 0.9999 for math".
    assert q == pytest.approx(0.9999, abs=TOL)


def test_clamp_q_bounds():
    assert clamp_q(0.0) == EPSILON
    assert clamp_q(1.0) == 1.0 - EPSILON
    assert clamp_q(-5.0) == EPSILON
    assert clamp_q(5.0) == 1.0 - EPSILON
    assert clamp_q(0.5) == 0.5


def test_visible_fifty_midpoint():
    q = from_visible_score(50)
    assert q == pytest.approx(0.5, abs=TOL)
    # 04 §6.1: logit(0.5) == 0.
    assert logit(q) == pytest.approx(0.0, abs=TOL)


def test_visible_9999():
    # q=99.99 — just inside the clamp, must stay finite and below 0.9999 clamp.
    q = from_visible_score(99.99)
    assert q == pytest.approx(0.9999, abs=TOL)  # 99.99/100 == 0.9999, exactly at ceiling
    assert math.isfinite(logit(q))


def test_to_visible_round_trip_edges():
    assert to_visible_score(from_visible_score(0)) == 0
    assert to_visible_score(from_visible_score(100)) == 100
    assert to_visible_score(from_visible_score(87)) == 87


# --------------------------------------------------------------------------- #
# 04 §6.1 — logit(sigmoid(z)) == z within tolerance (round-trip identity).     #
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("z", [-8.0, -2.0, -0.4, 0.0, 0.4, 1.0, 2.0, 8.0])
def test_logit_sigmoid_round_trip(z):
    # Stay within the clamp window so the round-trip is exact (|z| ~< 9.21 for
    # eps=1e-4). 04 §6.1 definitions.
    assert logit(sigmoid(z)) == pytest.approx(z, abs=1e-9)


def test_sigmoid_clamps_extreme_z():
    # Very large |z| saturates at the clamp, never 0 or 1 exactly (04 §20).
    assert sigmoid(1000.0) == 1.0 - EPSILON
    assert sigmoid(-1000.0) == EPSILON


# --------------------------------------------------------------------------- #
# 04 §9 — preserve: q_out == q_in.                                             #
# --------------------------------------------------------------------------- #
def test_preserve_is_identity():
    q = from_visible_score(99)
    assert preserve(q) == clamp_q(q)
    assert to_visible_score(preserve(from_visible_score(99))) == 99


# --------------------------------------------------------------------------- #
# 04 §10 — adjust: weak input lifted by a strong-positive validation impact.   #
# --------------------------------------------------------------------------- #
def test_adjust_strong_upgrade_lifts_weak_input():
    # Weak artifact (visible 55) + strong upgrade (+2.00 log-odds, 04 §10.1).
    q_in = from_visible_score(55)
    q_out = adjust(q_in, +2.00)
    assert q_out > q_in
    # 55 -> z≈0.2007 -> +2 -> z≈2.2007 -> sigmoid≈0.9003 ≈ visible 90.
    assert to_visible_score(q_out) == 90


def test_adjust_downgrade_lowers():
    q_in = from_visible_score(80)
    q_out = adjust(q_in, -2.00)
    assert q_out < q_in


def test_adjust_no_change_preset():
    q_in = from_visible_score(70)
    assert adjust(q_in, 0.0) == pytest.approx(clamp_q(q_in), abs=TOL)


# --------------------------------------------------------------------------- #
# 04 §11 — derive: low input through a strong/good utility rises; high input   #
# through a lossy utility (low target) falls.                                  #
# --------------------------------------------------------------------------- #
def test_derive_weak_input_strong_utility_lifts():
    # Weak input (40) through a strong utility aiming high (target 90, strength
    # 80) should pull UP toward the target. 04 §11 / §11.1.
    q_in = from_visible_score(40)
    q_out = derive(q_in, from_visible_score(90), transformation_strength=80)
    assert q_out > q_in
    assert to_visible_score(q_out) > 40


def test_derive_strong_input_lossy_utility_pulls_down():
    # 04 §17.3: a pristine input (99) through a lossy summarizer (target 80,
    # strength 80) should drop toward the low target.
    q_in = from_visible_score(99)
    q_out = derive(q_in, from_visible_score(80), transformation_strength=80)
    assert q_out < q_in
    assert to_visible_score(q_out) < 99
    # With strength 80, output sits much closer to the target (80) than input.
    assert to_visible_score(q_out) < 90


def test_derive_strength_zero_is_input_dominated():
    # 04 §7.2: transformation_strength=0 -> input dominates completely.
    q_in = from_visible_score(95)
    q_out = derive(q_in, from_visible_score(10), transformation_strength=0)
    assert q_out == pytest.approx(clamp_q(q_in), abs=TOL)


def test_derive_strength_hundred_is_target():
    # 04 §7.2: strength=100 -> utility output profile dominates.
    q_out = derive(from_visible_score(95), from_visible_score(40), transformation_strength=100)
    assert q_out == pytest.approx(from_visible_score(40), abs=TOL)


def test_derive_strength_clamped_above_100():
    # Defensive: out-of-range strength is clamped to [0, 100]/100 (04 §20).
    a = derive(from_visible_score(50), from_visible_score(80), transformation_strength=150)
    b = derive(from_visible_score(50), from_visible_score(80), transformation_strength=100)
    assert a == pytest.approx(b, abs=TOL)


# --------------------------------------------------------------------------- #
# 04 §13.1 — weighted geometric mean drags down on a low component, and        #
# tolerates missing components.                                                #
# --------------------------------------------------------------------------- #
def test_weighted_geometric_mean_matches_formula():
    scores = {"a": 0.9, "b": 0.5}
    weights = {"a": 0.5, "b": 0.5}
    expected = math.exp((0.5 * math.log(0.9) + 0.5 * math.log(0.5)) / 1.0)
    assert weighted_geometric_mean(scores, weights) == pytest.approx(expected, abs=TOL)


def test_geometric_mean_dragged_down_by_low_component():
    # Geometric < arithmetic when components differ (04 §13.1 rationale).
    scores = {"a": 0.99, "b": 0.20}
    weights = {"a": 0.5, "b": 0.5}
    geo = weighted_geometric_mean(scores, weights)
    arith = 0.5 * 0.99 + 0.5 * 0.20
    assert geo < arith


def test_weighted_geometric_mean_missing_component_skipped():
    # 04 §20: a weight key with no matching score is skipped, not treated as 0.
    scores = {"a": 0.8}  # "b" missing
    weights = {"a": 0.5, "b": 0.5}
    # Only "a" contributes -> mean == 0.8.
    assert weighted_geometric_mean(scores, weights) == pytest.approx(0.8, abs=TOL)


def test_weighted_geometric_mean_no_overlap_returns_epsilon():
    assert weighted_geometric_mean({"x": 0.9}, {"y": 1.0}) == EPSILON


# --------------------------------------------------------------------------- #
# 04 §5 — QualityVector clamps every axis on construction.                     #
# --------------------------------------------------------------------------- #
def test_quality_vector_from_visible_clamps_edges():
    v = QualityVector.from_visible(
        source_quality=0,
        capture_quality=100,
        faithfulness=50,
        alignment=87,
        coverage=99.99,
        utility_value=12,
    )
    d = v.as_dict()
    assert d["source_quality"] == EPSILON
    assert d["capture_quality"] == 1.0 - EPSILON
    assert d["faithfulness"] == pytest.approx(0.5, abs=TOL)
    assert v.visible()["alignment"] == 87


# --------------------------------------------------------------------------- #
# 04 §13 — composite profiles.                                                 #
# --------------------------------------------------------------------------- #
def _example_vector() -> QualityVector:
    # 04 §2 worked example.
    return QualityVector.from_visible(
        source_quality=98,
        capture_quality=99,
        faithfulness=78,
        alignment=85,
        coverage=90,
        utility_value=88,
    )


def test_composite_default_matches_doc_example():
    # The §13.1 weighted-geometric-mean formula applied to the §2 example vector
    # yields visible 89 (verified by hand: geo and weighted-arithmetic mean both
    # round to 89). 04 §2 narrates "87" as an illustrative number, but that
    # value does NOT come out of the §13.1 formula the spec defines — a spec
    # inconsistency. The formula is the source of truth, so we assert 89.
    v = _example_vector()
    q = compute_composite_quality(v, "default")
    assert to_visible_score(q) == 89


def test_composite_default_weights_complete():
    # The default weights cover exactly the six canonical axes (04 §13.1).
    assert set(DEFAULT_COMPOSITE_WEIGHTS) == set(_example_vector().as_dict())
    assert sum(DEFAULT_COMPOSITE_WEIGHTS.values()) == pytest.approx(1.0, abs=TOL)


def test_composite_conservative_is_weakest_of_three():
    # 04 §13.2: min(source, capture, faithfulness). Here faithfulness (78) wins.
    v = _example_vector()
    q = compute_composite_quality(v, "conservative")
    assert to_visible_score(q) == 78


def test_composite_utility_profile_runs():
    v = _example_vector()
    q = compute_composite_quality(v, "utility")
    assert 0.0 < q < 1.0


def test_composite_retrieval_modulates_semantic():
    # 04 §13.4: retrieval_score = semantic * (0.5 + 0.5*composite).
    v = _example_vector()
    semantic = 0.6
    q = compute_composite_quality(v, "retrieval", semantic_score=semantic)
    composite = compute_composite_quality(v, "default")
    expected = semantic * (0.5 + 0.5 * composite)
    assert q == pytest.approx(clamp_q(expected), abs=TOL)
    # Quality modifies but never erases semantic relevance: result stays within
    # [0.5*semantic, semantic].
    assert 0.5 * semantic <= q <= semantic


def test_composite_retrieval_requires_semantic_score():
    with pytest.raises(ValueError):
        compute_composite_quality(_example_vector(), "retrieval")


def test_composite_unknown_profile_raises():
    with pytest.raises(ValueError):
        compute_composite_quality(_example_vector(), "nonsense")


# --------------------------------------------------------------------------- #
# Roadmap "conflicting inputs" edge: a vector with one strong and one very      #
# weak axis must produce a composite the weak axis dominates (no laundering).   #
# --------------------------------------------------------------------------- #
def test_conflicting_components_weak_axis_dominates():
    # source pristine, faithfulness terrible — composite must stay low, not be
    # averaged away (04 §3.6 quality-laundering prevention, §13.1 geo-mean).
    conflicted = QualityVector.from_visible(
        source_quality=99,
        capture_quality=99,
        faithfulness=5,
        alignment=99,
        coverage=99,
        utility_value=99,
    )
    default_q = compute_composite_quality(conflicted, "default")
    conservative_q = compute_composite_quality(conflicted, "conservative")
    # Conservative floors at the weakest of the three -> faithfulness (5).
    assert to_visible_score(conservative_q) == 5
    # Default geo-mean is dragged well below the arithmetic mean (~83).
    assert to_visible_score(default_q) < 83


def test_root_reexport():
    # E9a contract: public functions re-exported from the package root.
    import matrx_utils

    assert matrx_utils.derive is derive
    assert matrx_utils.QualityVector is QualityVector
    assert matrx_utils.compute_composite_quality is compute_composite_quality
