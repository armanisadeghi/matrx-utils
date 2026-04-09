"""Permissions manager for the cloud sync layer.

Provides full ACL support: owner-based, direct user grants, group-based
grants, folder-inherited permissions, and shareable links with optional
expiry and use limits.

Permission levels (ordered by power):
    read  — view / download the file
    write — read + modify / overwrite the file
    admin — write + manage permissions, delete the file

Usage::

    pm = PermissionsManager(db, user_id="current-user-uuid")

    # Grant read access to another user
    pm.grant("file", file_id, grantee_id="other-user", level="read")

    # Check access
    level = pm.check("file", file_id)  # returns "admin" | "write" | "read" | None

    # Create a share link
    link = pm.create_share_link("file", file_id, permission_level="read", max_uses=10)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Literal

from .db import DatabaseClient

logger = logging.getLogger(__name__)

PermissionLevel = Literal["read", "write", "admin"]
ResourceType = Literal["file", "folder"]

_LEVEL_RANK = {"admin": 3, "write": 2, "read": 1}


def _higher(a: str | None, b: str | None) -> str | None:
    """Return the higher of two permission levels."""
    if a is None:
        return b
    if b is None:
        return a
    return a if _LEVEL_RANK.get(a, 0) >= _LEVEL_RANK.get(b, 0) else b


def _is_expired(row: dict) -> bool:
    """Return True if the permission/link has expired."""
    exp = row.get("expires_at")
    if not exp:
        return False
    if isinstance(exp, str):
        exp = datetime.fromisoformat(exp.replace("Z", "+00:00"))
    return exp <= datetime.now(timezone.utc)


class PermissionsManager:
    """Resolves and manages access control for cloud files and folders."""

    def __init__(self, db: DatabaseClient, user_id: str = "") -> None:
        self._db = db
        self._user_id = user_id

    @property
    def user_id(self) -> str:
        return self._user_id

    @user_id.setter
    def user_id(self, value: str) -> None:
        self._user_id = value

    # ------------------------------------------------------------------
    # Permission checking
    # ------------------------------------------------------------------

    def check(
        self,
        resource_type: ResourceType,
        resource_id: str,
        user_id: str | None = None,
    ) -> str | None:
        """Return the effective permission level for *user_id* on a resource.

        Returns ``"admin"``, ``"write"``, ``"read"``, or ``None`` (no access).
        """
        uid = user_id or self._user_id
        if not uid:
            return None

        # 1. Ownership check
        if resource_type == "file":
            record = self._db.get_file(resource_id)
        else:
            record = self._db.get_folder(resource_id)

        if not record:
            return None
        if record.get("owner_id") == uid:
            return "admin"
        if record.get("visibility") == "public":
            level: str | None = "read"
        else:
            level = None

        # 2. Direct user permission
        perm = self._db.get_user_permission(resource_id, resource_type, uid)
        if perm and not _is_expired(perm):
            level = _higher(level, perm["permission_level"])

        # 3. Group permissions
        group_ids = self._db.get_user_group_ids(uid)
        if group_ids:
            all_perms = self._db.list_permissions(resource_id, resource_type)
            for p in all_perms:
                if (
                    p["grantee_type"] == "group"
                    and p["grantee_id"] in group_ids
                    and not _is_expired(p)
                ):
                    level = _higher(level, p["permission_level"])

        # 4. Folder-inherited permission (for files only)
        if resource_type == "file" and record.get("parent_folder_id"):
            folder_level = self.check("folder", record["parent_folder_id"], uid)
            level = _higher(level, folder_level)

        return level

    async def check_async(
        self,
        resource_type: ResourceType,
        resource_id: str,
        user_id: str | None = None,
    ) -> str | None:
        """Async version of check()."""
        uid = user_id or self._user_id
        if not uid:
            return None

        if resource_type == "file":
            record = await self._db.get_file_async(resource_id)
        else:
            record = await self._db.get_folder_async(resource_id)

        if not record:
            return None
        if record.get("owner_id") == uid:
            return "admin"
        if record.get("visibility") == "public":
            level: str | None = "read"
        else:
            level = None

        perm = await self._db.get_user_permission_async(resource_id, resource_type, uid)
        if perm and not _is_expired(perm):
            level = _higher(level, perm["permission_level"])

        group_ids = await self._db.get_user_group_ids_async(uid)
        if group_ids:
            all_perms = await self._db.list_permissions_async(resource_id, resource_type)
            for p in all_perms:
                if (
                    p["grantee_type"] == "group"
                    and p["grantee_id"] in group_ids
                    and not _is_expired(p)
                ):
                    level = _higher(level, p["permission_level"])

        if resource_type == "file" and record.get("parent_folder_id"):
            folder_level = await self.check_async(
                "folder", record["parent_folder_id"], uid
            )
            level = _higher(level, folder_level)

        return level

    def require(
        self,
        resource_type: ResourceType,
        resource_id: str,
        minimum: PermissionLevel = "read",
        user_id: str | None = None,
    ) -> str:
        """Like check(), but raises PermissionError if access is insufficient."""
        level = self.check(resource_type, resource_id, user_id)
        if level is None or _LEVEL_RANK.get(level, 0) < _LEVEL_RANK[minimum]:
            raise PermissionError(
                f"User '{user_id or self._user_id}' requires '{minimum}' access "
                f"on {resource_type} '{resource_id}' but has '{level or 'none'}'."
            )
        return level

    async def require_async(
        self,
        resource_type: ResourceType,
        resource_id: str,
        minimum: PermissionLevel = "read",
        user_id: str | None = None,
    ) -> str:
        level = await self.check_async(resource_type, resource_id, user_id)
        if level is None or _LEVEL_RANK.get(level, 0) < _LEVEL_RANK[minimum]:
            raise PermissionError(
                f"User '{user_id or self._user_id}' requires '{minimum}' access "
                f"on {resource_type} '{resource_id}' but has '{level or 'none'}'."
            )
        return level

    # ------------------------------------------------------------------
    # Grant / revoke
    # ------------------------------------------------------------------

    def grant(
        self,
        resource_type: ResourceType,
        resource_id: str,
        grantee_id: str,
        level: PermissionLevel = "read",
        grantee_type: Literal["user", "group"] = "user",
        expires_at: str | None = None,
    ) -> dict:
        """Grant a permission.  Requires admin access on the resource."""
        self.require(resource_type, resource_id, "admin")
        return self._db.upsert_permission({
            "resource_id": resource_id,
            "resource_type": resource_type,
            "grantee_id": grantee_id,
            "grantee_type": grantee_type,
            "permission_level": level,
            "granted_by": self._user_id,
            "expires_at": expires_at,
        })

    async def grant_async(
        self,
        resource_type: ResourceType,
        resource_id: str,
        grantee_id: str,
        level: PermissionLevel = "read",
        grantee_type: Literal["user", "group"] = "user",
        expires_at: str | None = None,
    ) -> dict:
        await self.require_async(resource_type, resource_id, "admin")
        return await self._db.upsert_permission_async({
            "resource_id": resource_id,
            "resource_type": resource_type,
            "grantee_id": grantee_id,
            "grantee_type": grantee_type,
            "permission_level": level,
            "granted_by": self._user_id,
            "expires_at": expires_at,
        })

    def revoke(
        self,
        resource_type: ResourceType,
        resource_id: str,
        grantee_id: str,
        grantee_type: Literal["user", "group"] = "user",
    ) -> bool:
        """Revoke a permission.  Requires admin access on the resource."""
        self.require(resource_type, resource_id, "admin")
        return self._db.delete_permission(
            resource_id, resource_type, grantee_id, grantee_type
        )

    async def revoke_async(
        self,
        resource_type: ResourceType,
        resource_id: str,
        grantee_id: str,
        grantee_type: Literal["user", "group"] = "user",
    ) -> bool:
        await self.require_async(resource_type, resource_id, "admin")
        return await self._db.delete_permission_async(
            resource_id, resource_type, grantee_id, grantee_type
        )

    def list_permissions(
        self, resource_type: ResourceType, resource_id: str
    ) -> list[dict]:
        """List all permission grants on a resource.  Requires admin access."""
        self.require(resource_type, resource_id, "admin")
        return self._db.list_permissions(resource_id, resource_type)

    async def list_permissions_async(
        self, resource_type: ResourceType, resource_id: str
    ) -> list[dict]:
        await self.require_async(resource_type, resource_id, "admin")
        return await self._db.list_permissions_async(resource_id, resource_type)

    # ------------------------------------------------------------------
    # Share links
    # ------------------------------------------------------------------

    def create_share_link(
        self,
        resource_type: ResourceType,
        resource_id: str,
        permission_level: Literal["read", "write"] = "read",
        expires_at: str | None = None,
        max_uses: int | None = None,
    ) -> dict:
        """Create a shareable link.  Requires admin access on the resource."""
        self.require(resource_type, resource_id, "admin")
        return self._db.create_share_link({
            "resource_id": resource_id,
            "resource_type": resource_type,
            "permission_level": permission_level,
            "created_by": self._user_id,
            "expires_at": expires_at,
            "max_uses": max_uses,
        })

    async def create_share_link_async(
        self,
        resource_type: ResourceType,
        resource_id: str,
        permission_level: Literal["read", "write"] = "read",
        expires_at: str | None = None,
        max_uses: int | None = None,
    ) -> dict:
        await self.require_async(resource_type, resource_id, "admin")
        return await self._db.create_share_link_async({
            "resource_id": resource_id,
            "resource_type": resource_type,
            "permission_level": permission_level,
            "created_by": self._user_id,
            "expires_at": expires_at,
            "max_uses": max_uses,
        })

    def resolve_share_link(self, share_token: str) -> dict | None:
        """Look up a share link and increment its use counter.

        Returns the link record (with resource_id, resource_type,
        permission_level) or None if the link is invalid/expired/exhausted.
        """
        link = self._db.get_share_link(share_token)
        if not link or _is_expired(link):
            return None
        self._db.increment_share_link_use(share_token)
        return link

    async def resolve_share_link_async(self, share_token: str) -> dict | None:
        link = await self._db.get_share_link_async(share_token)
        if not link or _is_expired(link):
            return None
        await self._db.increment_share_link_use_async(share_token)
        return link

    def deactivate_share_link(self, share_token: str) -> bool:
        return self._db.deactivate_share_link(share_token)

    async def deactivate_share_link_async(self, share_token: str) -> bool:
        return await self._db.deactivate_share_link_async(share_token)

    def list_share_links(
        self, resource_type: ResourceType, resource_id: str
    ) -> list[dict]:
        self.require(resource_type, resource_id, "admin")
        return self._db.list_share_links(resource_id, resource_type)

    async def list_share_links_async(
        self, resource_type: ResourceType, resource_id: str
    ) -> list[dict]:
        await self.require_async(resource_type, resource_id, "admin")
        return await self._db.list_share_links_async(resource_id, resource_type)

    # ------------------------------------------------------------------
    # Group management
    # ------------------------------------------------------------------

    def create_group(self, name: str) -> dict:
        """Create a new user group owned by the current user."""
        return self._db.create_group({
            "name": name,
            "owner_id": self._user_id,
        })

    async def create_group_async(self, name: str) -> dict:
        return await self._db.create_group_async({
            "name": name,
            "owner_id": self._user_id,
        })

    def add_to_group(self, group_id: str, user_id: str, role: str = "member") -> dict:
        return self._db.add_group_member({
            "group_id": group_id,
            "user_id": user_id,
            "role": role,
            "added_by": self._user_id,
        })

    async def add_to_group_async(
        self, group_id: str, user_id: str, role: str = "member"
    ) -> dict:
        return await self._db.add_group_member_async({
            "group_id": group_id,
            "user_id": user_id,
            "role": role,
            "added_by": self._user_id,
        })

    def remove_from_group(self, group_id: str, user_id: str) -> bool:
        return self._db.remove_group_member(group_id, user_id)

    async def remove_from_group_async(self, group_id: str, user_id: str) -> bool:
        return await self._db.remove_group_member_async(group_id, user_id)

    def list_groups(self) -> list[dict]:
        return self._db.list_user_groups(self._user_id)

    async def list_groups_async(self) -> list[dict]:
        return await self._db.list_user_groups_async(self._user_id)

    def list_group_members(self, group_id: str) -> list[dict]:
        return self._db.list_group_members(group_id)

    async def list_group_members_async(self, group_id: str) -> list[dict]:
        return await self._db.list_group_members_async(group_id)
