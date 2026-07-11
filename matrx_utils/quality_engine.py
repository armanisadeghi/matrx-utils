"""Pure-math quality engine for the Matrx Quality Model (E9a).

Single source of truth for the *math* lives in
``docs/knowledge/04_matrx_quality_model.md`` (referred to below as "04").
This module implements that spec EXACTLY and adds nothing beyond it: it is
dependency-free, side-effect-free, and has no DB / sibling-package imports
(``matrx-utils`` is the root of the package graph). Every function maps to a
numbered section of 04; the citation is in each function's comment.

Out of scope for E9a (pure math only): ``create_quality_event`` / persistence,
``apply_utility_profile`` (the one-number→vector expansion, 04 TASK §5), the
multi-input basis (04 §12), and conflict penalties (04 §12.3) — all marked
"💤 deferred to v2" in 04. Those are E9b/DB work and MUST land beside the
schema, not here.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Mapping

# 04 §4.1 / §6.1 — clamp epsilon. Exact 0 / 1 are labels only, never math values.
EPSILON: float = 1e-4

# 04 §5 — the canonical six-axis quality vector. These names are canonical
# (04 §19 rule 3); never invent or rename an axis.
QUALITY_AXES: tuple[str, ...] = (
    "source_quality",
    "capture_quality",
    "faithfulness",
    "alignment",
    "coverage",
    "utility_value",
)

# 04 §10.1 — named adjustment presets → log-odds impacts. Names/direction are
# stable; the numbers may be globally tuned.
ADJUSTMENT_PRESETS: dict[str, float] = {
    "strong_downgrade": -2.00,
    "moderate_downgrade": -1.00,
    "minor_downgrade": -0.40,
    "no_change": 0.00,
    "minor_upgrade": 0.40,
    "moderate_upgrade": 1.00,
    "strong_upgrade": 2.00,
}

# 04 §13.1 — default composite weights (the weighted-geometric-mean profile).
DEFAULT_COMPOSITE_WEIGHTS: dict[str, float] = {
    "source_quality": 0.20,
    "capture_quality": 0.15,
    "faithfulness": 0.20,
    "alignment": 0.20,
    "coverage": 0.15,
    "utility_value": 0.10,
}

# 04 §13.3 — utility composite weights (practical usefulness over authority).
UTILITY_COMPOSITE_WEIGHTS: dict[str, float] = {
    "source_quality": 0.10,
    "capture_quality": 0.10,
    "faithfulness": 0.15,
    "alignment": 0.25,
    "coverage": 0.20,
    "utility_value": 0.20,
}


# --------------------------------------------------------------------------- #
# 04 §6.1 / §20 — log-odds primitives.                                         #
# --------------------------------------------------------------------------- #
def clamp_q(q: float, eps: float = EPSILON) -> float:
    # 04 §4.1: q = clamp(q, epsilon, 1 - epsilon). Keeps logit/sigmoid finite.
    return max(eps, min(1.0 - eps, q))


def logit(q: float) -> float:
    # 04 §6.1: logit(q) = ln(q / (1 - q)). Clamp first so it never hits ±inf.
    q = clamp_q(q)
    return math.log(q / (1.0 - q))


def sigmoid(z: float) -> float:
    # 04 §6.1: sigmoid(z) = 1 / (1 + e^-z). The §20 pseudocode `math.exp(-z)`
    # OVERFLOWS for large-negative z (e.g. a saturated adjust chain), raising
    # OverflowError instead of saturating — which would violate the "never inf,
    # never crash" contract. Use the numerically-stable branch form (identical
    # value for every finite z) and then clamp into (0, 1) per §20.
    if z >= 0.0:
        return clamp_q(1.0 / (1.0 + math.exp(-z)))
    ez = math.exp(z)
    return clamp_q(ez / (1.0 + ez))


# --------------------------------------------------------------------------- #
# 04 §4.1 — visible-score <-> normalized-q mapping.                            #
# --------------------------------------------------------------------------- #
def from_visible_score(score: float) -> float:
    # 04 §4.1 / §20: q = clamp(visible_score / 100). 0 -> 0.0001, 100 -> 0.9999.
    return clamp_q(score / 100.0)


def to_visible_score(q: float) -> int:
    # 04 §4.1 / §20: visible_score = round(clamp(q) * 100).
    return round(clamp_q(q) * 100)


# --------------------------------------------------------------------------- #
# 04 §§8-11 — the three canonical utility effect types.                        #
# These are the ONLY effect types (04 §8 / §19 rule 4).                        #
# --------------------------------------------------------------------------- #
def preserve(q_in: float) -> float:
    # 04 §9: q_out = q_in. A non-mutating utility (import, chunk, index).
    return clamp_q(q_in)


def adjust(q_in: float, impact: float) -> float:
    # 04 §10: z_out = z_in + impact ; q_out = sigmoid(z_out). `impact` is in
    # log-odds units (04 §10.1 presets, e.g. moderate_upgrade = +1.00).
    return sigmoid(logit(q_in) + impact)


def derive(q_in: float, q_target: float, transformation_strength: float) -> float:
    # 04 §11.1: a derived artifact blends input toward the utility's target in
    # log-odds space.
    #   strength = transformation_strength / 100   (0..1)
    #   z_out = (1 - strength) * z_in + strength * z_target
    #   q_out = sigmoid(z_out)
    # 04 §11: low input + good utility -> lifts; high input + lossy utility ->
    # drops. Both are intended.
    strength = transformation_strength / 100.0
    strength = max(0.0, min(1.0, strength))
    z_in = logit(q_in)
    z_target = logit(q_target)
    z_out = ((1.0 - strength) * z_in) + (strength * z_target)
    return sigmoid(z_out)


# --------------------------------------------------------------------------- #
# 04 §13.1 — weighted geometric mean (low components drag the composite down). #
# --------------------------------------------------------------------------- #
def weighted_geometric_mean(
    values: Mapping[str, float],
    weights: Mapping[str, float],
) -> float:
    # 04 §13.1 / §20:
    #   composite = exp( sum(w_i * ln(q_i)) / sum(w_i) )
    # Geometric (not arithmetic) so a single weak axis materially pulls the
    # composite down. Keys present in `weights` but missing from `values` are
    # skipped (04 §20 `continue`), which is how a partial vector is handled.
    numerator = 0.0
    denominator = 0.0
    for key, weight in weights.items():
        if key not in values:
            continue
        q = clamp_q(values[key])
        numerator += weight * math.log(q)
        denominator += weight
    if denominator == 0:
        # 04 §20: no overlapping keys -> nothing to average; floor at epsilon.
        return EPSILON
    return clamp_q(math.exp(numerator / denominator))


# --------------------------------------------------------------------------- #
# 04 §5 — the Quality Vector. Frozen: a pure value object, no side effects.    #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class QualityVector:
    """The six canonical quality axes (04 §5), each a normalized q in (0, 1).

    Construct from visible 0-100 scores with ``from_visible(...)``; read them
    back with ``visible()``. ``as_dict()`` feeds the composite functions.
    """

    source_quality: float
    capture_quality: float
    faithfulness: float
    alignment: float
    coverage: float
    utility_value: float

    def __post_init__(self) -> None:
        # 04 §4.1 / §7 (TASK §7 "no nulls for active scoring"): clamp every axis
        # into the open interval so downstream logit math never blows up. Uses
        # object.__setattr__ because the dataclass is frozen.
        for axis in QUALITY_AXES:
            object.__setattr__(self, axis, clamp_q(getattr(self, axis)))

    @classmethod
    def from_visible(
        cls,
        *,
        source_quality: float,
        capture_quality: float,
        faithfulness: float,
        alignment: float,
        coverage: float,
        utility_value: float,
    ) -> QualityVector:
        # 04 §4.1: build the internal vector from user-facing 0-100 scores.
        return cls(
            source_quality=from_visible_score(source_quality),
            capture_quality=from_visible_score(capture_quality),
            faithfulness=from_visible_score(faithfulness),
            alignment=from_visible_score(alignment),
            coverage=from_visible_score(coverage),
            utility_value=from_visible_score(utility_value),
        )

    def as_dict(self) -> dict[str, float]:
        return {axis: getattr(self, axis) for axis in QUALITY_AXES}

    def visible(self) -> dict[str, int]:
        # 04 §4 / §14 — the 0-100 scores a user/UI sees.
        return {axis: to_visible_score(getattr(self, axis)) for axis in QUALITY_AXES}


# --------------------------------------------------------------------------- #
# 04 §13 — composite quality with named, purpose-aware profiles.              #
# --------------------------------------------------------------------------- #
def compute_composite_quality(
    vector: QualityVector,
    profile: str = "default",
    *,
    semantic_score: float | None = None,
) -> float:
    # 04 §13: a single universal formula is wrong for some tasks, so the
    # composite is keyed by a named profile. Returns normalized q in (0, 1);
    # call to_visible_score() for display (04 §13.1).
    scores = vector.as_dict()

    if profile == "default":
        # 04 §13.1 — weighted geometric mean over all six axes.
        return weighted_geometric_mean(scores, DEFAULT_COMPOSITE_WEIGHTS)

    if profile == "conservative":
        # 04 §13.2 — the weakest of source/capture/faithfulness sets the floor.
        return clamp_q(
            min(
                scores["source_quality"],
                scores["capture_quality"],
                scores["faithfulness"],
            )
        )

    if profile == "utility":
        # 04 §13.3 — alignment/coverage/utility-weighted geometric mean.
        return weighted_geometric_mean(scores, UTILITY_COMPOSITE_WEIGHTS)

    if profile == "retrieval":
        # 04 §13.4: retrieval_score = semantic_score * quality_modifier, where
        #   quality_modifier = 0.5 + 0.5 * composite_quality
        # and composite_quality is the default-profile composite (04 §13.4 uses
        # the artifact's composite). Quality can boost/reduce but never erases
        # semantic relevance. semantic_score is required for this profile.
        if semantic_score is None:
            raise ValueError(
                "compute_composite_quality(profile='retrieval') requires "
                "semantic_score (04 §13.4)."
            )
        composite = weighted_geometric_mean(scores, DEFAULT_COMPOSITE_WEIGHTS)
        quality_modifier = 0.5 + (0.5 * composite)
        return clamp_q(semantic_score * quality_modifier)

    raise ValueError(
        f"Unknown composite profile {profile!r}; expected one of "
        "'default', 'conservative', 'utility', 'retrieval' (04 §13)."
    )


__all__ = [
    "EPSILON",
    "QUALITY_AXES",
    "ADJUSTMENT_PRESETS",
    "DEFAULT_COMPOSITE_WEIGHTS",
    "UTILITY_COMPOSITE_WEIGHTS",
    "clamp_q",
    "logit",
    "sigmoid",
    "from_visible_score",
    "to_visible_score",
    "preserve",
    "adjust",
    "derive",
    "weighted_geometric_mean",
    "QualityVector",
    "compute_composite_quality",
]
