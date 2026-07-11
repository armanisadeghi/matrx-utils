"""The injected DB policy is THE access decision — not the Python fallback.

The file layer used to resolve access in Python (owner -> public -> direct grant
-> parent folder). That mirror is a strict SUBSET of the real policy
(`iam.has_access_for`): it cannot see orgs, org-admins, memberships or
`platform.reachability` containers, so it silently DENIED legitimately-shared
files. The host now injects the authoritative resolver.

These tests pin the contract:
  * when a checker is injected it decides — the Python path is not consulted;
  * a deny raises PermissionError (fail-closed);
  * the Python fallback still works when nothing is injected (standalone
    matrx-utils), so the package keeps running with no host.
"""

from __future__ import annotations

import pytest

from matrx_utils.file_handling.cloud_sync.permissions import (
    PermissionsManager,
    configure_access_checker,
)


class _ExplodingDB:
    """Any Python-side resolution is a bug once a checker is injected."""

    def get_file(self, *a, **k):  # pragma: no cover - must never run
        raise AssertionError("Python fallback consulted despite an injected checker")

    async def get_file_async(self, *a, **k):  # pragma: no cover
        raise AssertionError("Python fallback consulted despite an injected checker")

    def get_user_permission(self, *a, **k):  # pragma: no cover
        raise AssertionError("Python fallback consulted despite an injected checker")

    async def get_user_permission_async(self, *a, **k):  # pragma: no cover
        raise AssertionError("Python fallback consulted despite an injected checker")


@pytest.fixture(autouse=True)
def _reset_checker():
    yield
    configure_access_checker(None, sync_checker=None)


def _pm() -> PermissionsManager:
    return PermissionsManager(_ExplodingDB(), user_id="u1")


async def test_injected_checker_decides_allow() -> None:
    seen: list[tuple] = []

    async def allow_all(user_id, rtype, rid, level):
        seen.append((user_id, rtype, rid, level))
        return True

    configure_access_checker(allow_all)
    pm = _pm()

    assert await pm.require_async("file", "f1", "read", "u1") == "read"
    # The policy question is forwarded verbatim — no Python pre-filtering.
    assert seen == [("u1", "file", "f1", "read")]


async def test_injected_checker_decides_deny_fail_closed() -> None:
    async def deny_all(user_id, rtype, rid, level):
        return False

    configure_access_checker(deny_all)
    pm = _pm()

    with pytest.raises(PermissionError):
        await pm.require_async("file", "f1", "read", "u1")


async def test_injected_checker_sees_every_level() -> None:
    asked: list[str] = []

    async def checker(user_id, rtype, rid, level):
        asked.append(level)
        return level != "admin"  # editor yes, admin no

    configure_access_checker(checker)
    pm = _pm()

    assert await pm.require_async("file", "f1", "write", "u1") == "write"
    with pytest.raises(PermissionError):
        await pm.require_async("file", "f1", "admin", "u1")
    assert asked == ["write", "admin"]


async def test_no_user_is_denied_even_with_permissive_checker() -> None:
    async def allow_all(user_id, rtype, rid, level):  # pragma: no cover
        raise AssertionError("must not consult the policy without an actor")

    configure_access_checker(allow_all)
    pm = PermissionsManager(_ExplodingDB(), user_id="")

    with pytest.raises(PermissionError):
        await pm.require_async("file", "f1", "read", None)


def test_sync_checker_decides() -> None:
    configure_access_checker(None, sync_checker=lambda u, t, i, lvl: lvl == "read")
    pm = _pm()

    assert pm.require("file", "f1", "read", "u1") == "read"
    with pytest.raises(PermissionError):
        pm.require("file", "f1", "admin", "u1")


async def test_python_fallback_still_works_standalone() -> None:
    """No host injected → the package still resolves (subset) rather than crash."""

    class _DB:
        async def get_file_async(self, fid):
            return {"id": fid, "owner_id": "owner-1", "visibility": "private"}

        async def get_user_permission_async(self, rid, rtype, uid):
            return {"permission_level": "read"} if uid == "grantee" else None

    configure_access_checker(None, sync_checker=None)
    pm = PermissionsManager(_DB(), user_id="")

    assert await pm.require_async("file", "f1", "read", "owner-1") == "admin"  # owner
    assert await pm.require_async("file", "f1", "read", "grantee") == "read"  # granted
    with pytest.raises(PermissionError):
        await pm.require_async("file", "f1", "read", "stranger")
