"""Supabase Storage backend.

Auto-configures from environment variables (or a matrx_utils settings object).

Key priority (first non-empty value wins):
    SUPABASE_SECRET_KEY       — new format (sb_secret_...), elevated/backend
    SUPABASE_SERVICE_ROLE_KEY — legacy JWT format, elevated/backend
    SUPABASE_PUBLISHABLE_KEY  — new format (sb_publishable_...), low-privilege
    SUPABASE_ANON_KEY         — legacy JWT format, low-privilege

Only SUPABASE_URL plus at least one key are required.

Bucket is always supplied at call time — it is part of the path:
    "bucket-name/path/to/object.ext"

There is intentionally no default bucket. Each Supabase project typically has
many buckets; callers are expected to be explicit about which one they target.

The secret / service_role key is strongly preferred for backend usage because
it bypasses Row Level Security policies, giving full read/write access.

storage3 API notes (as of storage3 >=0.7):
    list_buckets()      → list[SyncBucket]  — Pydantic model, use .name / .id
    list()              → list[dict[str, Any]]  — plain dicts
    create_signed_url() → SignedUrlResponse (TypedDict: signedURL, signedUrl)
    get_public_url()    → str directly
    remove()            → list[dict[str, Any]]
    copy() / move()     → dict[str, str]
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .base_backend import StorageBackend

if TYPE_CHECKING:
    from supabase import Client, AsyncClient
    from storage3._sync.file_api import SyncBucket
    from storage3._sync.file_api import SyncBucketActionsMixin
    from storage3._async.file_api import AsyncBucketActionsMixin


class SupabaseBackend(StorageBackend):
    def __init__(self) -> None:
        self._client: Client | None = None
        self._async_client: AsyncClient | None = None
        self._url: str = ""
        self._key: str = ""
        self._configured: bool = False
        self._init_from_settings()

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    def _init_from_settings(self) -> None:
        try:
            from matrx_utils.conf import settings

            url: str = self._safe_get(settings, "SUPABASE_URL")
            if not url:
                return

            # New format takes priority; legacy JWT keys are the fallback.
            key: str = (
                self._safe_get(settings, "SUPABASE_SECRET_KEY")
                or self._safe_get(settings, "SUPABASE_SERVICE_ROLE_KEY")
                or self._safe_get(settings, "SUPABASE_PUBLISHABLE_KEY")
                or self._safe_get(settings, "SUPABASE_ANON_KEY")
            )
            if not key:
                return

            self._url = url
            self._key = key
            self._configured = True
        except Exception:
            return

    @staticmethod
    def _safe_get(settings_obj: object, name: str) -> str:
        try:
            val: object = getattr(settings_obj, name, None)
            return val if isinstance(val, str) and val.strip() else ""
        except Exception:
            return ""

    def _get_client(self) -> Client:
        if self._client is None:
            from supabase import create_client
            self._client = create_client(self._url, self._key)
        return self._client  # type: ignore[return-value]

    async def _get_async_client(self) -> AsyncClient:
        if self._async_client is None:
            from supabase import acreate_client
            self._async_client = await acreate_client(self._url, self._key)
        return self._async_client  # type: ignore[return-value]

    def _get_storage(self):
        return self._get_client().storage

    async def _get_async_storage(self):
        client = await self._get_async_client()
        return client.storage

    def _bucket(self, bucket_name: str) -> SyncBucketActionsMixin:
        return self._get_storage().from_(bucket_name)  # type: ignore[return-value]

    async def _async_bucket(self, bucket_name: str) -> AsyncBucketActionsMixin:
        storage = await self._get_async_storage()
        return storage.from_(bucket_name)  # type: ignore[return-value]

    def is_configured(self) -> bool:
        return self._configured

    # ------------------------------------------------------------------
    # Path helpers
    # ------------------------------------------------------------------

    def _parse_path(self, path: str) -> tuple[str, str]:
        """Split 'bucket/path/to/file' → ('bucket', 'path/to/file').

        Bucket is always required — there is no default.
        Use the URI form:  supabase://bucket-name/path/to/file
        """
        if "/" not in path:
            raise ValueError(
                f"Supabase path '{path}' must include a bucket: 'bucket/path/to/file'. "
                "Use the URI form supabase://bucket-name/path/to/file."
            )
        bucket, _, file_path = path.partition("/")
        if not file_path:
            raise ValueError(
                f"Supabase path '{path}' has no file component after the bucket."
            )
        return bucket, file_path

    # ------------------------------------------------------------------
    # Core CRUD
    # ------------------------------------------------------------------

    def read(self, path: str) -> bytes:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        data: bytes = self._bucket(bucket).download(file_path)
        return data

    def write(self, path: str, content: bytes | str, upsert: bool = True) -> bool:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        raw: bytes = content.encode() if isinstance(content, str) else content
        if upsert:
            self._bucket(bucket).upload(file_path, raw, file_options={"upsert": "true"})
        else:
            self._bucket(bucket).upload(file_path, raw)
        return True

    def append(self, path: str, content: bytes | str) -> bool:
        self._require_configured()
        try:
            existing: bytes = self.read(path)
        except Exception:
            existing = b""
        raw: bytes = content.encode() if isinstance(content, str) else content
        return self.write(path, existing + raw, upsert=True)

    def delete(self, path: str) -> bool:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        self._bucket(bucket).remove([file_path])
        return True

    # ------------------------------------------------------------------
    # URL generation
    # ------------------------------------------------------------------

    def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Return a signed URL. Falls back to public URL if signing fails."""
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        try:
            # create_signed_url returns SignedUrlResponse TypedDict
            # with keys "signedURL" and "signedUrl" (both set to the same value)
            response = self._bucket(bucket).create_signed_url(file_path, expires_in)
            signed: str = response["signedURL"]
            if signed:
                return signed
        except Exception:
            pass
        return self.get_public_url(path)

    def get_public_url(self, path: str) -> str:
        """Return the permanent public URL (bucket must be set to Public)."""
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        url: str = self._bucket(bucket).get_public_url(file_path)
        return url

    # ------------------------------------------------------------------
    # Listing
    # ------------------------------------------------------------------

    def list_files(self, prefix: str = "") -> list[str]:
        """List files under *prefix*, which must include the bucket.

        prefix format: "bucket-name/optional/sub/path"
        """
        self._require_configured()

        if "/" not in prefix:
            raise ValueError(
                f"Supabase list_files() prefix '{prefix}' must include the bucket: "
                "'bucket-name/optional/path'. "
                "Use the URI form supabase://bucket-name/optional/path"
            )
        bucket, _, path_prefix = prefix.partition("/")

        # list() returns list[dict[str, Any]] — plain dicts
        items: list[dict[str, Any]] = self._bucket(bucket).list(path_prefix)
        results: list[str] = []
        for item in items:
            name: str = item.get("name", "")
            if name:
                full_path: str = f"{path_prefix}/{name}".lstrip("/")
                results.append(f"{bucket}/{full_path}")
        return results

    # ------------------------------------------------------------------
    # Bucket management helpers (convenience, not in ABC)
    # ------------------------------------------------------------------

    def list_buckets(self) -> list[str]:
        """Return the names of all buckets accessible with the current key."""
        self._require_configured()
        # list_buckets() returns list[SyncBucket] — Pydantic models, use .name
        buckets: list[SyncBucket] = self._get_storage().list_buckets()
        return [b.name for b in buckets if b.name]

    def create_bucket(self, bucket_name: str, public: bool = False) -> bool:
        self._require_configured()
        self._get_storage().create_bucket(bucket_name, options={"public": public})
        return True

    def move(self, src_path: str, dst_path: str) -> bool:
        """Move/rename within the same bucket."""
        self._require_configured()
        src_bucket, src_file = self._parse_path(src_path)
        dst_bucket, dst_file = self._parse_path(dst_path)
        if src_bucket != dst_bucket:
            raise ValueError(
                "Supabase Storage move() requires source and destination to be in the "
                f"same bucket. Got '{src_bucket}' and '{dst_bucket}'."
            )
        self._bucket(src_bucket).move(src_file, dst_file)
        return True

    def copy(self, src_path: str, dst_path: str) -> bool:
        """Server-side copy within the same bucket."""
        self._require_configured()
        src_bucket, src_file = self._parse_path(src_path)
        dst_bucket, dst_file = self._parse_path(dst_path)
        if src_bucket != dst_bucket:
            raise ValueError(
                "Supabase Storage copy() requires source and destination to be in the "
                f"same bucket. Got '{src_bucket}' and '{dst_bucket}'."
            )
        self._bucket(src_bucket).copy(src_file, dst_file)
        return True

    def get_metadata(self, path: str) -> dict[str, Any]:
        """Return the storage3 metadata dict for the object at *path*."""
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        folder: str = file_path.rsplit("/", 1)[0] if "/" in file_path else ""
        filename: str = file_path.rsplit("/", 1)[-1]
        items: list[dict[str, Any]] = self._bucket(bucket).list(folder)
        for item in items:
            if item.get("name") == filename:
                return item
        return {}

    # ------------------------------------------------------------------
    # Asynchronous API — native AsyncClient (no thread pool needed)
    # ------------------------------------------------------------------

    async def read_async(self, path: str) -> bytes:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        bucket_api = await self._async_bucket(bucket)
        data: bytes = await bucket_api.download(file_path)
        return data

    async def write_async(self, path: str, content: bytes | str, upsert: bool = True) -> bool:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        raw: bytes = content.encode() if isinstance(content, str) else content
        bucket_api = await self._async_bucket(bucket)
        if upsert:
            await bucket_api.upload(file_path, raw, file_options={"upsert": "true"})
        else:
            await bucket_api.upload(file_path, raw)
        return True

    async def append_async(self, path: str, content: bytes | str) -> bool:
        self._require_configured()
        try:
            existing: bytes = await self.read_async(path)
        except Exception:
            existing = b""
        raw: bytes = content.encode() if isinstance(content, str) else content
        return await self.write_async(path, existing + raw, upsert=True)

    async def delete_async(self, path: str) -> bool:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        bucket_api = await self._async_bucket(bucket)
        await bucket_api.remove([file_path])
        return True

    async def get_url_async(self, path: str, expires_in: int = 3600) -> str:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        bucket_api = await self._async_bucket(bucket)
        try:
            response = await bucket_api.create_signed_url(file_path, expires_in)
            signed: str = response["signedURL"]
            if signed:
                return signed
        except Exception:
            pass
        return await self.get_public_url_async(path)

    async def get_public_url_async(self, path: str) -> str:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        bucket_api = await self._async_bucket(bucket)
        url: str = await bucket_api.get_public_url(file_path)
        return url

    async def list_files_async(self, prefix: str = "") -> list[str]:
        self._require_configured()
        if "/" not in prefix:
            raise ValueError(
                f"Supabase list_files_async() prefix '{prefix}' must include the bucket."
            )
        bucket, _, path_prefix = prefix.partition("/")
        bucket_api = await self._async_bucket(bucket)
        items: list[dict[str, Any]] = await bucket_api.list(path_prefix)
        results: list[str] = []
        for item in items:
            name: str = item.get("name", "")
            if name:
                full_path: str = f"{path_prefix}/{name}".lstrip("/")
                results.append(f"{bucket}/{full_path}")
        return results

    async def copy_async(self, src_path: str, dst_path: str) -> bool:
        self._require_configured()
        src_bucket, src_file = self._parse_path(src_path)
        dst_bucket, dst_file = self._parse_path(dst_path)
        if src_bucket != dst_bucket:
            raise ValueError(
                "Supabase copy_async() requires source and destination in the same bucket."
            )
        bucket_api = await self._async_bucket(src_bucket)
        await bucket_api.copy(src_file, dst_file)
        return True

    async def get_metadata_async(self, path: str) -> dict[str, Any]:
        self._require_configured()
        bucket, file_path = self._parse_path(path)
        folder: str = file_path.rsplit("/", 1)[0] if "/" in file_path else ""
        filename: str = file_path.rsplit("/", 1)[-1]
        bucket_api = await self._async_bucket(bucket)
        items: list[dict[str, Any]] = await bucket_api.list(folder)
        for item in items:
            if item.get("name") == filename:
                return item
        return {}
