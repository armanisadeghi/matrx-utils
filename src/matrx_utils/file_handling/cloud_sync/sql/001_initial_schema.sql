-- ============================================================
-- Cloud File Sync — Initial Schema
-- ============================================================
--
-- Required by: matrx_utils.file_handling.cloud_sync
--
-- This migration creates all tables, indexes, triggers, and
-- Row Level Security policies needed for the managed cloud
-- file sync layer.  Run it once against your Postgres database
-- (Supabase SQL Editor, psql, or the migration runner).
--
-- Designed for Supabase but works with any Postgres >= 14 that
-- has the uuid-ossp extension available.
-- ============================================================

-- Enable UUID generation if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- 1. TABLES
-- ============================================================

-- Folder hierarchy (mirrors a virtual filesystem)
CREATE TABLE IF NOT EXISTS cloud_folders (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id        UUID NOT NULL,
    folder_path     TEXT NOT NULL,
    folder_name     TEXT NOT NULL,
    parent_id       UUID REFERENCES cloud_folders(id) ON DELETE CASCADE,
    visibility      TEXT NOT NULL DEFAULT 'private'
                        CHECK (visibility IN ('public', 'private', 'shared')),
    metadata        JSONB NOT NULL DEFAULT '{}',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at      TIMESTAMPTZ,

    UNIQUE (owner_id, folder_path)
);

-- Core file records
CREATE TABLE IF NOT EXISTS cloud_files (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id          UUID NOT NULL,
    file_path         TEXT NOT NULL,
    storage_uri       TEXT NOT NULL,
    file_name         TEXT NOT NULL,
    mime_type         TEXT,
    file_size         BIGINT,
    checksum          TEXT,
    visibility        TEXT NOT NULL DEFAULT 'private'
                          CHECK (visibility IN ('public', 'private', 'shared')),
    current_version   INT NOT NULL DEFAULT 1,
    parent_folder_id  UUID REFERENCES cloud_folders(id) ON DELETE SET NULL,
    metadata          JSONB NOT NULL DEFAULT '{}',
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at        TIMESTAMPTZ,

    UNIQUE (owner_id, file_path)
);

-- File version history
CREATE TABLE IF NOT EXISTS cloud_file_versions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_id         UUID NOT NULL REFERENCES cloud_files(id) ON DELETE CASCADE,
    version_number  INT NOT NULL,
    storage_uri     TEXT NOT NULL,
    file_size       BIGINT,
    checksum        TEXT,
    created_by      UUID,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    change_summary  TEXT,

    UNIQUE (file_id, version_number)
);

-- Access control entries (files and folders)
CREATE TABLE IF NOT EXISTS cloud_file_permissions (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id       UUID NOT NULL,
    resource_type     TEXT NOT NULL CHECK (resource_type IN ('file', 'folder')),
    grantee_id        UUID NOT NULL,
    grantee_type      TEXT NOT NULL DEFAULT 'user'
                          CHECK (grantee_type IN ('user', 'group')),
    permission_level  TEXT NOT NULL
                          CHECK (permission_level IN ('read', 'write', 'admin')),
    granted_by        UUID,
    granted_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at        TIMESTAMPTZ,

    UNIQUE (resource_id, resource_type, grantee_id, grantee_type)
);

-- Shareable links with optional expiry and use limits
CREATE TABLE IF NOT EXISTS cloud_share_links (
    id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id       UUID NOT NULL,
    resource_type     TEXT NOT NULL CHECK (resource_type IN ('file', 'folder')),
    share_token       TEXT UNIQUE NOT NULL DEFAULT uuid_generate_v4()::text,
    permission_level  TEXT NOT NULL DEFAULT 'read'
                          CHECK (permission_level IN ('read', 'write')),
    created_by        UUID,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at        TIMESTAMPTZ,
    max_uses          INT,
    use_count         INT NOT NULL DEFAULT 0,
    is_active         BOOLEAN NOT NULL DEFAULT true
);

-- User groups for group-based ACL
CREATE TABLE IF NOT EXISTS cloud_user_groups (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        TEXT NOT NULL,
    owner_id    UUID NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (owner_id, name)
);

-- Group membership
CREATE TABLE IF NOT EXISTS cloud_user_group_members (
    id        UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    group_id  UUID NOT NULL REFERENCES cloud_user_groups(id) ON DELETE CASCADE,
    user_id   UUID NOT NULL,
    role      TEXT NOT NULL DEFAULT 'member'
                  CHECK (role IN ('member', 'admin')),
    added_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    added_by  UUID,

    UNIQUE (group_id, user_id)
);


-- ============================================================
-- 2. INDEXES
-- ============================================================

-- Files
CREATE INDEX IF NOT EXISTS idx_cloud_files_owner
    ON cloud_files(owner_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_cloud_files_path
    ON cloud_files(owner_id, file_path) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_cloud_files_parent
    ON cloud_files(parent_folder_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_cloud_files_visibility
    ON cloud_files(visibility) WHERE deleted_at IS NULL;

-- Folders
CREATE INDEX IF NOT EXISTS idx_cloud_folders_owner
    ON cloud_folders(owner_id) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_cloud_folders_parent
    ON cloud_folders(parent_id) WHERE deleted_at IS NULL;

-- Versions
CREATE INDEX IF NOT EXISTS idx_cloud_versions_file
    ON cloud_file_versions(file_id);

-- Permissions
CREATE INDEX IF NOT EXISTS idx_cloud_perms_resource
    ON cloud_file_permissions(resource_id, resource_type);
CREATE INDEX IF NOT EXISTS idx_cloud_perms_grantee
    ON cloud_file_permissions(grantee_id, grantee_type);

-- Share links
CREATE INDEX IF NOT EXISTS idx_cloud_share_token
    ON cloud_share_links(share_token) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_cloud_share_resource
    ON cloud_share_links(resource_id, resource_type) WHERE is_active = true;

-- Groups
CREATE INDEX IF NOT EXISTS idx_cloud_group_members_user
    ON cloud_user_group_members(user_id);
CREATE INDEX IF NOT EXISTS idx_cloud_group_members_group
    ON cloud_user_group_members(group_id);


-- ============================================================
-- 3. UPDATED_AT TRIGGER
-- ============================================================

CREATE OR REPLACE FUNCTION cloud_sync_update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_cloud_files_updated_at
    BEFORE UPDATE ON cloud_files
    FOR EACH ROW EXECUTE FUNCTION cloud_sync_update_timestamp();

CREATE TRIGGER trg_cloud_folders_updated_at
    BEFORE UPDATE ON cloud_folders
    FOR EACH ROW EXECUTE FUNCTION cloud_sync_update_timestamp();


-- ============================================================
-- 4. ROW LEVEL SECURITY
-- ============================================================
-- These policies let client-side apps (React via Supabase JS)
-- see only files the authenticated user owns, has been granted
-- access to, or that are public.  The Python backend uses the
-- service-role key which bypasses RLS entirely.
-- ============================================================

ALTER TABLE cloud_files             ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_folders           ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_file_versions     ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_file_permissions  ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_share_links       ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_user_groups       ENABLE ROW LEVEL SECURITY;
ALTER TABLE cloud_user_group_members ENABLE ROW LEVEL SECURITY;

-- ----------------------------------------------------------
-- cloud_files
-- ----------------------------------------------------------

-- Owner full access
CREATE POLICY cloud_files_owner_select ON cloud_files
    FOR SELECT USING (owner_id = auth.uid() AND deleted_at IS NULL);

CREATE POLICY cloud_files_owner_insert ON cloud_files
    FOR INSERT WITH CHECK (owner_id = auth.uid());

CREATE POLICY cloud_files_owner_update ON cloud_files
    FOR UPDATE USING (owner_id = auth.uid() AND deleted_at IS NULL);

CREATE POLICY cloud_files_owner_delete ON cloud_files
    FOR DELETE USING (owner_id = auth.uid());

-- Public files visible to everyone
CREATE POLICY cloud_files_public_select ON cloud_files
    FOR SELECT USING (visibility = 'public' AND deleted_at IS NULL);

-- Direct user permission grants
CREATE POLICY cloud_files_shared_user_select ON cloud_files
    FOR SELECT USING (
        deleted_at IS NULL
        AND EXISTS (
            SELECT 1 FROM cloud_file_permissions
            WHERE resource_id = cloud_files.id
              AND resource_type = 'file'
              AND grantee_id = auth.uid()
              AND grantee_type = 'user'
              AND (expires_at IS NULL OR expires_at > now())
        )
    );

-- Group permission grants
CREATE POLICY cloud_files_shared_group_select ON cloud_files
    FOR SELECT USING (
        deleted_at IS NULL
        AND EXISTS (
            SELECT 1 FROM cloud_file_permissions p
            JOIN cloud_user_group_members gm
                ON p.grantee_id = gm.group_id
            WHERE p.resource_id = cloud_files.id
              AND p.resource_type = 'file'
              AND p.grantee_type = 'group'
              AND gm.user_id = auth.uid()
              AND (p.expires_at IS NULL OR p.expires_at > now())
        )
    );

-- Folder-inherited permission (files in shared folders)
CREATE POLICY cloud_files_folder_perm_select ON cloud_files
    FOR SELECT USING (
        deleted_at IS NULL
        AND parent_folder_id IS NOT NULL
        AND EXISTS (
            SELECT 1 FROM cloud_file_permissions
            WHERE resource_id = cloud_files.parent_folder_id
              AND resource_type = 'folder'
              AND grantee_id = auth.uid()
              AND grantee_type = 'user'
              AND (expires_at IS NULL OR expires_at > now())
        )
    );

-- Write permission (users with write or admin on the file)
CREATE POLICY cloud_files_shared_user_update ON cloud_files
    FOR UPDATE USING (
        deleted_at IS NULL
        AND EXISTS (
            SELECT 1 FROM cloud_file_permissions
            WHERE resource_id = cloud_files.id
              AND resource_type = 'file'
              AND grantee_id = auth.uid()
              AND grantee_type = 'user'
              AND permission_level IN ('write', 'admin')
              AND (expires_at IS NULL OR expires_at > now())
        )
    );

-- ----------------------------------------------------------
-- cloud_folders
-- ----------------------------------------------------------

CREATE POLICY cloud_folders_owner_select ON cloud_folders
    FOR SELECT USING (owner_id = auth.uid() AND deleted_at IS NULL);

CREATE POLICY cloud_folders_owner_insert ON cloud_folders
    FOR INSERT WITH CHECK (owner_id = auth.uid());

CREATE POLICY cloud_folders_owner_update ON cloud_folders
    FOR UPDATE USING (owner_id = auth.uid() AND deleted_at IS NULL);

CREATE POLICY cloud_folders_owner_delete ON cloud_folders
    FOR DELETE USING (owner_id = auth.uid());

CREATE POLICY cloud_folders_public_select ON cloud_folders
    FOR SELECT USING (visibility = 'public' AND deleted_at IS NULL);

CREATE POLICY cloud_folders_shared_user_select ON cloud_folders
    FOR SELECT USING (
        deleted_at IS NULL
        AND EXISTS (
            SELECT 1 FROM cloud_file_permissions
            WHERE resource_id = cloud_folders.id
              AND resource_type = 'folder'
              AND grantee_id = auth.uid()
              AND grantee_type = 'user'
              AND (expires_at IS NULL OR expires_at > now())
        )
    );

CREATE POLICY cloud_folders_shared_group_select ON cloud_folders
    FOR SELECT USING (
        deleted_at IS NULL
        AND EXISTS (
            SELECT 1 FROM cloud_file_permissions p
            JOIN cloud_user_group_members gm
                ON p.grantee_id = gm.group_id
            WHERE p.resource_id = cloud_folders.id
              AND p.resource_type = 'folder'
              AND p.grantee_type = 'group'
              AND gm.user_id = auth.uid()
              AND (p.expires_at IS NULL OR p.expires_at > now())
        )
    );

-- ----------------------------------------------------------
-- cloud_file_versions  (access follows parent file)
-- ----------------------------------------------------------

CREATE POLICY cloud_versions_via_file ON cloud_file_versions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM cloud_files
            WHERE cloud_files.id = cloud_file_versions.file_id
            -- relies on cloud_files RLS to filter
        )
    );

CREATE POLICY cloud_versions_owner_insert ON cloud_file_versions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM cloud_files
            WHERE cloud_files.id = cloud_file_versions.file_id
              AND cloud_files.owner_id = auth.uid()
        )
    );

-- ----------------------------------------------------------
-- cloud_file_permissions  (owner + admin can manage)
-- ----------------------------------------------------------

CREATE POLICY cloud_perms_owner_select ON cloud_file_permissions
    FOR SELECT USING (
        -- file owner
        EXISTS (
            SELECT 1 FROM cloud_files
            WHERE cloud_files.id = cloud_file_permissions.resource_id
              AND cloud_file_permissions.resource_type = 'file'
              AND cloud_files.owner_id = auth.uid()
        )
        OR
        -- folder owner
        EXISTS (
            SELECT 1 FROM cloud_folders
            WHERE cloud_folders.id = cloud_file_permissions.resource_id
              AND cloud_file_permissions.resource_type = 'folder'
              AND cloud_folders.owner_id = auth.uid()
        )
        OR
        -- grantee can see their own grants
        (grantee_id = auth.uid() AND grantee_type = 'user')
    );

CREATE POLICY cloud_perms_owner_insert ON cloud_file_permissions
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM cloud_files
            WHERE cloud_files.id = cloud_file_permissions.resource_id
              AND cloud_file_permissions.resource_type = 'file'
              AND cloud_files.owner_id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM cloud_folders
            WHERE cloud_folders.id = cloud_file_permissions.resource_id
              AND cloud_file_permissions.resource_type = 'folder'
              AND cloud_folders.owner_id = auth.uid()
        )
    );

CREATE POLICY cloud_perms_owner_delete ON cloud_file_permissions
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM cloud_files
            WHERE cloud_files.id = cloud_file_permissions.resource_id
              AND cloud_file_permissions.resource_type = 'file'
              AND cloud_files.owner_id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM cloud_folders
            WHERE cloud_folders.id = cloud_file_permissions.resource_id
              AND cloud_file_permissions.resource_type = 'folder'
              AND cloud_folders.owner_id = auth.uid()
        )
    );

-- ----------------------------------------------------------
-- cloud_share_links  (owner can manage)
-- ----------------------------------------------------------

CREATE POLICY cloud_shares_owner_all ON cloud_share_links
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM cloud_files
            WHERE cloud_files.id = cloud_share_links.resource_id
              AND cloud_share_links.resource_type = 'file'
              AND cloud_files.owner_id = auth.uid()
        )
        OR EXISTS (
            SELECT 1 FROM cloud_folders
            WHERE cloud_folders.id = cloud_share_links.resource_id
              AND cloud_share_links.resource_type = 'folder'
              AND cloud_folders.owner_id = auth.uid()
        )
    );

-- ----------------------------------------------------------
-- cloud_user_groups
-- ----------------------------------------------------------

CREATE POLICY cloud_groups_owner_all ON cloud_user_groups
    FOR ALL USING (owner_id = auth.uid());

CREATE POLICY cloud_groups_member_select ON cloud_user_groups
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM cloud_user_group_members
            WHERE group_id = cloud_user_groups.id
              AND user_id = auth.uid()
        )
    );

-- ----------------------------------------------------------
-- cloud_user_group_members
-- ----------------------------------------------------------

CREATE POLICY cloud_group_members_owner_all ON cloud_user_group_members
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM cloud_user_groups
            WHERE cloud_user_groups.id = cloud_user_group_members.group_id
              AND cloud_user_groups.owner_id = auth.uid()
        )
    );

CREATE POLICY cloud_group_members_self_select ON cloud_user_group_members
    FOR SELECT USING (user_id = auth.uid());


-- ============================================================
-- 5. HELPER FUNCTIONS (callable from client via supabase.rpc)
-- ============================================================

-- Resolve the effective permission level for a user on a file.
-- Returns 'admin', 'write', 'read', or NULL (no access).
CREATE OR REPLACE FUNCTION cloud_get_effective_permission(
    p_file_id UUID,
    p_user_id UUID
) RETURNS TEXT AS $$
DECLARE
    v_owner_id UUID;
    v_visibility TEXT;
    v_level TEXT;
BEGIN
    -- Check ownership
    SELECT owner_id, visibility INTO v_owner_id, v_visibility
    FROM cloud_files WHERE id = p_file_id AND deleted_at IS NULL;

    IF NOT FOUND THEN RETURN NULL; END IF;
    IF v_owner_id = p_user_id THEN RETURN 'admin'; END IF;
    IF v_visibility = 'public' THEN RETURN 'read'; END IF;

    -- Direct user permission (pick highest)
    SELECT permission_level INTO v_level
    FROM cloud_file_permissions
    WHERE resource_id = p_file_id
      AND resource_type = 'file'
      AND grantee_id = p_user_id
      AND grantee_type = 'user'
      AND (expires_at IS NULL OR expires_at > now())
    ORDER BY
        CASE permission_level
            WHEN 'admin' THEN 1
            WHEN 'write' THEN 2
            WHEN 'read'  THEN 3
        END
    LIMIT 1;

    IF v_level IS NOT NULL THEN RETURN v_level; END IF;

    -- Group permission (pick highest across all groups)
    SELECT p.permission_level INTO v_level
    FROM cloud_file_permissions p
    JOIN cloud_user_group_members gm ON p.grantee_id = gm.group_id
    WHERE p.resource_id = p_file_id
      AND p.resource_type = 'file'
      AND p.grantee_type = 'group'
      AND gm.user_id = p_user_id
      AND (p.expires_at IS NULL OR p.expires_at > now())
    ORDER BY
        CASE p.permission_level
            WHEN 'admin' THEN 1
            WHEN 'write' THEN 2
            WHEN 'read'  THEN 3
        END
    LIMIT 1;

    IF v_level IS NOT NULL THEN RETURN v_level; END IF;

    -- Folder-inherited permission
    SELECT p.permission_level INTO v_level
    FROM cloud_files f
    JOIN cloud_file_permissions p
        ON p.resource_id = f.parent_folder_id AND p.resource_type = 'folder'
    WHERE f.id = p_file_id
      AND f.parent_folder_id IS NOT NULL
      AND (
          (p.grantee_id = p_user_id AND p.grantee_type = 'user')
          OR (p.grantee_type = 'group' AND EXISTS (
              SELECT 1 FROM cloud_user_group_members gm
              WHERE gm.group_id = p.grantee_id AND gm.user_id = p_user_id
          ))
      )
      AND (p.expires_at IS NULL OR p.expires_at > now())
    ORDER BY
        CASE p.permission_level
            WHEN 'admin' THEN 1
            WHEN 'write' THEN 2
            WHEN 'read'  THEN 3
        END
    LIMIT 1;

    RETURN v_level;  -- NULL if no access
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- Build the full file tree visible to a user (owned + shared + public).
-- Returns as JSON array for efficient client consumption.
CREATE OR REPLACE FUNCTION cloud_get_user_file_tree(p_user_id UUID)
RETURNS JSONB AS $$
    SELECT COALESCE(jsonb_agg(row_to_json(t)::jsonb), '[]'::jsonb)
    FROM (
        SELECT
            f.id,
            f.owner_id,
            f.file_path,
            f.file_name,
            f.mime_type,
            f.file_size,
            f.visibility,
            f.current_version,
            f.parent_folder_id,
            f.metadata,
            f.created_at,
            f.updated_at,
            CASE
                WHEN f.owner_id = p_user_id THEN 'admin'
                ELSE cloud_get_effective_permission(f.id, p_user_id)
            END AS effective_permission
        FROM cloud_files f
        WHERE f.deleted_at IS NULL
          AND (
              f.owner_id = p_user_id
              OR f.visibility = 'public'
              OR cloud_get_effective_permission(f.id, p_user_id) IS NOT NULL
          )
        ORDER BY f.file_path
    ) t;
$$ LANGUAGE sql STABLE SECURITY DEFINER;
