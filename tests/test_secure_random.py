"""Tests for the CSPRNG selection primitive."""
from collections import Counter

import pytest

from matrx_utils.secure_random import (
    secure_choice,
    secure_randint,
    secure_sample,
    secure_shuffle,
)


def test_choice_empty_raises():
    with pytest.raises(IndexError):
        secure_choice([])


def test_choice_in_population():
    pop = list(range(10))
    for _ in range(200):
        assert secure_choice(pop) in pop


def test_sample_distinct_and_clamped():
    pop = list(range(5))
    s = secure_sample(pop, 3)
    assert len(s) == 3 and len(set(s)) == 3 and all(x in pop for x in s)
    # k > n clamps to n rather than raising.
    s = secure_sample(pop, 99)
    assert len(s) == 5 and set(s) == set(pop)


def test_sample_negative_raises():
    with pytest.raises(ValueError):
        secure_sample([1, 2], -1)


def test_randint_bounds_and_validation():
    for _ in range(300):
        assert 2 <= secure_randint(2, 4) <= 4
    assert secure_randint(5, 5) == 5
    with pytest.raises(ValueError):
        secure_randint(4, 2)


def test_shuffle_is_permutation_without_mutating_source():
    src = list(range(20))
    out = secure_shuffle(src)
    assert sorted(out) == list(range(20))
    assert src == list(range(20))  # original untouched


def test_distribution_covers_full_range():
    c = Counter(secure_randint(0, 9) for _ in range(3000))
    assert len(c) == 10  # every value appears — sanity that it's not constant
