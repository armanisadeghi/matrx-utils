"""Configuration for the cloud file sync layer.

CloudSyncConfig holds all settings needed to connect the sync engine
to a Postgres database (via Supabase) and an S3 bucket.  Pass it to
FileManager to enable automatic cloud synchronization:

    from matrx_utils import FileManager
    from matrx_utils.file_handling.cloud_sync import CloudSyncConfig

    fm = FileManager("my_app", cloud_sync=CloudSyncConfig(
        user_id="current-user-uuid",
        s3_bucket="my-files-bucket",
    ))

When no explicit URLs/keys are provided, the config falls back to the
values already present in ``matrx_utils.conf.settings`` (which reads
from environment variables or a configured settings object).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CloudSyncConfig:
    """Immutable configuration for the cloud sync layer.

    Parameters
    ----------
    user_id:
        UUID of the currently authenticated user.  Required for all
        permission checks and file ownership.  In web apps (FastAPI),
        set this per-request via ``sync_engine.set_user(user_id)``.
    s3_bucket:
        Default S3 bucket name for file storage.  Files are stored at
        ``s3://{s3_bucket}/{user_id}/{file_path}``.
    storage_backend:
        Which cloud backend to use for file bytes.
        ``"s3"`` (default) or ``"supabase"``.
    supabase_url:
        Supabase project URL.  Falls back to ``settings.SUPABASE_URL``.
    supabase_key:
        Supabase service-role key (bypasses RLS for backend operations).
        Falls back to ``settings.SUPABASE_SECRET_KEY``.
    auto_sync:
        When True (default), all FileManager write/delete operations
        automatically sync to cloud + database.  Pass ``cloud_sync=False``
        per-call to override.
    version_storage_prefix:
        Prefix within the bucket for storing previous file versions.
        Defaults to ``.versions``.
    database_url:
        Direct Postgres connection string for the migration runner.
        Not used at runtime (runtime uses Supabase PostgREST).
    """

    # Required
    user_id: str = ""
    s3_bucket: str = ""

    # Backend selection
    storage_backend: str = "s3"

    # Supabase connection (falls back to settings/env)
    supabase_url: str = ""
    supabase_key: str = ""

    # Behaviour
    auto_sync: bool = True
    version_storage_prefix: str = ".versions"

    # Direct Postgres (migration runner only)
    database_url: str = ""

    def resolve_supabase_url(self) -> str:
        """Return the Supabase URL, falling back to settings/env."""
        if self.supabase_url:
            return self.supabase_url
        from matrx_utils.conf import settings
        return _safe_get(settings, "SUPABASE_URL", "SUPABASE_MATRIX_URL")

    def resolve_supabase_key(self) -> str:
        """Return the Supabase service-role key, falling back to settings/env."""
        if self.supabase_key:
            return self.supabase_key
        from matrx_utils.conf import settings
        return _safe_get(
            settings,
            "SUPABASE_SECRET_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "SUPABASE_MATRIX_KEY",
        )

    def resolve_s3_bucket(self) -> str:
        """Return the S3 bucket name, falling back to settings/env."""
        if self.s3_bucket:
            return self.s3_bucket
        from matrx_utils.conf import settings
        return _safe_get(settings, "AWS_S3_DEFAULT_BUCKET")

    def is_configured(self) -> bool:
        """Return True if the minimum settings are present for cloud sync."""
        try:
            url = self.resolve_supabase_url()
            key = self.resolve_supabase_key()
            bucket = self.resolve_s3_bucket()
            return bool(url and key and bucket)
        except Exception:
            return False


def _safe_get(settings_obj: object, *names: str) -> str:
    """Try each attribute name in order, return the first non-empty value."""
    for name in names:
        try:
            value = getattr(settings_obj, name, None)
            if value:
                return str(value)
        except Exception:
            continue
    return ""
