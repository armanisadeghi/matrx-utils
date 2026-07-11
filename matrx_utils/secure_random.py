"""Cryptographically-secure random selection helpers.

Built on ``os.urandom`` via :class:`random.SystemRandom` — non-seedable and
non-reproducible by design, for the case where the *unpredictability* of a choice
is the point (e.g. an entropy-injection "wheel" that must not converge to the same
pick across calls). For ordinary, reproducible randomness use the stdlib
``random`` module instead.

This is the single shared primitive: never scatter ``secrets.choice`` /
``random.SystemRandom()`` constructions across the codebase — import from here.
"""
from __future__ import annotations

from random import SystemRandom
from typing import Sequence, TypeVar

T = TypeVar("T")

_sysrand = SystemRandom()


def secure_choice(seq: Sequence[T]) -> T:
    if not seq:
        raise IndexError("secure_choice() arg is an empty sequence")
    return _sysrand.choice(seq)


def secure_sample(population: Sequence[T], k: int) -> list[T]:
    """Return ``k`` distinct items chosen uniformly at random, in random order.

    ``k`` is clamped to ``len(population)`` so callers never have to guard the
    bound themselves.
    """
    if k < 0:
        raise ValueError("k must be non-negative")
    n = len(population)
    if k > n:
        k = n
    return _sysrand.sample(list(population), k)


def secure_shuffle(seq: Sequence[T]) -> list[T]:
    out = list(seq)
    _sysrand.shuffle(out)
    return out


def secure_randint(low: int, high: int) -> int:
    """Inclusive on both ends, like :meth:`random.Random.randint`."""
    if low > high:
        raise ValueError("low must be <= high")
    return _sysrand.randint(low, high)
