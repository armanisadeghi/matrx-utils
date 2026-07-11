"""Vocabulary-hint primitives — turn a wrong name into the information that
makes the NEXT attempt succeed.

The pattern (established by matrx-ai's ``db_hints``): a structured fact ("name X
is not in vocabulary V") becomes a difflib did-you-mean plus a bounded option
list, never an unbounded dump. Stdlib only — every tier may import this.
"""
from __future__ import annotations

import difflib
from collections.abc import Iterable, Sequence

__all__ = ["did_you_mean", "format_options", "suggestion_line"]


def did_you_mean(
    wrong: str,
    options: Iterable[str],
    n: int = 5,
    cutoff: float = 0.6,
) -> list[str]:
    """Closest matches for ``wrong`` among ``options``, best first (difflib)."""
    if not wrong:
        return []
    return difflib.get_close_matches(wrong, list(options), n=n, cutoff=cutoff)


def format_options(names: Sequence[str], cap: int) -> str:
    """Bounded comma list: ``a, b, c … (+N more)`` — never an unbounded dump."""
    if len(names) <= cap:
        return ", ".join(names)
    return ", ".join(names[:cap]) + f" … (+{len(names) - cap} more)"


def suggestion_line(
    wrong: str,
    options: Iterable[str],
    *,
    noun: str = "name",
) -> str | None:
    """One human/agent-readable did-you-mean sentence, or ``None`` when nothing
    is close enough. Single confident match → ``Did you mean 'x'?``; several →
    a bounded ``one of`` list."""
    matches = did_you_mean(wrong, options)
    if not matches:
        return None
    if len(matches) == 1:
        return f"Did you mean {noun} '{matches[0]}'?"
    return f"Did you mean one of these {noun}s: {format_options(matches, 5)}?"
