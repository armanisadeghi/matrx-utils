"""Cloud file sync — managed cloud storage with permissions and versioning.

This subpackage adds a fully managed file synchronization layer on top of
the existing file_handling system.  It uses:

- **Postgres** (via Supabase PostgREST) for file metadata, ownership,
  permissions, sharing, and version history.
- **AWS S3** (or Supabase Storage) for the actual file bytes.

When ``CloudSyncConfig`` is passed to ``FileManager``, all file operations
automatically sync to the cloud and record metadata in the database.

Quick start::

    from matrx_utils import FileManager
    from matrx_utils.file_handling.cloud_sync import CloudSyncConfig

    fm = FileManager("my_app", cloud_sync=CloudSyncConfig(
        user_id="current-user-uuid",
        s3_bucket="my-files-bucket",
    ))

    # Auto-sync: local write + cloud upload + DB tracking
    fm.write_json("base", "reports/q1.json", {"revenue": 1_000_000})

    # Managed write: full control over permissions and versioning
    result = fm.managed_write("reports/q1.json", data, visibility="private",
                              share_with=["other-user-uuid"])

    # Managed read with permission check
    data = await fm.managed_read_async("reports/q1.json")

    # Version history
    versions = fm.sync_engine.versions.list_versions(result.file_id)

    # Restore a previous version
    fm.sync_engine.versions.restore_version(result.file_id, version_number=1)

Database setup::

    from matrx_utils.file_handling.cloud_sync import get_migration_sql

    # Get the SQL to run in Supabase SQL Editor or psql
    sql = get_migration_sql()

    # Or run programmatically (requires psycopg2)
    from matrx_utils.file_handling.cloud_sync import run_migrations
    run_migrations("postgresql://user:pass@host:5432/db")
"""

from .config import CloudSyncConfig
from .db import DatabaseClient
from .migrations import (
    get_all_migration_files,
    get_migration_sql,
    is_schema_applied,
    print_migration_sql,
    run_migrations,
)
from .models import (
    CloudFile,
    CloudFilePermission,
    CloudFileVersion,
    CloudFolder,
    CloudGroupMember,
    CloudShareLink,
    CloudUserGroup,
    FileTreeEntry,
    PermissionInfo,
    SyncResult,
)
from .permissions import PermissionsManager, configure_access_checker
from .sync_engine import SyncEngine
from .variants import (
    VariantEncoder,
    get_variant_encoder,
    has_variant_encoder,
    register_variant_encoder,
    render_variant_async,
    variant_file_path,
)
from .versioning import VersionManager

__all__ = [
    # Config
    "CloudSyncConfig",
    # Models
    "CloudFile",
    "CloudFilePermission",
    "CloudFileVersion",
    "CloudFolder",
    "CloudGroupMember",
    "CloudShareLink",
    "CloudUserGroup",
    "FileTreeEntry",
    "PermissionInfo",
    "SyncResult",
    # Core
    "DatabaseClient",
    "PermissionsManager",
    "configure_access_checker",
    "VersionManager",
    "SyncEngine",
    # Migrations
    "get_migration_sql",
    "get_all_migration_files",
    "run_migrations",
    "is_schema_applied",
    "print_migration_sql",
    # Variants
    "VariantEncoder",
    "register_variant_encoder",
    "get_variant_encoder",
    "has_variant_encoder",
    "render_variant_async",
    "variant_file_path",
]
