"""Database client for the cloud sync layer.

Wraps the Supabase Python client to provide typed access to the file
tables, which live in the dedicated ``files`` Postgres schema (the
2026 DB canonicalization moved them out of ``public`` and dropped the
``cld_`` prefix): ``files.files``, ``files.folders``,
``files.file_versions``, ``files.share_links``, ``files.uploads_inflight``,
``files.webhooks``, ``files.webhook_deliveries``, ``files.idempotency``,
``files.user_account``, ``files.account_tiers``,
``files.user_storage_usage``, ``files.file_rag_jobs`` and siblings.

Permissions are NOT a file-schema table — file ACLs now live in the
canonical ``iam.permissions`` table and resolve through the
``iam.has_access`` / ``public.has_permission`` RPCs (see permissions.py).
The legacy ``cld_user_groups`` user-group feature is dead and removed.

The client uses the service-role key, which bypasses Row Level Security.
RLS is enforced only for client-side (React/TypeScript) access.

Both sync and async APIs are provided.  Prefer async in FastAPI routes.

ALL file-schema access goes through ``schema(SCHEMA_FILES).table(...)`` —
centralised here via ``_table`` / ``_atable`` and the module-level
``files_table`` / ``afiles_table`` helpers so the schema is set in ONE
place. IAM ACL access goes through ``schema(SCHEMA_IAM).table(...)`` via
``_iam_table`` / ``_aiam_table``. Never call bare ``client.table(...)``
against the default (``public``) schema — it 404s (PGRST205).
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

from .config import CloudSyncConfig

logger = logging.getLogger(__name__)

# The Postgres schema the file tables live in (post-2026 canonicalization).
SCHEMA_FILES = "files"
# File ACLs live in the canonical IAM schema — NOT public, NOT files.
SCHEMA_IAM = "iam"

# Table names within SCHEMA_FILES — centralised so a move is a one-line
# change. These are BARE names (no schema, no ``cld_`` prefix); the schema
# is applied by the ``files_table`` / ``afiles_table`` helpers below.
T_FILES = "files"
T_FOLDERS = "folders"
T_VERSIONS = "file_versions"
T_SHARE_LINKS = "share_links"
T_UPLOADS = "uploads_inflight"
T_IDEMPOTENCY = "idempotency"
T_USER_ACCOUNT = "user_account"
T_ACCOUNT_TIERS = "account_tiers"
T_STORAGE_USAGE = "user_storage_usage"
T_RAG_JOBS = "file_rag_jobs"
T_PERMISSIONS = "permissions"

# Safe outbound file fields — everything a client / agent tool may see.
# Deliberately EXCLUDES the server-only ``storage_uri`` (must never leave the
# server — files are identified by ``id``; see file_handling/FEATURE.md) and
# the legacy ``owner_id`` alias (annihilated — the canonical column is
# ``created_by``). Consumed by ``list_files_filtered_async``.
SAFE_FILE_FIELDS = (
    "id, created_by, organization_id, parent_folder_id, file_path, file_name, "
    "mime_type, size_bytes, checksum, visibility, current_version, "
    "width, height, duration_ms, metadata, created_at, updated_at, deleted_at"
)


def files_table(client: Any, name: str) -> Any:
    """Return a query builder bound to a table in the ``files`` schema.

    ``client`` is a SYNC Supabase client. Use this everywhere instead of
    ``client.table(name)`` so the file schema is set in exactly one place.
    """
    return client.schema(SCHEMA_FILES).table(name)


def afiles_table(client: Any, name: str) -> Any:
    """Return a query builder bound to a table in the ``files`` schema.

    ``client`` is an ASYNC Supabase client. ``.schema().table()`` is
    synchronous construction on the async client (only ``.execute()`` is
    awaited), so this helper is not a coroutine.
    """
    return client.schema(SCHEMA_FILES).table(name)


def iam_table(client: Any, name: str) -> Any:
    """Return a query builder bound to a table in the ``iam`` schema."""
    return client.schema(SCHEMA_IAM).table(name)


def aiam_table(client: Any, name: str) -> Any:
    """Return a query builder bound to a table in the ``iam`` schema (async client)."""
    return client.schema(SCHEMA_IAM).table(name)


class DatabaseClient:
    """Thin wrapper over the Supabase PostgREST client.

    Lazy-initialises both sync and async Supabase clients on first use.
    """

    def __init__(self, config: CloudSyncConfig) -> None:
        self._config = config
        self._client: Any | None = None
        self._async_client: Any | None = None
        # Personal-org cache (uid -> org uuid). A user's personal org is
        # immutable, so caching for the process lifetime avoids an RPC per write.
        self._personal_org_cache: dict[str, str] = {}

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
            client = await acreate_client(url, key)
            # Supabase builds the PostgREST sub-client lazily on the first
            # `.table()` / `.rpc()` call. That construction creates an
            # httpx.AsyncClient, which synchronously builds an SSL context
            # (ssl.create_default_context(cafile=certifi.where())) — a
            # CPU/IO-bound operation that can block the event loop for ~1s on
            # a cold process. Warm it in a thread here so the freeze never
            # lands on the loop, regardless of which consumer hits the client
            # first. Accessing `.postgrest` triggers _init_postgrest_client.
            await asyncio.to_thread(lambda: client.postgrest)
            self._async_client = client
        return self._async_client

    # ------------------------------------------------------------------
    # Generic helpers
    # ------------------------------------------------------------------

    def _table(self, name: str) -> Any:
        """Files-schema table builder (sync). All file tables live in
        ``files``; this binds the schema in one place."""
        return files_table(self._get_client(), name)

    async def _atable(self, name: str) -> Any:
        """Files-schema table builder (async)."""
        client = await self._get_async_client()
        return afiles_table(client, name)

    def _iam_table(self, name: str) -> Any:
        """IAM-schema table builder (sync). ACLs live in ``iam``."""
        return iam_table(self._get_client(), name)

    async def _aiam_table(self, name: str) -> Any:
        """IAM-schema table builder (async)."""
        client = await self._get_async_client()
        return aiam_table(client, name)

    @staticmethod
    def _strip_none(data: dict) -> dict:
        """Remove keys with None values so Postgres uses defaults."""
        return {k: v for k, v in data.items() if v is not None}

    @staticmethod
    def _first_or_none(response: Any) -> dict | None:
        if response.data:
            return response.data[0]
        return None

    # ------------------------------------------------------------------
    # owner_id <-> created_by boundary shim (files / folders only)
    # ------------------------------------------------------------------
    # The 2026 DB canonicalization renamed the owner column on the entity
    # tables (files.files / files.folders) from ``owner_id`` to the
    # canonical ``created_by``. The whole Python layer (CloudFile/CloudFolder
    # models, sync_engine, every aidream caller — 200+ references) still
    # speaks ``owner_id``, so we translate in EXACTLY ONE place: here, at the
    # PostgREST boundary. Writes map owner_id -> created_by on the way in;
    # reads add owner_id back from created_by on the way out, so callers that
    # construct models OR read ``row["owner_id"]`` directly are unchanged.
    # Sibling tables keep their own owner columns and never touch this shim:
    # uploads_inflight / idempotency / webhooks -> owner_id (unchanged);
    # user_account / user_storage_usage / file_rag_jobs -> user_id;
    # file_versions / share_links -> created_by (their models already use it).
    # Legacy 'shared' visibility -> canonical 'private'. The platform.visibility
    # enum is private<internal<link<public; the removed 'shared' value meant
    # "private file shared with specific users", which is now expressed purely
    # by iam.permissions rows (sharing is independent of ambient visibility).
    # Normalising here — the single files/folders write choke point — means a
    # legacy 'shared' from ANY of the ~15 API boundaries can never reach the DB
    # enum (which would 500), without 422-ing clients that still send it.
    _LEGACY_VISIBILITY = {"shared": "private"}

    @classmethod
    def _owner_to_db(cls, data: dict) -> dict:
        """files/folders write-prep: owner_id->created_by + visibility normalise."""
        out = data
        if "owner_id" in out:
            out = {k: v for k, v in out.items() if k != "owner_id"}
            out["created_by"] = data["owner_id"]
        vis = out.get("visibility")
        if vis in cls._LEGACY_VISIBILITY:
            if out is data:
                out = dict(data)
            out["visibility"] = cls._LEGACY_VISIBILITY[vis]
        return out

    @staticmethod
    def _owner_from_db(row: dict | None) -> dict | None:
        """files/folders read: expose created_by (DB) as owner_id (Python)."""
        if row is not None and "created_by" in row and "owner_id" not in row:
            return {**row, "owner_id": row["created_by"]}
        return row

    @classmethod
    def _owner_from_db_many(cls, rows: list[dict] | None) -> list[dict]:
        return [cls._owner_from_db(r) for r in (rows or [])]

    # ==================================================================
    # FILES
    # ==================================================================

    def get_file(self, file_id: str, *, include_deleted: bool = False) -> dict | None:
        q = self._table(T_FILES).select("*").eq("id", file_id)
        if not include_deleted:
            q = q.is_("deleted_at", "null")
        resp = q.execute()
        return self._owner_from_db(self._first_or_none(resp))

    async def get_file_async(
        self, file_id: str, *, include_deleted: bool = False
    ) -> dict | None:
        t = await self._atable(T_FILES)
        q = t.select("*").eq("id", file_id)
        if not include_deleted:
            q = q.is_("deleted_at", "null")
        resp = await q.execute()
        return self._owner_from_db(self._first_or_none(resp))

    def get_file_by_path(self, owner_id: str, file_path: str) -> dict | None:
        resp = (
            self._table(T_FILES)
            .select("*")
            .eq("created_by", owner_id)
            .eq("file_path", file_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._owner_from_db(self._first_or_none(resp))

    async def get_file_by_path_async(
        self, owner_id: str, file_path: str
    ) -> dict | None:
        t = await self._atable(T_FILES)
        resp = (
            await t.select("*")
            .eq("created_by", owner_id)
            .eq("file_path", file_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._owner_from_db(self._first_or_none(resp))

    # ------------------------------------------------------------------
    # Dedup lookups by content hash. Used by the FileService intent
    # contract (intent='create' / 'alias_existing' / 'force_new_copy').
    # Returns the OLDEST non-deleted, non-duplicate row in the scope so
    # the keeper is stable across calls.
    # ------------------------------------------------------------------

    def get_file_by_checksum(
        self,
        checksum: str,
        *,
        owner_id: str | None = None,
        organization_id: str | None = None,
    ) -> dict | None:
        q = (
            self._table(T_FILES)
            .select("*")
            .eq("checksum", checksum)
            .is_("deleted_at", "null")
            .is_("duplicate_of_file_id", "null")
        )
        if organization_id is not None:
            q = q.eq("organization_id", organization_id)
        elif owner_id is not None:
            q = q.eq("created_by", owner_id).is_("organization_id", "null")
        else:
            return None
        resp = q.order("created_at", desc=False).limit(1).execute()
        return self._owner_from_db(self._first_or_none(resp))

    async def get_file_by_checksum_async(
        self,
        checksum: str,
        *,
        owner_id: str | None = None,
        organization_id: str | None = None,
    ) -> dict | None:
        """Find the canonical (oldest, non-deleted, non-duplicate-alias)
        cld_files row for a given content checksum.

        Org-scope wins if ``organization_id`` is provided: the file is
        canonical across the whole org. Otherwise it's owner-scoped to
        personal libraries. Returns ``None`` if no match.
        """
        if not checksum:
            return None
        t = await self._atable(T_FILES)
        q = (
            t.select("*")
            .eq("checksum", checksum)
            .is_("deleted_at", "null")
            .is_("duplicate_of_file_id", "null")
        )
        if organization_id is not None:
            q = q.eq("organization_id", organization_id)
        elif owner_id is not None:
            q = q.eq("created_by", owner_id).is_("organization_id", "null")
        else:
            return None
        resp = await q.order("created_at", desc=False).limit(1).execute()
        return self._owner_from_db(self._first_or_none(resp))

    def upsert_file(self, data: dict) -> dict:
        cleaned = self._owner_to_db(self._strip_none(data))
        if "id" in cleaned:
            # Pinned-id insert — plain insert, never an ON CONFLICT upsert.
            # See upsert_file_async for the full rationale (a concurrent
            # collision would otherwise rewrite the winning row's primary
            # key and orphan its pending cld_file_versions insert).
            resp = self._table(T_FILES).insert(cleaned).execute()
            return self._owner_from_db(resp.data[0])
        resp = (
            self._table(T_FILES)
            .upsert(cleaned, on_conflict="created_by,file_path")
            .execute()
        )
        return self._owner_from_db(resp.data[0])

    async def upsert_file_async(self, data: dict) -> dict:
        cleaned = self._owner_to_db(self._strip_none(data))
        t = await self._atable(T_FILES)
        if "id" in cleaned:
            # Pinned-id insert (canonical-key scheme: TUS / AI media /
            # variants). A pinned id means a brand-new row — it must NEVER
            # be an ``ON CONFLICT (owner_id, file_path) DO UPDATE`` upsert.
            # On a concurrent collision that upsert runs ``SET id=<new uuid>``
            # against the row that already won (owner_id, file_path),
            # rewriting THAT row's primary key (the FK to cld_file_versions
            # is ON DELETE CASCADE with no ON UPDATE, so a not-yet-referenced
            # id is freely mutable) and orphaning the winner's pending
            # cld_file_versions insert (FK 23503). A plain insert instead
            # raises 23505 on a genuine path collision, which the caller's
            # race-recovery path resolves by reading the winning row.
            resp = await t.insert(cleaned).execute()
            return self._owner_from_db(resp.data[0])
        resp = await t.upsert(cleaned, on_conflict="created_by,file_path").execute()
        return self._owner_from_db(resp.data[0])

    def ensure_personal_organization(self, user_id: str) -> str | None:
        """Sync twin of :meth:`ensure_personal_organization_async`."""
        if not user_id:
            return None
        cached = self._personal_org_cache.get(user_id)
        if cached:
            return cached
        client = self._get_client()
        resp = client.rpc(
            "ensure_personal_organization", {"p_user_id": user_id}
        ).execute()
        org_id = resp.data if isinstance(resp.data, str) else None
        if org_id:
            self._personal_org_cache[user_id] = org_id
        return org_id

    async def ensure_personal_organization_async(self, user_id: str) -> str | None:
        """Resolve the user's personal-org UUID via the SECURITY DEFINER RPC.

        Every cld_files row MUST carry a non-NULL organization_id (the
        platform org-scoping invariant). When a write supplies no explicit
        org, the owner's personal org is the default — resolved here.
        Result is cached per process (personal org is immutable).

        Returns None only if resolution fails; callers must treat that as a
        loud fallback, never a silent NULL they're happy with.
        """
        if not user_id:
            return None
        cached = self._personal_org_cache.get(user_id)
        if cached:
            return cached
        client = await self._get_async_client()
        resp = await client.rpc(
            "ensure_personal_organization", {"p_user_id": user_id}
        ).execute()
        org_id = resp.data if isinstance(resp.data, str) else None
        if org_id:
            self._personal_org_cache[user_id] = org_id
        return org_id

    def update_file(self, file_id: str, updates: dict) -> dict | None:
        cleaned = self._owner_to_db(self._strip_none(updates))
        resp = self._table(T_FILES).update(cleaned).eq("id", file_id).execute()
        return self._owner_from_db(self._first_or_none(resp))

    async def update_file_async(self, file_id: str, updates: dict) -> dict | None:
        cleaned = self._owner_to_db(self._strip_none(updates))
        t = await self._atable(T_FILES)
        resp = await t.update(cleaned).eq("id", file_id).execute()
        return self._owner_from_db(self._first_or_none(resp))

    def soft_delete_file(self, file_id: str) -> bool:
        # Prefer the cascade-aware SQL function which also deactivates share
        # links pointing at the file. Falls back to the column-only update if
        # the RPC isn't installed (older schemas).
        try:
            client = self._get_client()
            resp = client.rpc("soft_delete_file", {"p_file_id": file_id}).execute()
            return bool(resp.data)
        except Exception:
            resp = (
                self._table(T_FILES)
                .update({"deleted_at": datetime.now(UTC).isoformat()})
                .eq("id", file_id)
                .execute()
            )
            return bool(resp.data)

    async def soft_delete_file_async(self, file_id: str) -> bool:
        try:
            client = await self._get_async_client()
            resp = await client.rpc(
                "soft_delete_file", {"p_file_id": file_id}
            ).execute()
            return bool(resp.data)
        except Exception:
            t = await self._atable(T_FILES)
            resp = (
                await t.update({"deleted_at": datetime.now(UTC).isoformat()})
                .eq("id", file_id)
                .execute()
            )
            return bool(resp.data)

    # Hard delete: returns the storage URIs that need to be purged from S3.
    def hard_delete_file(self, file_id: str) -> dict | None:
        client = self._get_client()
        resp = client.rpc("hard_delete_file", {"p_file_id": file_id}).execute()
        return resp.data if isinstance(resp.data, dict) else None

    async def hard_delete_file_async(self, file_id: str) -> dict | None:
        client = await self._get_async_client()
        resp = await client.rpc("hard_delete_file", {"p_file_id": file_id}).execute()
        return resp.data if isinstance(resp.data, dict) else None

    def list_files(self, owner_id: str, folder_id: str | None = None) -> list[dict]:
        q = (
            self._table(T_FILES)
            .select("*")
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .order("file_path")
        )
        if folder_id is not None:
            q = q.eq("parent_folder_id", folder_id)
        return self._owner_from_db_many(q.execute().data)

    async def list_files_async(
        self, owner_id: str, folder_id: str | None = None
    ) -> list[dict]:
        t = await self._atable(T_FILES)
        q = (
            t.select("*")
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .order("file_path")
        )
        if folder_id is not None:
            q = q.eq("parent_folder_id", folder_id)
        return self._owner_from_db_many((await q.execute()).data)

    async def list_files_paginated_async(
        self,
        owner_id: str,
        prefix: str | None = None,
        limit: int = 1000,
    ) -> list[dict]:
        """Bounded listing for a user's files, optional path prefix.

        Pushes the prefix filter + ``limit`` into the database instead of
        pulling every row and filtering in Python — same loop-stall class as
        ``list_changed_files_async``.
        """
        t = await self._atable(T_FILES)
        q = (
            t.select(
                "id,file_path,size_bytes,mime_type,current_version,checksum,updated_at,created_at"
            )
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .order("file_path")
            .limit(limit)
        )
        if prefix:
            q = q.like("file_path", f"{prefix}%")
        return self._owner_from_db_many((await q.execute()).data)

    async def list_files_filtered_async(
        self,
        created_by: str,
        *,
        folder_id: str | None = None,
        mime_prefix: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[dict]:
        """Owner-scoped file listing with folder + mime-prefix filters and
        offset pagination — the canonical primitive behind the ``cloud_file``
        agent tool's ``list`` action.

        Scoped by the canonical ``created_by`` column (NEVER the legacy
        ``owner_id`` alias, which is being annihilated). Selects an explicit
        safe field set — ``SAFE_FILE_FIELDS`` — so the server-only
        ``storage_uri`` can never leave the server, and returns rows AS-IS
        (no ``owner_id`` shim re-added). Newest first.
        """
        t = await self._atable(T_FILES)
        q = (
            t.select(SAFE_FILE_FIELDS)
            .eq("created_by", created_by)
            .is_("deleted_at", "null")
        )
        if folder_id:
            q = q.eq("parent_folder_id", folder_id)
        if mime_prefix:
            q = q.like("mime_type", f"{mime_prefix}%")
        resp = (
            await q.order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resp.data or []

    async def get_storage_usage_async(self, owner_id: str) -> dict:
        """Total bytes + file count for a user, parsed lean.

        Selects only ``size_bytes`` (not ``*``) so even for a user with many
        files the postgrest response is tiny and its synchronous parse can't
        stall the loop — the same failure quota/used-bytes used to risk by
        pulling every full row just to sum one column.
        """
        t = await self._atable(T_FILES)
        rows = (
            await t.select("size_bytes")
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .execute()
        ).data
        total = sum(int(r.get("size_bytes") or 0) for r in rows)
        return {"used_bytes": total, "files_count": len(rows)}

    async def list_changed_files_async(
        self,
        owner_id: str,
        since_iso: str,
        limit: int = 1000,
    ) -> list[dict]:
        """Server-side "changes since" query for the down-sync poll fallback.

        Filters ``updated_at > since`` and bounds the result set in the
        database — instead of pulling every one of a user's rows and filtering
        in Python. Selecting a narrow column set + a hard ``limit`` keeps the
        postgrest response small enough that its synchronous parse/validate
        can never stall the event loop (the 2026-06-12 ``event_loop_stall``).
        """
        t = await self._atable(T_FILES)
        q = (
            t.select(
                "id,file_path,size_bytes,mime_type,current_version,checksum,updated_at,created_at"
            )
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .gt("updated_at", since_iso)
            .order("updated_at")
            .limit(limit)
        )
        return self._owner_from_db_many((await q.execute()).data)

    def list_variants_by_master(self, master_file_id: str) -> list[dict]:
        """Every cld_files row whose metadata.derived_from == master_file_id.

        Backs the VariantsService 'look before render' check — given a
        master, returns the catalog of already-rendered variants so we
        can skip the encoder for keys that already exist.
        """
        resp = (
            self._table(T_FILES)
            .select("*")
            .eq("metadata->>derived_from", master_file_id)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._owner_from_db_many(resp.data)

    async def list_variants_by_master_async(self, master_file_id: str) -> list[dict]:
        t = await self._atable(T_FILES)
        resp = await (
            t.select("*")
            .eq("metadata->>derived_from", master_file_id)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._owner_from_db_many(resp.data)

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
        return self._owner_from_db(self._first_or_none(resp))

    async def get_folder_async(self, folder_id: str) -> dict | None:
        t = await self._atable(T_FOLDERS)
        resp = (
            await t.select("*").eq("id", folder_id).is_("deleted_at", "null").execute()
        )
        return self._owner_from_db(self._first_or_none(resp))

    def get_folder_by_path(self, owner_id: str, folder_path: str) -> dict | None:
        resp = (
            self._table(T_FOLDERS)
            .select("*")
            .eq("created_by", owner_id)
            .eq("folder_path", folder_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._owner_from_db(self._first_or_none(resp))

    async def get_folder_by_path_async(
        self, owner_id: str, folder_path: str
    ) -> dict | None:
        t = await self._atable(T_FOLDERS)
        resp = (
            await t.select("*")
            .eq("created_by", owner_id)
            .eq("folder_path", folder_path)
            .is_("deleted_at", "null")
            .execute()
        )
        return self._owner_from_db(self._first_or_none(resp))

    def upsert_folder(self, data: dict) -> dict:
        cleaned = self._owner_to_db(self._strip_none(data))
        resp = (
            self._table(T_FOLDERS)
            .upsert(cleaned, on_conflict="created_by,folder_path")
            .execute()
        )
        return self._owner_from_db(resp.data[0])

    async def upsert_folder_async(self, data: dict) -> dict:
        cleaned = self._owner_to_db(self._strip_none(data))
        t = await self._atable(T_FOLDERS)
        resp = await t.upsert(cleaned, on_conflict="created_by,folder_path").execute()
        return self._owner_from_db(resp.data[0])

    def list_folders(self, owner_id: str, parent_id: str | None = None) -> list[dict]:
        q = (
            self._table(T_FOLDERS)
            .select("*")
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .order("folder_path")
        )
        if parent_id is not None:
            q = q.eq("parent_id", parent_id)
        return self._owner_from_db_many(q.execute().data)

    async def list_folders_async(
        self, owner_id: str, parent_id: str | None = None
    ) -> list[dict]:
        t = await self._atable(T_FOLDERS)
        q = (
            t.select("*")
            .eq("created_by", owner_id)
            .is_("deleted_at", "null")
            .order("folder_path")
        )
        if parent_id is not None:
            q = q.eq("parent_id", parent_id)
        return self._owner_from_db_many((await q.execute()).data)

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
    # PERMISSIONS  (canonical iam.permissions)
    # ==================================================================
    #
    # File ACLs moved off the graveyarded ``cld_file_permissions`` table
    # onto the canonical ``iam.permissions`` (resource_type + resource_id
    # + granted_to_user_id / granted_to_organization_id, permission_level
    # enum viewer<editor<admin, created_by, status='active'). The user-group
    # feature is dead — only direct user grants (and, for completeness, org
    # grants) are supported here.
    #
    # The method signatures + the dict shape callers pass/receive are kept
    # stable (resource_id, resource_type, grantee_id, grantee_type,
    # permission_level in read/write/admin, granted_by, expires_at) so call
    # sites in service.py / sync_engine.py / permissions.py are unchanged.
    # Translation to/from the canonical columns happens here, in one place.

    # legacy file-ACL level  <->  canonical permission_level enum
    _LEVEL_TO_CANONICAL = {"read": "viewer", "write": "editor", "admin": "admin"}
    _LEVEL_FROM_CANONICAL = {"viewer": "read", "editor": "write", "admin": "admin"}

    @classmethod
    def _to_canonical_permission(cls, data: dict) -> dict:
        """Map a legacy file-ACL grant dict onto a iam.permissions row."""
        grantee_type = data.get("grantee_type") or "user"
        if grantee_type not in ("user", "organization"):
            # 'group' (and anything else) is the dead user-group path.
            raise ValueError(
                f"Unsupported grantee_type {grantee_type!r}; the user-group "
                "ACL path is removed — only 'user'/'organization' grants exist."
            )
        level = data.get("permission_level") or "read"
        row: dict[str, Any] = {
            "resource_type": data["resource_type"],
            "resource_id": data["resource_id"],
            "permission_level": cls._LEVEL_TO_CANONICAL.get(level, level),
            "created_by": data.get("granted_by"),
            "status": "active",
            "expires_at": data.get("expires_at"),
        }
        if grantee_type == "organization":
            row["granted_to_organization_id"] = data["grantee_id"]
        else:
            row["granted_to_user_id"] = data["grantee_id"]
        return row

    @classmethod
    def _from_canonical_permission(cls, row: dict) -> dict:
        """Map a iam.permissions row back to the legacy file-ACL shape
        that callers expect (permission_level read/write/admin, grantee_*)."""
        if row.get("granted_to_organization_id"):
            grantee_type = "organization"
            grantee_id = row.get("granted_to_organization_id")
        else:
            grantee_type = "user"
            grantee_id = row.get("granted_to_user_id")
        level = row.get("permission_level")
        return {
            **row,
            "grantee_type": grantee_type,
            "grantee_id": grantee_id,
            "permission_level": cls._LEVEL_FROM_CANONICAL.get(level, level),
            "granted_by": row.get("created_by"),
        }

    @staticmethod
    def _permission_conflict_key(grantee_type: str) -> str:
        return (
            "resource_type,resource_id,granted_to_organization_id"
            if grantee_type == "organization"
            else "resource_type,resource_id,granted_to_user_id"
        )

    def upsert_permission(self, data: dict) -> dict:
        row = self._strip_none(self._to_canonical_permission(data))
        conflict = self._permission_conflict_key(data.get("grantee_type") or "user")
        resp = (
            self._iam_table(T_PERMISSIONS).upsert(row, on_conflict=conflict).execute()
        )
        return self._from_canonical_permission(resp.data[0])

    async def upsert_permission_async(self, data: dict) -> dict:
        row = self._strip_none(self._to_canonical_permission(data))
        conflict = self._permission_conflict_key(data.get("grantee_type") or "user")
        t = await self._aiam_table(T_PERMISSIONS)
        resp = await t.upsert(row, on_conflict=conflict).execute()
        return self._from_canonical_permission(resp.data[0])

    def _delete_permission_query(
        self, client_table: Any, resource_id, resource_type, grantee_id, grantee_type
    ):
        q = (
            client_table.delete()
            .eq("resource_type", resource_type)
            .eq("resource_id", resource_id)
        )
        if grantee_type == "organization":
            return q.eq("granted_to_organization_id", grantee_id)
        return q.eq("granted_to_user_id", grantee_id)

    def delete_permission(
        self,
        resource_id: str,
        resource_type: str,
        grantee_id: str,
        grantee_type: str = "user",
    ) -> bool:
        t = self._iam_table(T_PERMISSIONS)
        resp = self._delete_permission_query(
            t, resource_id, resource_type, grantee_id, grantee_type
        ).execute()
        return bool(resp.data)

    async def delete_permission_async(
        self,
        resource_id: str,
        resource_type: str,
        grantee_id: str,
        grantee_type: str = "user",
    ) -> bool:
        t = await self._aiam_table(T_PERMISSIONS)
        resp = await self._delete_permission_query(
            t, resource_id, resource_type, grantee_id, grantee_type
        ).execute()
        return bool(resp.data)

    def list_permissions(self, resource_id: str, resource_type: str) -> list[dict]:
        resp = (
            self._iam_table(T_PERMISSIONS)
            .select("*")
            .eq("resource_type", resource_type)
            .eq("resource_id", resource_id)
            .eq("status", "active")
            .execute()
        )
        return [self._from_canonical_permission(r) for r in (resp.data or [])]

    async def list_permissions_async(
        self, resource_id: str, resource_type: str
    ) -> list[dict]:
        t = await self._aiam_table(T_PERMISSIONS)
        resp = (
            await t.select("*")
            .eq("resource_type", resource_type)
            .eq("resource_id", resource_id)
            .eq("status", "active")
            .execute()
        )
        return [self._from_canonical_permission(r) for r in (resp.data or [])]

    def get_user_permission(
        self,
        resource_id: str,
        resource_type: str,
        user_id: str,
    ) -> dict | None:
        """Get the direct user permission for a resource, if any."""
        resp = (
            self._iam_table(T_PERMISSIONS)
            .select("*")
            .eq("resource_type", resource_type)
            .eq("resource_id", resource_id)
            .eq("granted_to_user_id", user_id)
            .eq("status", "active")
            .execute()
        )
        row = self._first_or_none(resp)
        return self._from_canonical_permission(row) if row else None

    async def get_user_permission_async(
        self,
        resource_id: str,
        resource_type: str,
        user_id: str,
    ) -> dict | None:
        t = await self._aiam_table(T_PERMISSIONS)
        resp = (
            await t.select("*")
            .eq("resource_type", resource_type)
            .eq("resource_id", resource_id)
            .eq("granted_to_user_id", user_id)
            .eq("status", "active")
            .execute()
        )
        row = self._first_or_none(resp)
        return self._from_canonical_permission(row) if row else None

    def has_platform_viewer_access(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
    ) -> bool:
        """Ask ``public.has_access_as`` — the platform judge with an explicit user.

        Used for Shared Knowledge / reachability cascades (e.g. industry grant
        on a data_store → member file). Service-role clients cannot use
        ``iam.has_access`` (``auth.uid()`` is NULL); this RPC takes ``p_user``.
        Viewer only — never elevates to write/admin.
        """
        if not user_id or not resource_id:
            return False
        client = self._get_client()
        resp = client.rpc(
            "has_access_as",
            {
                "p_user": user_id,
                "p_type": resource_type,
                "p_id": resource_id,
                "p_required": "viewer",
            },
        ).execute()
        return bool(resp.data)

    async def has_platform_viewer_access_async(
        self,
        user_id: str,
        resource_type: str,
        resource_id: str,
    ) -> bool:
        """Async twin of :meth:`has_platform_viewer_access`."""
        if not user_id or not resource_id:
            return False
        client = await self._get_async_client()
        resp = await client.rpc(
            "has_access_as",
            {
                "p_user": user_id,
                "p_type": resource_type,
                "p_id": resource_id,
                "p_required": "viewer",
            },
        ).execute()
        return bool(resp.data)

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
        # Inline the is_active + expires_at filter so callers don't have to
        # defensively re-check (closes the C3 leak where deactivated /
        # expired links continued to resolve).
        now_iso = datetime.now(UTC).isoformat()
        resp = (
            self._table(T_SHARE_LINKS)
            .select("*")
            .eq("share_token", share_token)
            .eq("is_active", True)
            .or_(f"expires_at.is.null,expires_at.gt.{now_iso}")
            .execute()
        )
        return self._first_or_none(resp)

    async def get_share_link_async(self, share_token: str) -> dict | None:
        now_iso = datetime.now(UTC).isoformat()
        t = await self._atable(T_SHARE_LINKS)
        resp = (
            await t.select("*")
            .eq("share_token", share_token)
            .eq("is_active", True)
            .or_(f"expires_at.is.null,expires_at.gt.{now_iso}")
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
        """Atomically increment use_count and auto-deactivate at max_uses.

        Delegates to the ``consume_share_link(TEXT)`` SQL function which
        does the read + check + update in a single row-locked statement.
        Replaces the previous non-atomic read-then-update pattern that
        could overshoot ``max_uses`` under concurrent access.
        """
        client = self._get_client()
        resp = client.rpc("consume_share_link", {"p_token": share_token}).execute()
        return resp.data if resp.data else None

    async def increment_share_link_use_async(self, share_token: str) -> dict | None:
        client = await self._get_async_client()
        resp = await client.rpc(
            "consume_share_link", {"p_token": share_token}
        ).execute()
        return resp.data if resp.data else None

    # NOTE: the user-group ACL feature (cld_user_groups / cld_user_group_members)
    # was removed in the 2026 DB canonicalization — those tables are
    # graveyarded and the group methods that used them are gone. File ACLs
    # are direct user/org grants on iam.permissions (see PERMISSIONS above).
