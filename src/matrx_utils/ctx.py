"""matrx_utils.ctx — lightweight, optional request-context protocol.

Any app that wants matrx-utils features (cloud_sync, etc.) to automatically
resolve the current user registers a *context getter* once at startup.  From
that point on, every call that would otherwise need an explicit ``user_id``
argument resolves it transparently from the running request context.

Three patterns
--------------

**Pattern A — aidream / matrx-connect** (register once, everything is automatic):

    # In your app startup, after configure_settings(...)
    from matrx_utils.conf import configure_context
    from matrx_connect.context.app_context import try_get_app_context
    configure_context(try_get_app_context)

    # Now, inside any request handler:
    result = await fm.managed_write_async("reports/q1.json", data)
    # user_id is read from AppContext automatically — no argument needed.

**Pattern B — any other FastAPI / Django / WSGI app**:

    from matrx_utils.conf import configure_context
    configure_context(lambda: getattr(request_local, "ctx", None))

    # The lambda is called on every resolution attempt; it must return an
    # object with a .user_id attribute, or None.

**Pattern C — background scripts, CLI tools, tests** (no middleware):

    from matrx_utils.ctx import set_manual_context, clear_manual_context
    from matrx_utils.ctx import SimpleUserContext

    token = set_manual_context(SimpleUserContext(user_id="test-user-uuid"))
    try:
        fm.managed_write("output.json", data)   # user_id resolved automatically
    finally:
        clear_manual_context(token)

Resolution order
----------------
1. Manual context pushed via ``set_manual_context()`` (highest priority —
   useful for tests and background jobs that run outside middleware).
2. Registered getter (``configure_context(fn)``) — used in web frameworks.
3. Fall back to ``""`` / ``None`` — cloud_sync will use the ``user_id`` baked
   into ``CloudSyncConfig``, or raise if none is available.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Callable, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# UserContext protocol — what matrx-utils expects from a context object
# ---------------------------------------------------------------------------

@runtime_checkable
class UserContext(Protocol):
    """Structural protocol for a request-scoped user context.

    Any object that has these attributes satisfies the protocol — you do *not*
    need to inherit from this class.  ``AppContext`` from ``matrx_connect``
    already satisfies it without modification.
    """

    user_id: str
    is_authenticated: bool
    organization_id: str | None


# ---------------------------------------------------------------------------
# SimpleUserContext — a plain dataclass for scripts / tests / background tasks
# ---------------------------------------------------------------------------

@dataclass
class SimpleUserContext:
    """Minimal UserContext for use outside of a web framework.

    Suitable for CLI scripts, background workers, Celery tasks, and tests.

    Examples
    --------
        ctx = SimpleUserContext(user_id="some-uuid")
        ctx = SimpleUserContext(user_id="admin", is_authenticated=True, is_admin=True)
        ctx = SimpleUserContext(
            user_id="org-admin",
            organization_id="org-uuid",
            metadata={"role": "owner"},
        )
    """

    user_id: str = ""
    is_authenticated: bool = False
    is_admin: bool = False
    organization_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Module-level context getter slot — set by configure_context()
# ---------------------------------------------------------------------------

_context_getter: Callable[[], Any | None] | None = None


# ---------------------------------------------------------------------------
# Manual context ContextVar — for background tasks / tests
# ---------------------------------------------------------------------------

_manual_context: ContextVar[SimpleUserContext | None] = ContextVar(
    "matrx_manual_context", default=None
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_active_context() -> Any | None:
    """Return the active user context, or None if none is set.

    Resolution order:
    1. Manual context (``set_manual_context``).
    2. Registered getter (``configure_context``).
    3. ``None``.
    """
    manual = _manual_context.get(None)
    if manual is not None:
        return manual

    if _context_getter is not None:
        try:
            return _context_getter()
        except Exception:
            return None

    return None


def get_active_user_id() -> str:
    """Return the user_id from the active context, or ``""`` if none is set."""
    ctx = get_active_context()
    if ctx is None:
        return ""
    return getattr(ctx, "user_id", "") or ""


def get_active_organization_id() -> str | None:
    """Return the organization_id from the active context, or ``None``."""
    ctx = get_active_context()
    if ctx is None:
        return None
    return getattr(ctx, "organization_id", None)


def is_authenticated() -> bool:
    """Return True if the active context belongs to an authenticated user."""
    ctx = get_active_context()
    if ctx is None:
        return False
    return bool(getattr(ctx, "is_authenticated", False))


def set_manual_context(ctx: SimpleUserContext) -> Token:
    """Push a manual context for the current async task / thread.

    Returns a ``Token`` that must be passed to ``clear_manual_context()``
    to restore the previous state.

    This is the recommended approach for background workers, Celery tasks,
    CLI scripts, and unit tests that run outside of HTTP middleware.

    Example
    -------
        token = set_manual_context(SimpleUserContext(user_id="abc"))
        try:
            ...
        finally:
            clear_manual_context(token)
    """
    return _manual_context.set(ctx)


def clear_manual_context(token: Token) -> None:
    """Restore the context to its state before the matching ``set_manual_context()`` call."""
    _manual_context.reset(token)


def context_for_user(user_id: str, **kwargs: Any):
    """Context manager / token helper for one-liner test setup.

    Example
    -------
        with context_for_user("user-uuid"):
            result = fm.managed_write("file.json", data)
    """
    return _ContextBlock(SimpleUserContext(user_id=user_id, **kwargs))


class _ContextBlock:
    """Internal context manager returned by ``context_for_user``."""

    def __init__(self, ctx: SimpleUserContext) -> None:
        self._ctx = ctx
        self._token: Token | None = None

    def __enter__(self) -> SimpleUserContext:
        self._token = set_manual_context(self._ctx)
        return self._ctx

    def __exit__(self, *_: Any) -> None:
        if self._token is not None:
            clear_manual_context(self._token)
