"""Detached task — spawn an ``asyncio.Task`` in a fresh ContextVar scope.

The default ``asyncio.create_task(coro)`` copies the current task's
``contextvars.Context`` snapshot into the child task. That snapshot
includes every ContextVar set in the parent — most relevantly for
matrx-orm, the ``_active_connection`` ContextVar that points at the
parent's open transaction connection.

When the child task subsequently runs a DB query, matrx-orm sees the
inherited ``_active_connection`` and dispatches the query onto the
**parent's transaction connection** — exactly while the parent is
running its own statement. asyncpg refuses concurrent operations on a
single connection and raises::

    asyncpg.exceptions.InterfaceError: cannot perform operation:
    another operation is in progress

The fix is to spawn the child task in a **fresh** Context that does
not inherit the parent's transaction state. That child task acquires
its own pool connection, runs its own statement, no collision. This
is the entire purpose of :func:`detached_task`.

Use this anywhere you would use ``asyncio.create_task(coro)`` for a
fire-and-forget DB write **inside** a request handler or other code
that may be running within an open ``transaction()`` /
:class:`matrx_orm.Session`. Examples:

* Tool-call DB logging (``cx_tool_trace`` writes)
* Observational-memory buffer flushes
* Deferred labelers / analytics emitters
* Anything that says "this should not block the main flow"

This module belongs to matrx-utils so any package can import it
without crossing the dependency graph upward.
"""

from __future__ import annotations

import asyncio
import contextvars
import logging
from collections.abc import Coroutine
from typing import Any

logger = logging.getLogger("matrx_utils.detached_task")


def detached_task(
    coro: Coroutine[Any, Any, Any],
    *,
    name: str | None = None,
) -> asyncio.Task[Any]:
    """Spawn ``coro`` as an :class:`asyncio.Task` in a fresh Context.

    Unlike :func:`asyncio.create_task`, the spawned task does **not**
    inherit the caller's ``contextvars.Context``. This deliberately
    breaks any ContextVar-mediated state inheritance — including
    matrx-orm's ``_active_connection``, the matrx-ai
    ``_execution_state``, and any custom ContextVars the caller has
    set.

    The intent is single: prevent a fire-and-forget task from running
    a DB query on the parent's open transaction connection (asyncpg
    "cannot perform operation: another operation is in progress").
    The detached task starts with no transaction context and acquires
    its own pool connection if it needs one.

    Args:
        coro: the coroutine to run.
        name: optional name for the task (forwarded to ``Task.set_name``
            so it shows up in tracebacks / introspection).

    Returns:
        The :class:`asyncio.Task` wrapping ``coro``. Caller may discard
        it; the task is not garbage-collected mid-flight because the
        event loop holds a strong reference.

    Caveats:
        * The detached task gets a **fresh** Context, not the absence
          of one. If you genuinely want some piece of context to flow
          through (e.g. a trace ID), set it explicitly inside the
          coroutine.
        * If the running loop is shutting down (no running loop), this
          raises ``RuntimeError`` like ``asyncio.create_task``. Caller
          should guard if that case is reachable.
    """
    # Fresh, empty Context. Critically, this is NOT a snapshot of the
    # caller — it is a brand-new Context with no inherited ContextVars.
    # The runtime gives the new task this Context as its execution scope.
    fresh_ctx = contextvars.Context()

    # asyncio.create_task accepts a ``context`` kwarg as of 3.11 that
    # specifies the Context the task runs in. (Earlier asyncio versions
    # always used copy_context; the explicit kwarg is what makes this
    # primitive viable.)
    task = asyncio.create_task(coro, context=fresh_ctx)
    if name is not None:
        task.set_name(name)
    return task
