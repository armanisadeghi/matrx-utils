"""Canonical retry / backoff — the one place the Matrx family computes "wait how long".

The repo had ~23 hand-rolled retry loops and a backoff calculator buried in
``matrx_graph.executor._retry``; this is their shared home. ``compute_backoff_ms``
is the pure delay math (promoted from matrx-graph, semantics preserved exactly so
graph can delegate to it without changing behaviour). ``retry_async`` is a general
async retry wrapper for ANY coroutine — DB calls, provider calls, queue polling —
not just HTTP. (``http_client`` keeps its own thin HTTP policy for 429/5xx +
``Retry-After`` semantics, but its delay math delegates here.)

    from matrx_utils import retry_async, compute_backoff_ms

    rows = await retry_async(lambda: db.fetch(...), retry_on=(ConnectionError,))
    delay_ms = compute_backoff_ms(attempt, initial_ms=500, max_ms=10_000)
"""
from __future__ import annotations

import random
from asyncio import sleep as _sleep
from typing import Awaitable, Callable, Sequence, TypeVar

T = TypeVar("T")

# The strategy names ``compute_backoff_ms`` understands (match matrx-graph's
# BackoffStrategy enum values, so graph passes ``policy.backoff.value`` straight in).
NONE = "none"
FIXED = "fixed"
LINEAR = "linear"
EXPONENTIAL = "exponential"
EXPONENTIAL_JITTER = "exponential_jitter"


def compute_backoff_ms(
    attempt: int,
    *,
    initial_ms: int,
    max_ms: int,
    strategy: str = EXPONENTIAL_JITTER,
) -> int:
    """Delay before the next attempt, in milliseconds.

    ``attempt`` is the attempt that just failed (1-indexed): the first retry uses
    ``attempt=1``, the second ``attempt=2``. ``exponential_jitter`` (the default)
    jitters uniformly in ``[0.5x, 1.5x]`` of the exponential base. Every result is
    capped at ``max_ms``. ``initial_ms <= 0`` or ``strategy="none"`` returns 0.
    Semantics are byte-faithful to the original ``matrx_graph`` implementation.
    """
    if initial_ms <= 0 or strategy == NONE:
        return 0
    if strategy == FIXED:
        value = initial_ms
    elif strategy == LINEAR:
        value = initial_ms * attempt
    elif strategy == EXPONENTIAL:
        value = initial_ms * (2 ** (attempt - 1))
    elif strategy == EXPONENTIAL_JITTER:
        raw = initial_ms * (2 ** (attempt - 1))
        value = int(raw * random.uniform(0.5, 1.5))
    else:
        raise ValueError(f"unknown backoff strategy {strategy!r}")
    return min(value, max_ms)


async def retry_async(
    fn: Callable[[], Awaitable[T]],
    *,
    max_attempts: int = 3,
    initial_ms: int = 500,
    max_ms: int = 10_000,
    strategy: str = EXPONENTIAL_JITTER,
    retry_on: Sequence[type[BaseException]] = (Exception,),
    on_retry: Callable[[int, BaseException, int], None] | None = None,
) -> T:
    """Await ``fn()``, retrying on ``retry_on`` exceptions with backoff.

    Returns ``fn()``'s result, or re-raises the last exception once
    ``max_attempts`` is reached. ``retry_on`` defaults to every ``Exception`` —
    **narrow it** to the genuinely transient types (e.g. ``ConnectionError``,
    ``TimeoutError``) so real bugs surface instead of being retried. ``on_retry``,
    if given, is called ``(attempt, exc, delay_ms)`` before each sleep — wire it
    to your logger/emitter; this primitive deliberately stays silent on its own.
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be >= 1")
    retry_on = tuple(retry_on)
    attempt = 0
    while True:
        attempt += 1
        try:
            return await fn()
        except retry_on as exc:
            if attempt >= max_attempts:
                raise
            delay_ms = compute_backoff_ms(attempt, initial_ms=initial_ms, max_ms=max_ms, strategy=strategy)
            if on_retry is not None:
                on_retry(attempt, exc, delay_ms)
            await _sleep(delay_ms / 1000)
