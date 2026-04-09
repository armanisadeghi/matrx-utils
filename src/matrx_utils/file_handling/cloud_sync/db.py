"""Database client for the cloud sync layer.

Wraps the Supabase Python client to provide typed access to the
cloud_files, cloud_folders, cloud_file_versions, cloud_file_permissions,
cloud_share_links, cloud_user_groups, and cloud_user_group_members tables.

The client uses the service-role key, which bypasses Row Level Security.
RLS is enforced only for client-side (React/TypeScript) access.

Both sync and async APIs are provided.  Prefer async in FastAPI routes.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from .config import CloudSyncConfig

logger = logging.getLogger(__name__)

# Table names — centralised so a rename is a one-line change.
T_FILES = "cloud_files"
T_FOLDERS = "cloud_folders"
T_VERSIONS = "cloud_file_versions"
T_PERMISSIONS = "cloud_file_permissions"
T_SHARE_LINKS = "cloud_share_links"
T_GROUPS = "cloud_user_groups"
T_GROUP_MEMBERS = "cloud_user_group_members"


class DatabaseClient:
    """Thin wrapper over the Supabase PostgREST client.

    Lazy-initialises both sync and async Supabase clients on first use.
    """

    def __init__(self, config: CloudSyncConfig) -> None:
        self._config = config
        self._client: Any | None = None
        self._async_client: Any | None = None

    # ------------------------------------------------------------------
    # Lazy client accessors
    # ------------------------------------------------------------------

    def _get_client(self) -> Any:
        if self._client is None:
            from supabase import create_client
            url = self._config.resolve_supabase_url()
            key = self._config.resolve_supabase_key()
            if not url or not key:
                raise RuntimeError(
                    "Cloud sync database not configured. Provide supabase_url "
                    "and supabase_key in CloudSyncConfig, or set SUPABASE_URL "
                    "and SUPABASE_SECRET_KEY environment variables."
                )
            self._client = create_client(url, key)
        return self._client

    async def _get_async_client(self) -> Any:
        if self._async_client is None:
            from supabase import acreate_client
            url = self._config.resolve_supabase_url()
            key = self._config.resolve_supabase_key()
            if not url or not key:
                raise RuntimeError(
                    "Cloud sync database not configured. Provide supabase_url "
                    "and supabase_key in CloudSyncConfig, or set SUPABASE_URL "
                    "and SUPABASE_SECRET_KEY environment variables."
                )
            self._async_client = await acreate_client(url, key)
        return self._async_client

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    def _table(self, name: str) -> Any:
        return self._get_client().table(name)

    async def _atable(self, name: str) -> Any:
        client = await self._get_async_client()
        return client.table(name)

    @staticmethod
    def _strip_none(data: dict) -> dict:
        """Remove keys with None values so Postgres uses defaults."""
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def _first_or_none(response: Any) -> dict | None:
        if response.data:
            return response.data[0]
        return None

    # ==================================================================
    # FILES
    # ==================================================================

    def get_file(self, file_id: str) -> dict | None:
        resp = (
            self._table(T_FILES)
            .select("*")
            .eq("id", file_id)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._first_or_none(resp)

    async def get_file_async(self, file_id: str) -> dict | None:
        t = await self._atable(T_FILES)
        resp = await t.select("*").eq("id", file_id).is_("deleted_at", "null").execute()
        return self._first_or_none(resp)

    def get_file_by_path(self, owner_id: str, file_path: str) -> dict | None:
        resp = (
            self._table(T_FILES)
            .select("*")
            .eq("owner_id", owner_id)
            .eq("file_path", file_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._first_or_none(resp)

    async def get_file_by_path_async(self, owner_id: str, file_path: str) -> dict | None:
        t = await self._atable(T_FILES)
        resp = (
            await t.select("*")
            .eq("owner_id", owner_id)
            .eq("file_path", file_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._first_or_none(resp)

    def upsert_file(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = (
            self._table(T_FILES)
            .upsert(cleaned, on_conflict="owner_id,file_path")
            .execute()
        )
        return resp.data[0]

    async def upsert_file_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_FILES)
        resp = await t.upsert(cleaned, on_conflict="owner_id,file_path").execute()
        return resp.data[0]

    def update_file(self, file_id: str, updates: dict) -> dict | None:
        cleaned = self._strip_none(updates)
        resp = self._table(T_FILES).update(cleaned).eq("id", file_id).execute()
        return self._first_or_none(resp)

    async def update_file_async(self, file_id: str, updates: dict) -> dict | None:
        cleaned = self._strip_none(updates)
        t = await self._atable(T_FILES)
        resp = await t.update(cleaned).eq("id", file_id).execute()
        return self._first_or_none(resp)

    def soft_delete_file(self, file_id: str) -> bool:
        resp = (
            self._table(T_FILES)
            .update({"deleted_at": datetime.utcnow().isoformat()})
            .eq("id", file_id)
            .execute()
        )
        return bool(resp.data)

    async def soft_delete_file_async(self, file_id: str) -> bool:
        t = await self._atable(T_FILES)
        resp = (
            await t.update({"deleted_at": datetime.utcnow().isoformat()})
            .eq("id", file_id)
            .execute()
        )
        return bool(resp.data)

    def list_files(self, owner_id: str, folder_id: str | None = None) -> list[dict]:
        q = (
            self._table(T_FILES)
            .select("*")
            .eq("owner_id", owner_id)
            .is_("deleted_at", "null")
            .order("file_path")
        )
        if folder_id is not None:
            q = q.eq("parent_folder_id", folder_id)
        return q.execute().data

    async def list_files_async(
        self, owner_id: str, folder_id: str | None = None
    ) -> list[dict]:
        t = await self._atable(T_FILES)
        q = (
            t.select("*")
            .eq("owner_id", owner_id)
            .is_("deleted_at", "null")
            .order("file_path")
        )
        if folder_id is not None:
            q = q.eq("parent_folder_id", folder_id)
        return (await q.execute()).data

    # ==================================================================
    # FOLDERS
    # ==================================================================

    def get_folder(self, folder_id: str) -> dict | None:
        resp = (
            self._table(T_FOLDERS)
            .select("*")
            .eq("id", folder_id)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._first_or_none(resp)

    async def get_folder_async(self, folder_id: str) -> dict | None:
        t = await self._atable(T_FOLDERS)
        resp = await t.select("*").eq("id", folder_id).is_("deleted_at", "null").execute()
        return self._first_or_none(resp)

    def get_folder_by_path(self, owner_id: str, folder_path: str) -> dict | None:
        resp = (
            self._table(T_FOLDERS)
            .select("*")
            .eq("owner_id", owner_id)
            .eq("folder_path", folder_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._first_or_none(resp)

    async def get_folder_by_path_async(self, owner_id: str, folder_path: str) -> dict | None:
        t = await self._atable(T_FOLDERS)
        resp = (
            await t.select("*")
            .eq("owner_id", owner_id)
            .eq("folder_path", folder_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._first_or_none(resp)

    def upsert_folder(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = (
            self._table(T_FOLDERS)
            .upsert(cleaned, on_conflict="owner_id,folder_path")
            .execute()
        )
        return resp.data[0]

    async def upsert_folder_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_FOLDERS)
        resp = await t.upsert(cleaned, on_conflict="owner_id,folder_path").execute()
        return resp.data[0]

    def list_folders(self, owner_id: str, parent_id: str | None = None) -> list[dict]:
        q = (
            self._table(T_FOLDERS)
            .select("*")
            .eq("owner_id", owner_id)
            .is_("deleted_at", "null")
            .order("folder_path")
        )
        if parent_id is not None:
            q = q.eq("parent_id", parent_id)
        return q.execute().data

    async def list_folders_async(
        self, owner_id: str, parent_id: str | None = None
    ) -> list[dict]:
        t = await self._atable(T_FOLDERS)
        q = (
            t.select("*")
            .eq("owner_id", owner_id)
            .is_("deleted_at", "null")
            .order("folder_path")
        )
        if parent_id is not None:
            q = q.eq("parent_id", parent_id)
        return (await q.execute()).data

    # ==================================================================
    # VERSIONS
    # ==================================================================

    def create_version(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = self._table(T_VERSIONS).insert(cleaned).execute()
        return resp.data[0]

    async def create_version_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_VERSIONS)
        resp = await t.insert(cleaned).execute()
        return resp.data[0]

    def list_versions(self, file_id: str) -> list[dict]:
        return (
            self._table(T_VERSIONS)
            .select("*")
            .eq("file_id", file_id)
            .order("version_number", desc=True)
            .execute()
            .data
        )

    async def list_versions_async(self, file_id: str) -> list[dict]:
        t = await self._atable(T_VERSIONS)
        return (
            await t.select("*")
            .eq("file_id", file_id)
            .order("version_number", desc=True)
            .execute()
        ).data

    def get_version(self, file_id: str, version_number: int) -> dict | None:
        resp = (
            self._table(T_VERSIONS)
            .select("*")
            .eq("file_id", file_id)
            .eq("version_number", version_number)
            .execute()
        )
        return self._first_or_none(resp)

    async def get_version_async(self, file_id: str, version_number: int) -> dict | None:
        t = await self._atable(T_VERSIONS)
        resp = (
            await t.select("*")
            .eq("file_id", file_id)
            .eq("version_number", version_number)
            .execute()
        )
        return self._first_or_none(resp)

    # ==================================================================
    # PERMISSIONS
    # ==================================================================

    def upsert_permission(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = (
            self._table(T_PERMISSIONS)
            .upsert(cleaned, on_conflict="resource_id,resource_type,grantee_id,grantee_type")
            .execute()
        )
        return resp.data[0]

    async def upsert_permission_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_PERMISSIONS)
        resp = (
            await t.upsert(
                cleaned,
                on_conflict="resource_id,resource_type,grantee_id,grantee_type",
            ).execute()
        )
        return resp.data[0]

    def delete_permission(
        self,
        resource_id: str,
        resource_type: str,
        grantee_id: str,
        grantee_type: str = "user",
    ) -> bool:
        resp = (
            self._table(T_PERMISSIONS)
            .delete()
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .eq("grantee_id", grantee_id)
            .eq("grantee_type", grantee_type)
            .execute()
        )
        return bool(resp.data)

    async def delete_permission_async(
        self,
        resource_id: str,
        resource_type: str,
        grantee_id: str,
        grantee_type: str = "user",
    ) -> bool:
        t = await self._atable(T_PERMISSIONS)
        resp = (
            await t.delete()
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .eq("grantee_id", grantee_id)
            .eq("grantee_type", grantee_type)
            .execute()
        )
        return bool(resp.data)

    def list_permissions(self, resource_id: str, resource_type: str) -> list[dict]:
        return (
            self._table(T_PERMISSIONS)
            .select("*")
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .execute()
            .data
        )

    async def list_permissions_async(
        self, resource_id: str, resource_type: str
    ) -> list[dict]:
        t = await self._atable(T_PERMISSIONS)
        return (
            await t.select("*")
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .execute()
        ).data

    def get_user_permission(
        self,
        resource_id: str,
        resource_type: str,
        user_id: str,
    ) -> dict | None:
        """Get the direct user permission for a resource, if any."""
        resp = (
            self._table(T_PERMISSIONS)
            .select("*")
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .eq("grantee_id", user_id)
            .eq("grantee_type", "user")
            .execute()
        )
        return self._first_or_none(resp)

    async def get_user_permission_async(
        self,
        resource_id: str,
        resource_type: str,
        user_id: str,
    ) -> dict | None:
        t = await self._atable(T_PERMISSIONS)
        resp = (
            await t.select("*")
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .eq("grantee_id", user_id)
            .eq("grantee_type", "user")
            .execute()
        )
        return self._first_or_none(resp)

    # ==================================================================
    # SHARE LINKS
    # ==================================================================

    def create_share_link(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = self._table(T_SHARE_LINKS).insert(cleaned).execute()
        return resp.data[0]

    async def create_share_link_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_SHARE_LINKS)
        resp = await t.insert(cleaned).execute()
        return resp.data[0]

    def get_share_link(self, share_token: str) -> dict | None:
        resp = (
            self._table(T_SHARE_LINKS)
            .select("*")
            .eq("share_token", share_token)
            .eq("is_active", True)
            .execute()
        )
        return self._first_or_none(resp)

    async def get_share_link_async(self, share_token: str) -> dict | None:
        t = await self._atable(T_SHARE_LINKS)
        resp = (
            await t.select("*")
            .eq("share_token", share_token)
            .eq("is_active", True)
            .execute()
        )
        return self._first_or_none(resp)

    def list_share_links(self, resource_id: str, resource_type: str) -> list[dict]:
        return (
            self._table(T_SHARE_LINKS)
            .select("*")
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .eq("is_active", True)
            .execute()
            .data
        )

    async def list_share_links_async(
        self, resource_id: str, resource_type: str
    ) -> list[dict]:
        t = await self._atable(T_SHARE_LINKS)
        return (
            await t.select("*")
            .eq("resource_id", resource_id)
            .eq("resource_type", resource_type)
            .eq("is_active", True)
            .execute()
        ).data

    def deactivate_share_link(self, share_token: str) -> bool:
        resp = (
            self._table(T_SHARE_LINKS)
            .update({"is_active": False})
            .eq("share_token", share_token)
            .execute()
        )
        return bool(resp.data)

    async def deactivate_share_link_async(self, share_token: str) -> bool:
        t = await self._atable(T_SHARE_LINKS)
        resp = (
            await t.update({"is_active": False})
            .eq("share_token", share_token)
            .execute()
        )
        return bool(resp.data)

    def increment_share_link_use(self, share_token: str) -> dict | None:
        """Increment use_count and deactivate if max_uses reached."""
        link = self.get_share_link(share_token)
        if not link:
            return None
        new_count = link["use_count"] + 1
        updates: dict[str, Any] = {"use_count": new_count}
        if link.get("max_uses") and new_count >= link["max_uses"]:
            updates["is_active"] = False
        resp = (
            self._table(T_SHARE_LINKS)
            .update(updates)
            .eq("share_token", share_token)
            .execute()
        )
        return self._first_or_none(resp)

    async def increment_share_link_use_async(self, share_token: str) -> dict | None:
        link = await self.get_share_link_async(share_token)
        if not link:
            return None
        new_count = link["use_count"] + 1
        updates: dict[str, Any] = {"use_count": new_count}
        if link.get("max_uses") and new_count >= link["max_uses"]:
            updates["is_active"] = False
        t = await self._atable(T_SHARE_LINKS)
        resp = await t.update(updates).eq("share_token", share_token).execute()
        return self._first_or_none(resp)

    # ==================================================================
    # USER GROUPS
    # ==================================================================

    def create_group(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = self._table(T_GROUPS).insert(cleaned).execute()
        return resp.data[0]

    async def create_group_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_GROUPS)
        resp = await t.insert(cleaned).execute()
        return resp.data[0]

    def get_group(self, group_id: str) -> dict | None:
        resp = self._table(T_GROUPS).select("*").eq("id", group_id).execute()
        return self._first_or_none(resp)

    async def get_group_async(self, group_id: str) -> dict | None:
        t = await self._atable(T_GROUPS)
        resp = await t.select("*").eq("id", group_id).execute()
        return self._first_or_none(resp)

    def list_user_groups(self, user_id: str) -> list[dict]:
        """List groups the user owns or belongs to."""
        owned = (
            self._table(T_GROUPS)
            .select("*")
            .eq("owner_id", user_id)
            .execute()
            .data
        )
        member_of = (
            self._table(T_GROUP_MEMBERS)
            .select("group_id")
            .eq("user_id", user_id)
            .execute()
            .data
        )
        member_ids = {m["group_id"] for m in member_of}
        owned_ids = {g["id"] for g in owned}
        extra_ids = member_ids - owned_ids
        if extra_ids:
            extra = (
                self._table(T_GROUPS)
                .select("*")
                .in_("id", list(extra_ids))
                .execute()
                .data
            )
            owned.extend(extra)
        return owned

    async def list_user_groups_async(self, user_id: str) -> list[dict]:
        t_groups = await self._atable(T_GROUPS)
        t_members = await self._atable(T_GROUP_MEMBERS)
        owned = (await t_groups.select("*").eq("owner_id", user_id).execute()).data
        member_of = (
            await t_members.select("group_id").eq("user_id", user_id).execute()
        ).data
        member_ids = {m["group_id"] for m in member_of}
        owned_ids = {g["id"] for g in owned}
        extra_ids = member_ids - owned_ids
        if extra_ids:
            t_groups2 = await self._atable(T_GROUPS)
            extra = (
                await t_groups2.select("*").in_("id", list(extra_ids)).execute()
            ).data
            owned.extend(extra)
        return owned

    def delete_group(self, group_id: str) -> bool:
        resp = self._table(T_GROUPS).delete().eq("id", group_id).execute()
        return bool(resp.data)

    async def delete_group_async(self, group_id: str) -> bool:
        t = await self._atable(T_GROUPS)
        resp = await t.delete().eq("id", group_id).execute()
        return bool(resp.data)

    # ==================================================================
    # GROUP MEMBERS
    # ==================================================================

    def add_group_member(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        resp = (
            self._table(T_GROUP_MEMBERS)
            .upsert(cleaned, on_conflict="group_id,user_id")
            .execute()
        )
        return resp.data[0]

    async def add_group_member_async(self, data: dict) -> dict:
        cleaned = self._strip_none(data)
        t = await self._atable(T_GROUP_MEMBERS)
        resp = await t.upsert(cleaned, on_conflict="group_id,user_id").execute()
        return resp.data[0]

    def remove_group_member(self, group_id: str, user_id: str) -> bool:
        resp = (
            self._table(T_GROUP_MEMBERS)
            .delete()
            .eq("group_id", group_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(resp.data)

    async def remove_group_member_async(self, group_id: str, user_id: str) -> bool:
        t = await self._atable(T_GROUP_MEMBERS)
        resp = await t.delete().eq("group_id", group_id).eq("user_id", user_id).execute()
        return bool(resp.data)

    def list_group_members(self, group_id: str) -> list[dict]:
        return (
            self._table(T_GROUP_MEMBERS)
            .select("*")
            .eq("group_id", group_id)
            .execute()
            .data
        )

    async def list_group_members_async(self, group_id: str) -> list[dict]:
        t = await self._atable(T_GROUP_MEMBERS)
        return (await t.select("*").eq("group_id", group_id).execute()).data

    def get_user_group_ids(self, user_id: str) -> list[str]:
        """Return group IDs the user belongs to (for permission resolution)."""
        rows = (
            self._table(T_GROUP_MEMBERS)
            .select("group_id")
            .eq("user_id", user_id)
            .execute()
            .data
        )
        return [r["group_id"] for r in rows]

    async def get_user_group_ids_async(self, user_id: str) -> list[str]:
        t = await self._atable(T_GROUP_MEMBERS)
        rows = (await t.select("group_id").eq("user_id", user_id).execute()).data
        return [r["group_id"] for r in rows]
