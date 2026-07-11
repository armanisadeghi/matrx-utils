"""detached_task — verify the ContextVar inheritance break.

The primitive's entire value is that a fire-and-forget task does NOT
inherit ContextVars from the parent. These tests prove it.
"""

from __future__ import annotations

import asyncio
import contextvars

import pytest

from matrx_utils import detached_task


_test_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "_detached_task_test_var", default="default"
)


@pytest.mark.asyncio
async def test_detached_task_does_not_inherit_contextvar():
    """The parent sets a ContextVar; the detached task must NOT see it."""
    _test_var.set("parent_value")
    seen_in_child: list[str] = []

    async def _child():
        seen_in_child.append(_test_var.get())

    task = detached_task(_child())
    await task

    assert seen_in_child == ["default"]


@pytest.mark.asyncio
async def test_create_task_DOES_inherit_contextvar_for_comparison():
    """Baseline: prove asyncio.create_task DOES inherit, so the
    detached_task behavior is meaningfully different (not a no-op)."""
    _test_var.set("parent_value")
    seen_in_child: list[str] = []

    async def _child():
        seen_in_child.append(_test_var.get())

    task = asyncio.create_task(_child())
    await task

    assert seen_in_child == ["parent_value"]


@pytest.mark.asyncio
async def test_detached_task_returns_a_task():
    """Return value must be an asyncio.Task that can be awaited."""

    async def _child():
        return 42

    task = detached_task(_child())
    assert isinstance(task, asyncio.Task)
    result = await task
    assert result == 42


@pytest.mark.asyncio
async def test_detached_task_with_name():
    """Optional name argument is set on the Task."""

    async def _child():
        return None

    task = detached_task(_child(), name="my-detached-thing")
    assert task.get_name() == "my-detached-thing"
    await task


@pytest.mark.asyncio
async def test_detached_task_child_can_set_its_own_contextvars():
    """The detached task starts with a fresh Context but can still
    set its own ContextVars internally — they just don't bleed up."""
    parent_seen_after: list[str] = []
    _test_var.set("parent_initial")

    async def _child():
        _test_var.set("child_override")

    task = detached_task(_child())
    await task
    parent_seen_after.append(_test_var.get())

    # The child's set() ran in the fresh Context, so the parent value
    # is unchanged.
    assert parent_seen_after == ["parent_initial"]


@pytest.mark.asyncio
async def test_detached_task_simulates_transaction_connection_break():
    """The intended use case: a parent has 'opened a transaction'
    (set an _active_connection ContextVar). A detached task started
    inside must NOT see the connection."""
    _fake_active_connection: contextvars.ContextVar[object | None] = contextvars.ContextVar(
        "_fake_active_connection", default=None,
    )
    sentinel_conn = object()
    _fake_active_connection.set(sentinel_conn)

    saw_connection: list[object | None] = []

    async def _detached_writer():
        # Simulates a write task. Would have inherited the connection
        # via asyncio.create_task — but detached_task gives us a fresh
        # Context.
        saw_connection.append(_fake_active_connection.get())

    await detached_task(_detached_writer())

    assert saw_connection == [None], (
        "Detached task inherited the transaction connection — this "
        "would cause asyncpg.InterfaceError in production."
    )
