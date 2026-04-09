"""Pydantic models for the cloud file sync layer.

These models represent the database entities (cloud_files, cloud_folders,
cloud_file_versions, etc.) and the results returned by sync operations.
They are used for validation, serialization, and as typed return values
throughout the cloud_sync package.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


def _uuid() -> str:
    return str(uuid.uuid4())


# ------------------------------------------------------------------
# Core entities
# ------------------------------------------------------------------

class CloudFile(BaseModel):
    """A tracked file in the cloud sync system."""
    id: str = Field(default_factory=_uuid)
    owner_id: str
    file_path: str
    storage_uri: str
    file_name: str
    mime_type: str | None = None
    file_size: int | None = None
    checksum: str | None = None
    visibility: Literal["public", "private", "shared"] = "private"
    current_version: int = 1
    parent_folder_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class CloudFolder(BaseModel):
    """A virtual folder in the cloud sync file tree."""
    id: str = Field(default_factory=_uuid)
    owner_id: str
    folder_path: str
    folder_name: str
    parent_id: str | None = None
    visibility: Literal["public", "private", "shared"] = "private"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None


class CloudFileVersion(BaseModel):
    """A single version of a tracked file."""
    id: str = Field(default_factory=_uuid)
    file_id: str
    version_number: int
    storage_uri: str
    file_size: int | None = None
    checksum: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    change_summary: str | None = None


class CloudFilePermission(BaseModel):
    """An ACL entry granting access to a file or folder."""
    id: str = Field(default_factory=_uuid)
    resource_id: str
    resource_type: Literal["file", "folder"]
    grantee_id: str
    grantee_type: Literal["user", "group"] = "user"
    permission_level: Literal["read", "write", "admin"]
    granted_by: str | None = None
    granted_at: datetime | None = None
    expires_at: datetime | None = None


class CloudShareLink(BaseModel):
    """A shareable link to a file or folder."""
    id: str = Field(default_factory=_uuid)
    resource_id: str
    resource_type: Literal["file", "folder"]
    share_token: str = Field(default_factory=_uuid)
    permission_level: Literal["read", "write"] = "read"
    created_by: str | None = None
    created_at: datetime | None = None
    expires_at: datetime | None = None
    max_uses: int | None = None
    use_count: int = 0
    is_active: bool = True


class CloudUserGroup(BaseModel):
    """A named group of users for group-based ACL."""
    id: str = Field(default_factory=_uuid)
    name: str
    owner_id: str
    created_at: datetime | None = None


class CloudGroupMember(BaseModel):
    """Membership record linking a user to a group."""
    id: str = Field(default_factory=_uuid)
    group_id: str
    user_id: str
    role: Literal["member", "admin"] = "member"
    added_at: datetime | None = None
    added_by: str | None = None


# ------------------------------------------------------------------
# Operation results
# ------------------------------------------------------------------

class SyncResult(BaseModel):
    """Returned from managed write/update operations."""
    file_id: str
    storage_uri: str
    version_number: int
    file_size: int | None = None
    checksum: str | None = None
    is_new: bool = False
    url: str | None = None


class FileTreeEntry(BaseModel):
    """A single entry in the user's file tree (returned by list operations)."""
    id: str
    owner_id: str
    file_path: str
    file_name: str
    mime_type: str | None = None
    file_size: int | None = None
    visibility: str
    current_version: int
    parent_folder_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None
    effective_permission: str | None = None


class PermissionInfo(BaseModel):
    """Summary of a permission grant (for listing permissions on a resource)."""
    id: str
    grantee_id: str
    grantee_type: str
    permission_level: str
    granted_by: str | None = None
    granted_at: datetime | None = None
    expires_at: datetime | None = None
