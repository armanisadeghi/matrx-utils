-- ============================================================
-- Cloud Files — Security, Correctness, Quotas, Tiers, Audit
-- (migration 003) — fixes every Critical and most High issues
-- from docs/cloud_files_quality_assessment.md
--
-- Idempotent / safe to re-run.
-- ============================================================

-- ------------------------------------------------------------
-- 1. RPC LOCKDOWN  (fixes C1: SECURITY DEFINER RPC disclosure)
-- ------------------------------------------------------------
-- Every SECURITY DEFINER function below now refuses to run for
-- a UUID that doesn't match auth.uid() — except when the
-- service-role calls it (auth.uid() returns NULL for service-role).

REVOKE EXECUTE ON FUNCTION cld_get_user_file_tree(UUID) FROM PUBLIC, anon, authenticated;
REVOKE EXECUTE ON FUNCTION cld_get_effective_permission(UUID, UUID) FROM PUBLIC, anon, authenticated;

-- Grant back ONLY to authenticated users with caller-identity check enforced inside.
GRANT EXECUTE ON FUNCTION cld_get_user_file_tree(UUID) TO authenticated, service_role;
GRANT EXECUTE ON FUNCTION cld_get_effective_permission(UUID, UUID) TO authenticated, service_role;

-- The original cld_get_effective_permission used parameter name p_file_id;
-- Postgres refuses CREATE OR REPLACE when arg names change, so drop first.
DROP FUNCTION IF EXISTS cld_get_effective_permission(UUID, UUID) CASCADE;

-- Re-create the tree RPC with caller-identity guard + folders included +
-- pagination + N+1 fix (single recursive CTE instead of per-row sub-RPC).
CREATE OR REPLACE FUNCTION cld_get_user_file_tree(
    p_user_id UUID,
    p_limit INT DEFAULT 5000,
    p_offset INT DEFAULT 0,
    p_include_folders BOOLEAN DEFAULT true,
    p_include_deleted BOOLEAN DEFAULT false
)
RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    -- Caller-identity check: anyone calling via the anon/authenticated key
    -- must pass their own user_id. Service-role bypasses (auth.uid() is NULL).
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden: p_user_id does not match auth.uid()'
            USING ERRCODE = '42501';
    END IF;

    -- Clamp limit to a sane max even if the caller asks for more.
    p_limit := LEAST(GREATEST(p_limit, 1), 5000);

    SELECT COALESCE(jsonb_agg(row_to_json(t)::jsonb), '[]'::jsonb)
    INTO v_result
    FROM (
        SELECT
            'file'::text      AS kind,
            f.id,
            f.owner_id,
            f.file_path       AS path,
            f.file_name       AS name,
            f.parent_folder_id AS parent_id,
            f.mime_type,
            f.file_size       AS size_bytes,
            f.visibility,
            f.current_version,
            f.metadata,
            f.created_at,
            f.updated_at,
            f.deleted_at,
            CASE
                WHEN f.owner_id = p_user_id THEN 'admin'
                ELSE cld_get_effective_permission(f.id, p_user_id)
            END AS effective_permission
        FROM cld_files f
        WHERE (p_include_deleted OR f.deleted_at IS NULL)
          AND (
              f.owner_id = p_user_id
              OR f.visibility = 'public'
              OR cld_get_effective_permission(f.id, p_user_id) IS NOT NULL
          )

        UNION ALL

        SELECT
            'folder'::text    AS kind,
            d.id,
            d.owner_id,
            d.folder_path     AS path,
            d.folder_name     AS name,
            d.parent_id,
            NULL::text        AS mime_type,
            NULL::bigint      AS size_bytes,
            d.visibility,
            NULL::int         AS current_version,
            d.metadata,
            d.created_at,
            d.updated_at,
            d.deleted_at,
            CASE
                WHEN d.owner_id = p_user_id THEN 'admin'
                ELSE NULL
            END AS effective_permission
        FROM cld_folders d
        WHERE p_include_folders
          AND (p_include_deleted OR d.deleted_at IS NULL)
          AND d.owner_id = p_user_id
        ORDER BY 5  -- name
        LIMIT p_limit OFFSET p_offset
    ) t;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

COMMENT ON FUNCTION cld_get_user_file_tree(UUID, INT, INT, BOOLEAN, BOOLEAN) IS
'Return the user''s file tree with optional folder inclusion + pagination.
Refuses to run when the caller (auth.uid()) is not p_user_id.
Service-role callers (auth.uid() = NULL) skip the check, so the backend
can still call it with arbitrary user_ids when serving guests.';

-- Re-grant after function signature change.
REVOKE EXECUTE ON FUNCTION cld_get_user_file_tree(UUID, INT, INT, BOOLEAN, BOOLEAN) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION cld_get_user_file_tree(UUID, INT, INT, BOOLEAN, BOOLEAN) TO authenticated, service_role;

-- Same caller-identity guard on cld_get_effective_permission.
CREATE OR REPLACE FUNCTION cld_get_effective_permission(
    p_resource_id UUID,
    p_user_id UUID
) RETURNS TEXT AS $$
DECLARE
    v_owner_id UUID;
    v_level    TEXT;
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden: p_user_id does not match auth.uid()'
            USING ERRCODE = '42501';
    END IF;

    SELECT owner_id INTO v_owner_id FROM cld_files WHERE id = p_resource_id AND deleted_at IS NULL;
    IF v_owner_id IS NULL THEN
        SELECT owner_id INTO v_owner_id FROM cld_folders WHERE id = p_resource_id AND deleted_at IS NULL;
    END IF;

    IF v_owner_id = p_user_id THEN
        RETURN 'admin';
    END IF;

    -- Direct grant
    SELECT permission_level
      INTO v_level
      FROM cld_file_permissions
     WHERE resource_id = p_resource_id
       AND grantee_id = p_user_id
       AND grantee_type = 'user'
       AND (expires_at IS NULL OR expires_at > now())
     ORDER BY CASE permission_level WHEN 'admin' THEN 3 WHEN 'write' THEN 2 WHEN 'read' THEN 1 END DESC
     LIMIT 1;

    IF v_level IS NOT NULL THEN
        RETURN v_level;
    END IF;

    -- Group grant
    SELECT p.permission_level
      INTO v_level
      FROM cld_file_permissions p
      JOIN cld_user_group_members gm ON gm.group_id = p.grantee_id
     WHERE p.resource_id = p_resource_id
       AND p.grantee_type = 'group'
       AND gm.user_id = p_user_id
       AND (p.expires_at IS NULL OR p.expires_at > now())
     ORDER BY CASE p.permission_level WHEN 'admin' THEN 3 WHEN 'write' THEN 2 WHEN 'read' THEN 1 END DESC
     LIMIT 1;

    IF v_level IS NOT NULL THEN
        RETURN v_level;
    END IF;

    -- Inherited from parent folder (recursive). Walk up the parent chain.
    -- Files: walk parent_folder_id -> folder.parent_id -> ...
    -- Folders: walk parent_id -> ...
    WITH RECURSIVE chain AS (
        -- Seed with the file's parent folder (if resource is a file)
        SELECT f.parent_folder_id AS folder_id
          FROM cld_files f
         WHERE f.id = p_resource_id AND f.parent_folder_id IS NOT NULL
        UNION ALL
        -- Or seed with the folder itself (if resource is a folder)
        SELECT d.id
          FROM cld_folders d
         WHERE d.id = p_resource_id
        UNION ALL
        -- Walk up via parent_id
        SELECT d.parent_id
          FROM cld_folders d
          JOIN chain c ON c.folder_id = d.id
         WHERE d.parent_id IS NOT NULL
    )
    SELECT p.permission_level
      INTO v_level
      FROM chain c
      JOIN cld_file_permissions p ON p.resource_id = c.folder_id AND p.resource_type = 'folder'
     WHERE (
              (p.grantee_id = p_user_id AND p.grantee_type = 'user')
           OR EXISTS (
               SELECT 1 FROM cld_user_group_members gm
                WHERE gm.group_id = p.grantee_id AND gm.user_id = p_user_id
           )
       )
       AND (p.expires_at IS NULL OR p.expires_at > now())
     ORDER BY CASE p.permission_level WHEN 'admin' THEN 3 WHEN 'write' THEN 2 WHEN 'read' THEN 1 END DESC
     LIMIT 1;

    RETURN v_level;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

REVOKE EXECUTE ON FUNCTION cld_get_effective_permission(UUID, UUID) FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION cld_get_effective_permission(UUID, UUID) TO authenticated, service_role;

-- Lock down cld_migrate_guest_to_user — service-role only.
REVOKE EXECUTE ON FUNCTION cld_migrate_guest_to_user(UUID, UUID) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION cld_migrate_guest_to_user(UUID, UUID) TO service_role;


-- ------------------------------------------------------------
-- 2. RLS FIX FOR cld_file_versions  (fixes H4: no-op policy)
-- ------------------------------------------------------------
DROP POLICY IF EXISTS cld_versions_via_file ON cld_file_versions;
CREATE POLICY cld_versions_via_file ON cld_file_versions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM cld_files f
             WHERE f.id = cld_file_versions.file_id
               AND f.deleted_at IS NULL
               AND (
                     f.owner_id = auth.uid()
                  OR f.visibility = 'public'
                  OR cld_get_effective_permission(f.id, auth.uid()) IS NOT NULL
               )
        )
    );


-- ------------------------------------------------------------
-- 3. ATOMIC OPS  (fixes H1 version race + M1 share-link race)
-- ------------------------------------------------------------

-- Atomic version bump. Returns the new version_number to use for the
-- write that produced this call. Uses row-level lock on cld_files.
CREATE OR REPLACE FUNCTION cld_bump_version(p_file_id UUID)
RETURNS INT AS $$
DECLARE
    v_new INT;
BEGIN
    UPDATE cld_files
       SET current_version = current_version + 1,
           updated_at = now()
     WHERE id = p_file_id
       AND deleted_at IS NULL
    RETURNING current_version INTO v_new;
    IF v_new IS NULL THEN
        RAISE EXCEPTION 'cld_bump_version: file % not found or deleted', p_file_id
            USING ERRCODE = 'no_data_found';
    END IF;
    RETURN v_new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_bump_version(UUID) TO service_role;

-- Atomic share-link increment. Returns the link row if it was actually
-- consumed (within max_uses, not expired, still active), else NULL.
CREATE OR REPLACE FUNCTION cld_consume_share_link(p_token TEXT)
RETURNS JSONB AS $$
DECLARE
    v_link cld_share_links%ROWTYPE;
BEGIN
    UPDATE cld_share_links
       SET use_count = use_count + 1,
           is_active = CASE
               WHEN max_uses IS NOT NULL AND (use_count + 1) >= max_uses THEN false
               ELSE is_active
           END
     WHERE share_token = p_token
       AND is_active = true
       AND (expires_at IS NULL OR expires_at > now())
       AND (max_uses IS NULL OR use_count < max_uses)
    RETURNING * INTO v_link;
    IF v_link.id IS NULL THEN
        RETURN NULL;
    END IF;
    RETURN row_to_json(v_link)::jsonb;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_consume_share_link(TEXT) TO service_role;


-- ------------------------------------------------------------
-- 4. CASCADE-AWARE SOFT DELETE  (fixes H6 + cascade-deactivate share links from C3)
-- ------------------------------------------------------------

-- Soft-delete a folder + every descendant folder + every file inside the
-- subtree, and deactivate every share link pointing at any of those rows.
CREATE OR REPLACE FUNCTION cld_soft_delete_folder(p_folder_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_owner UUID;
    v_folders INT;
    v_files INT;
    v_links INT;
BEGIN
    SELECT owner_id INTO v_owner FROM cld_folders WHERE id = p_folder_id AND deleted_at IS NULL;
    IF v_owner IS NULL THEN
        RETURN jsonb_build_object('folders', 0, 'files', 0, 'links', 0);
    END IF;

    -- Walk the descendant folder tree
    WITH RECURSIVE descendants AS (
        SELECT id FROM cld_folders WHERE id = p_folder_id
        UNION ALL
        SELECT d.id
          FROM cld_folders d
          JOIN descendants ds ON d.parent_id = ds.id
         WHERE d.deleted_at IS NULL
    ),
    deleted_folders AS (
        UPDATE cld_folders
           SET deleted_at = now()
         WHERE id IN (SELECT id FROM descendants)
           AND deleted_at IS NULL
        RETURNING id
    ),
    deleted_files AS (
        UPDATE cld_files
           SET deleted_at = now()
         WHERE parent_folder_id IN (SELECT id FROM deleted_folders)
           AND deleted_at IS NULL
        RETURNING id
    ),
    deactivated_links AS (
        UPDATE cld_share_links
           SET is_active = false
         WHERE (resource_type = 'folder' AND resource_id IN (SELECT id FROM deleted_folders))
            OR (resource_type = 'file'   AND resource_id IN (SELECT id FROM deleted_files))
        RETURNING id
    )
    SELECT
        (SELECT count(*) FROM deleted_folders),
        (SELECT count(*) FROM deleted_files),
        (SELECT count(*) FROM deactivated_links)
    INTO v_folders, v_files, v_links;

    RETURN jsonb_build_object('folders', v_folders, 'files', v_files, 'links', v_links);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_soft_delete_folder(UUID) TO service_role;

-- Soft-delete a file: set deleted_at + cascade-deactivate share links.
CREATE OR REPLACE FUNCTION cld_soft_delete_file(p_file_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    v_ok BOOLEAN := false;
BEGIN
    UPDATE cld_files SET deleted_at = now()
     WHERE id = p_file_id AND deleted_at IS NULL
    RETURNING true INTO v_ok;
    IF v_ok THEN
        UPDATE cld_share_links SET is_active = false
         WHERE resource_type = 'file' AND resource_id = p_file_id;
    END IF;
    RETURN COALESCE(v_ok, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_soft_delete_file(UUID) TO service_role;

-- Hard-delete a file: removes versions, permissions, share-links, the
-- file row itself. Storage-side cleanup is the caller's job (Python
-- enumerates `.versions/<file_id>/*` + main object and deletes from S3).
-- Returns the storage_uri's that were referenced so the caller can purge.
CREATE OR REPLACE FUNCTION cld_hard_delete_file(p_file_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_main_uri TEXT;
    v_version_uris TEXT[];
BEGIN
    SELECT storage_uri INTO v_main_uri FROM cld_files WHERE id = p_file_id;
    IF v_main_uri IS NULL THEN
        RETURN jsonb_build_object('main', NULL, 'versions', '[]'::jsonb);
    END IF;

    SELECT array_agg(storage_uri) INTO v_version_uris
      FROM cld_file_versions WHERE file_id = p_file_id;

    DELETE FROM cld_share_links     WHERE resource_type = 'file' AND resource_id = p_file_id;
    DELETE FROM cld_file_permissions WHERE resource_type = 'file' AND resource_id = p_file_id;
    DELETE FROM cld_file_versions    WHERE file_id = p_file_id;
    DELETE FROM cld_files            WHERE id = p_file_id;

    RETURN jsonb_build_object(
        'main', v_main_uri,
        'versions', COALESCE(to_jsonb(v_version_uris), '[]'::jsonb)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_hard_delete_file(UUID) TO service_role;

-- Restore from trash: undo soft-delete on a single file.
CREATE OR REPLACE FUNCTION cld_restore_file(p_file_id UUID)
RETURNS BOOLEAN AS $$
DECLARE v_ok BOOLEAN := false;
BEGIN
    UPDATE cld_files SET deleted_at = NULL
     WHERE id = p_file_id AND deleted_at IS NOT NULL
    RETURNING true INTO v_ok;
    RETURN COALESCE(v_ok, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_restore_file(UUID) TO service_role;

-- Restore from trash: undo soft-delete on a folder + every descendant.
CREATE OR REPLACE FUNCTION cld_restore_folder(p_folder_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_folders INT;
    v_files INT;
BEGIN
    WITH RECURSIVE descendants AS (
        SELECT id FROM cld_folders WHERE id = p_folder_id
        UNION ALL
        SELECT d.id FROM cld_folders d JOIN descendants ds ON d.parent_id = ds.id
    ),
    restored_folders AS (
        UPDATE cld_folders SET deleted_at = NULL
         WHERE id IN (SELECT id FROM descendants) AND deleted_at IS NOT NULL
        RETURNING id
    ),
    restored_files AS (
        UPDATE cld_files SET deleted_at = NULL
         WHERE parent_folder_id IN (SELECT id FROM restored_folders) AND deleted_at IS NOT NULL
        RETURNING id
    )
    SELECT (SELECT count(*) FROM restored_folders), (SELECT count(*) FROM restored_files)
    INTO v_folders, v_files;
    RETURN jsonb_build_object('folders', v_folders, 'files', v_files);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_restore_folder(UUID) TO service_role;


-- ------------------------------------------------------------
-- 5. FOLDER RENAME / MOVE — cascade child paths  (fixes H7)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_rename_folder(
    p_folder_id UUID,
    p_new_path TEXT,
    p_new_parent_id UUID DEFAULT NULL
) RETURNS JSONB AS $$
DECLARE
    v_owner UUID;
    v_old_path TEXT;
    v_new_name TEXT;
    v_descendants_files INT;
    v_descendants_folders INT;
BEGIN
    SELECT owner_id, folder_path INTO v_owner, v_old_path
      FROM cld_folders WHERE id = p_folder_id AND deleted_at IS NULL;
    IF v_owner IS NULL THEN
        RAISE EXCEPTION 'folder % not found', p_folder_id USING ERRCODE = 'no_data_found';
    END IF;

    p_new_path := trim(both '/' from p_new_path);
    v_new_name := split_part(p_new_path, '/', GREATEST(array_length(string_to_array(p_new_path, '/'), 1), 1));

    UPDATE cld_folders
       SET folder_path = p_new_path,
           folder_name = v_new_name,
           parent_id   = COALESCE(p_new_parent_id, parent_id),
           updated_at  = now()
     WHERE id = p_folder_id;

    -- Re-prefix child folder paths
    UPDATE cld_folders
       SET folder_path = p_new_path || substring(folder_path FROM length(v_old_path) + 1),
           updated_at  = now()
     WHERE owner_id = v_owner
       AND folder_path LIKE v_old_path || '/%'
       AND deleted_at IS NULL
    RETURNING id INTO v_descendants_folders;
    GET DIAGNOSTICS v_descendants_folders = ROW_COUNT;

    -- Re-prefix child file paths
    UPDATE cld_files
       SET file_path  = p_new_path || substring(file_path FROM length(v_old_path) + 1),
           updated_at = now()
     WHERE owner_id = v_owner
       AND file_path LIKE v_old_path || '/%'
       AND deleted_at IS NULL;
    GET DIAGNOSTICS v_descendants_files = ROW_COUNT;

    RETURN jsonb_build_object(
        'old_path', v_old_path,
        'new_path', p_new_path,
        'descendant_folders', v_descendants_folders,
        'descendant_files', v_descendants_files
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_rename_folder(UUID, TEXT, UUID) TO service_role;


-- ------------------------------------------------------------
-- 6. ATOMIC FOLDER CHAIN ENSURE  (fixes M10 race)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_ensure_folder_chain(
    p_owner_id UUID,
    p_folder_path TEXT
) RETURNS UUID AS $$
DECLARE
    v_path TEXT;
    v_part TEXT;
    v_parent UUID := NULL;
    v_current_path TEXT := '';
    v_id UUID;
BEGIN
    v_path := trim(both '/' from p_folder_path);
    IF v_path = '' THEN
        RETURN NULL;
    END IF;
    FOR v_part IN SELECT unnest(string_to_array(v_path, '/'))
    LOOP
        v_current_path := CASE WHEN v_current_path = '' THEN v_part ELSE v_current_path || '/' || v_part END;
        INSERT INTO cld_folders (owner_id, folder_path, folder_name, parent_id)
        VALUES (p_owner_id, v_current_path, v_part, v_parent)
        ON CONFLICT (owner_id, folder_path) DO UPDATE SET updated_at = now()
        RETURNING id INTO v_id;
        v_parent := v_id;
    END LOOP;
    RETURN v_parent;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_ensure_folder_chain(UUID, TEXT) TO service_role;


-- ------------------------------------------------------------
-- 7. ACCOUNT TIERS + LIMITS + USAGE  (fixes C11 + M28 + user request)
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS cld_account_tiers (
    id                          TEXT PRIMARY KEY,
    name                        TEXT NOT NULL,
    is_default_for_users        BOOLEAN NOT NULL DEFAULT false,
    is_default_for_guests       BOOLEAN NOT NULL DEFAULT false,
    -- Storage caps (NULL = unlimited)
    max_storage_bytes           BIGINT,
    max_file_size_bytes         BIGINT,
    max_files                   INT,
    max_versions_per_file       INT,
    -- Daily caps (NULL = unlimited)
    max_daily_uploads           INT,
    max_daily_upload_bytes      BIGINT,
    -- Resource caps
    max_share_links_per_resource INT,
    max_bulk_items              INT,
    -- Rate limits (per minute)
    rate_limit_uploads_per_min  INT,
    rate_limit_downloads_per_min INT,
    rate_limit_general_per_min  INT,
    -- Feature flags
    features                    JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO cld_account_tiers
    (id, name, is_default_for_users, is_default_for_guests,
     max_storage_bytes, max_file_size_bytes, max_files, max_versions_per_file,
     max_daily_uploads, max_daily_upload_bytes,
     max_share_links_per_resource, max_bulk_items,
     rate_limit_uploads_per_min, rate_limit_downloads_per_min, rate_limit_general_per_min,
     features)
VALUES
    ('guest', 'Guest', false, true,
     200*1024*1024,      -- 200 MB total
     25*1024*1024,       -- 25 MB per file
     50, 3,
     20, 500*1024*1024,
     3, 50,
     10, 60, 120,
     '{"resumable_upload": false, "presigned_put": false, "audit_log": false}'::jsonb),
    ('free', 'Free', true, false,
     5::bigint*1024*1024*1024,         -- 5 GB
     100*1024*1024,                    -- 100 MB per file
     5000, 10,
     200, 5::bigint*1024*1024*1024,
     10, 200,
     60, 300, 600,
     '{"resumable_upload": false, "presigned_put": false}'::jsonb),
    ('pro', 'Pro', false, false,
     100::bigint*1024*1024*1024,       -- 100 GB
     5::bigint*1024*1024*1024,         -- 5 GB per file
     100000, 30,
     2000, 100::bigint*1024*1024*1024,
     50, 500,
     300, 2000, 3000,
     '{"resumable_upload": true, "presigned_put": true}'::jsonb),
    ('enterprise', 'Enterprise', false, false,
     NULL, NULL, NULL, 100,
     NULL, NULL,
     NULL, 5000,
     NULL, NULL, NULL,
     '{"resumable_upload": true, "presigned_put": true, "audit_log": true, "legal_hold": true}'::jsonb)
ON CONFLICT (id) DO NOTHING;

-- Per-user overrides (tier assignment + custom limits)
CREATE TABLE IF NOT EXISTS cld_user_account (
    user_id          UUID PRIMARY KEY,
    tier_id          TEXT NOT NULL REFERENCES cld_account_tiers(id),
    custom_limits    JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_blocked       BOOLEAN NOT NULL DEFAULT false,
    blocked_reason   TEXT,
    notes            TEXT,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Storage + daily-usage tracking (one row per user, autocreated on first write)
CREATE TABLE IF NOT EXISTS cld_user_storage_usage (
    user_id              UUID PRIMARY KEY,
    bytes_used           BIGINT NOT NULL DEFAULT 0,
    files_count          INT NOT NULL DEFAULT 0,
    daily_upload_count   INT NOT NULL DEFAULT 0,
    daily_upload_bytes   BIGINT NOT NULL DEFAULT 0,
    daily_reset_at       DATE NOT NULL DEFAULT CURRENT_DATE,
    updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Resolve effective limits for a user (tier defaults merged with custom_limits).
CREATE OR REPLACE FUNCTION cld_get_user_limits(p_user_id UUID, p_is_guest BOOLEAN DEFAULT false)
RETURNS JSONB AS $$
DECLARE
    v_tier_id TEXT;
    v_tier cld_account_tiers%ROWTYPE;
    v_custom JSONB := '{}'::jsonb;
    v_blocked BOOLEAN := false;
    v_block_reason TEXT;
BEGIN
    SELECT tier_id, custom_limits, is_blocked, blocked_reason
      INTO v_tier_id, v_custom, v_blocked, v_block_reason
      FROM cld_user_account WHERE user_id = p_user_id;

    IF v_tier_id IS NULL THEN
        IF p_is_guest THEN
            SELECT id INTO v_tier_id FROM cld_account_tiers WHERE is_default_for_guests = true LIMIT 1;
        ELSE
            SELECT id INTO v_tier_id FROM cld_account_tiers WHERE is_default_for_users = true LIMIT 1;
        END IF;
    END IF;

    SELECT * INTO v_tier FROM cld_account_tiers WHERE id = v_tier_id;
    IF v_tier.id IS NULL THEN
        v_tier.id := 'free';
    END IF;

    RETURN jsonb_build_object(
        'tier_id', v_tier.id,
        'tier_name', v_tier.name,
        'is_blocked', v_blocked,
        'blocked_reason', v_block_reason,
        'max_storage_bytes',          COALESCE((v_custom->>'max_storage_bytes')::bigint,          v_tier.max_storage_bytes),
        'max_file_size_bytes',        COALESCE((v_custom->>'max_file_size_bytes')::bigint,        v_tier.max_file_size_bytes),
        'max_files',                  COALESCE((v_custom->>'max_files')::int,                     v_tier.max_files),
        'max_versions_per_file',      COALESCE((v_custom->>'max_versions_per_file')::int,         v_tier.max_versions_per_file),
        'max_daily_uploads',          COALESCE((v_custom->>'max_daily_uploads')::int,             v_tier.max_daily_uploads),
        'max_daily_upload_bytes',     COALESCE((v_custom->>'max_daily_upload_bytes')::bigint,     v_tier.max_daily_upload_bytes),
        'max_share_links_per_resource', COALESCE((v_custom->>'max_share_links_per_resource')::int, v_tier.max_share_links_per_resource),
        'max_bulk_items',             COALESCE((v_custom->>'max_bulk_items')::int,                v_tier.max_bulk_items),
        'rate_limit_uploads_per_min',   COALESCE((v_custom->>'rate_limit_uploads_per_min')::int,   v_tier.rate_limit_uploads_per_min),
        'rate_limit_downloads_per_min', COALESCE((v_custom->>'rate_limit_downloads_per_min')::int, v_tier.rate_limit_downloads_per_min),
        'rate_limit_general_per_min',   COALESCE((v_custom->>'rate_limit_general_per_min')::int,   v_tier.rate_limit_general_per_min),
        'features',                   COALESCE(v_custom->'features', v_tier.features)
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_get_user_limits(UUID, BOOLEAN) TO service_role;

-- Pre-flight quota check for an upload. Returns (allowed, reason, remaining bytes).
CREATE OR REPLACE FUNCTION cld_check_upload_quota(
    p_user_id UUID,
    p_size_bytes BIGINT,
    p_is_guest BOOLEAN DEFAULT false
) RETURNS JSONB AS $$
DECLARE
    v_limits JSONB := cld_get_user_limits(p_user_id, p_is_guest);
    v_usage cld_user_storage_usage%ROWTYPE;
    v_max_file BIGINT;
    v_max_storage BIGINT;
    v_max_files INT;
    v_max_daily_uploads INT;
    v_max_daily_bytes BIGINT;
BEGIN
    IF (v_limits->>'is_blocked')::boolean THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'account_blocked',
            'detail', v_limits->>'blocked_reason');
    END IF;

    v_max_file        := (v_limits->>'max_file_size_bytes')::bigint;
    v_max_storage     := (v_limits->>'max_storage_bytes')::bigint;
    v_max_files       := (v_limits->>'max_files')::int;
    v_max_daily_uploads := (v_limits->>'max_daily_uploads')::int;
    v_max_daily_bytes := (v_limits->>'max_daily_upload_bytes')::bigint;

    IF v_max_file IS NOT NULL AND p_size_bytes > v_max_file THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'file_too_large',
            'limit', v_max_file, 'attempted', p_size_bytes);
    END IF;

    SELECT * INTO v_usage FROM cld_user_storage_usage WHERE user_id = p_user_id;
    IF v_usage.user_id IS NULL THEN
        RETURN jsonb_build_object('allowed', true, 'reason', 'first_upload', 'limits', v_limits);
    END IF;

    -- Reset daily counter if needed
    IF v_usage.daily_reset_at < CURRENT_DATE THEN
        v_usage.daily_upload_count := 0;
        v_usage.daily_upload_bytes := 0;
    END IF;

    IF v_max_storage IS NOT NULL AND v_usage.bytes_used + p_size_bytes > v_max_storage THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'storage_quota_exceeded',
            'limit', v_max_storage, 'used', v_usage.bytes_used, 'attempted', p_size_bytes);
    END IF;
    IF v_max_files IS NOT NULL AND v_usage.files_count + 1 > v_max_files THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'file_count_exceeded',
            'limit', v_max_files, 'used', v_usage.files_count);
    END IF;
    IF v_max_daily_uploads IS NOT NULL AND v_usage.daily_upload_count + 1 > v_max_daily_uploads THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'daily_uploads_exceeded',
            'limit', v_max_daily_uploads, 'used', v_usage.daily_upload_count);
    END IF;
    IF v_max_daily_bytes IS NOT NULL AND v_usage.daily_upload_bytes + p_size_bytes > v_max_daily_bytes THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'daily_bytes_exceeded',
            'limit', v_max_daily_bytes, 'used', v_usage.daily_upload_bytes);
    END IF;

    RETURN jsonb_build_object('allowed', true, 'limits', v_limits, 'usage', row_to_json(v_usage)::jsonb);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_check_upload_quota(UUID, BIGINT, BOOLEAN) TO service_role;

-- Apply usage delta (called after successful upload / version-replace / delete).
CREATE OR REPLACE FUNCTION cld_apply_usage_delta(
    p_user_id UUID,
    p_bytes_delta BIGINT,
    p_files_delta INT,
    p_record_upload BOOLEAN DEFAULT false,
    p_upload_bytes BIGINT DEFAULT 0
) RETURNS VOID AS $$
BEGIN
    INSERT INTO cld_user_storage_usage
        (user_id, bytes_used, files_count, daily_upload_count, daily_upload_bytes, daily_reset_at)
    VALUES
        (p_user_id, GREATEST(p_bytes_delta, 0), GREATEST(p_files_delta, 0),
         CASE WHEN p_record_upload THEN 1 ELSE 0 END,
         CASE WHEN p_record_upload THEN p_upload_bytes ELSE 0 END,
         CURRENT_DATE)
    ON CONFLICT (user_id) DO UPDATE
       SET bytes_used = GREATEST(cld_user_storage_usage.bytes_used + p_bytes_delta, 0),
           files_count = GREATEST(cld_user_storage_usage.files_count + p_files_delta, 0),
           daily_upload_count = CASE
               WHEN cld_user_storage_usage.daily_reset_at < CURRENT_DATE THEN
                   CASE WHEN p_record_upload THEN 1 ELSE 0 END
               ELSE cld_user_storage_usage.daily_upload_count + CASE WHEN p_record_upload THEN 1 ELSE 0 END
           END,
           daily_upload_bytes = CASE
               WHEN cld_user_storage_usage.daily_reset_at < CURRENT_DATE THEN
                   CASE WHEN p_record_upload THEN p_upload_bytes ELSE 0 END
               ELSE cld_user_storage_usage.daily_upload_bytes + CASE WHEN p_record_upload THEN p_upload_bytes ELSE 0 END
           END,
           daily_reset_at = CASE
               WHEN cld_user_storage_usage.daily_reset_at < CURRENT_DATE THEN CURRENT_DATE
               ELSE cld_user_storage_usage.daily_reset_at
           END,
           updated_at = now();
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_apply_usage_delta(UUID, BIGINT, INT, BOOLEAN, BIGINT) TO service_role;

-- Return the usage + tier limits for an arbitrary user. Used by /files/usage.
CREATE OR REPLACE FUNCTION cld_get_usage_status(p_user_id UUID, p_is_guest BOOLEAN DEFAULT false)
RETURNS JSONB AS $$
DECLARE
    v_limits JSONB := cld_get_user_limits(p_user_id, p_is_guest);
    v_usage cld_user_storage_usage%ROWTYPE;
BEGIN
    SELECT * INTO v_usage FROM cld_user_storage_usage WHERE user_id = p_user_id;
    RETURN jsonb_build_object(
        'limits', v_limits,
        'usage', COALESCE(row_to_json(v_usage)::jsonb,
            jsonb_build_object('bytes_used', 0, 'files_count', 0,
                'daily_upload_count', 0, 'daily_upload_bytes', 0))
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_get_usage_status(UUID, BOOLEAN) TO service_role;


-- ------------------------------------------------------------
-- 8. VERSION RETENTION  (fixes M8: unbounded versions)
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_prune_old_versions(p_file_id UUID, p_keep INT)
RETURNS JSONB AS $$
DECLARE
    v_pruned_uris TEXT[];
BEGIN
    IF p_keep IS NULL OR p_keep <= 0 THEN
        RETURN jsonb_build_object('pruned', 0, 'storage_uris', '[]'::jsonb);
    END IF;
    WITH ranked AS (
        SELECT id, storage_uri,
               row_number() OVER (PARTITION BY file_id ORDER BY version_number DESC) AS rn
          FROM cld_file_versions WHERE file_id = p_file_id
    ),
    deleted AS (
        DELETE FROM cld_file_versions
         WHERE id IN (SELECT id FROM ranked WHERE rn > p_keep)
        RETURNING storage_uri
    )
    SELECT array_agg(storage_uri) INTO v_pruned_uris FROM deleted;
    RETURN jsonb_build_object(
        'pruned', COALESCE(array_length(v_pruned_uris, 1), 0),
        'storage_uris', COALESCE(to_jsonb(v_pruned_uris), '[]'::jsonb)
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_prune_old_versions(UUID, INT) TO service_role;


-- ------------------------------------------------------------
-- 9. AUDIT EVENTS  (fixes M6 and lays foundation for webhooks)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cld_events (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_id        UUID,
    actor_type      TEXT NOT NULL CHECK (actor_type IN ('user', 'guest', 'system', 'service')),
    event_type      TEXT NOT NULL,                  -- e.g. 'file.uploaded', 'file.deleted', 'permission.granted'
    resource_type   TEXT,                            -- 'file' | 'folder' | 'share_link' | 'group'
    resource_id     UUID,
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb,
    request_id      TEXT,
    ip_address      INET
);
CREATE INDEX IF NOT EXISTS idx_cld_events_actor      ON cld_events (actor_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_cld_events_resource   ON cld_events (resource_type, resource_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS idx_cld_events_type_time  ON cld_events (event_type, occurred_at DESC);

ALTER TABLE cld_events ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS cld_events_self_select ON cld_events;
CREATE POLICY cld_events_self_select ON cld_events
    FOR SELECT USING (actor_id = auth.uid());


-- ------------------------------------------------------------
-- 10. GUEST MIGRATION IDEMPOTENCY  (fixes C4)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cld_guest_migrations (
    guest_id        UUID PRIMARY KEY,
    migrated_to     UUID NOT NULL,
    migrated_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    fingerprint_hash TEXT NOT NULL,
    payload         JSONB NOT NULL DEFAULT '{}'::jsonb
);

-- Wrap cld_migrate_guest_to_user with the idempotency table.
CREATE OR REPLACE FUNCTION cld_migrate_guest_to_user_safe(
    p_guest_id UUID,
    p_new_user_id UUID,
    p_fingerprint_hash TEXT
) RETURNS JSONB AS $$
DECLARE
    v_existing cld_guest_migrations%ROWTYPE;
    v_result JSONB;
BEGIN
    SELECT * INTO v_existing FROM cld_guest_migrations WHERE guest_id = p_guest_id;
    IF v_existing.guest_id IS NOT NULL THEN
        IF v_existing.migrated_to <> p_new_user_id THEN
            RAISE EXCEPTION 'guest % already migrated to a different user (locked)', p_guest_id
                USING ERRCODE = '23505';
        END IF;
        -- Idempotent re-call: return previous payload.
        RETURN v_existing.payload;
    END IF;

    v_result := cld_migrate_guest_to_user(p_guest_id, p_new_user_id);

    INSERT INTO cld_guest_migrations (guest_id, migrated_to, fingerprint_hash, payload)
    VALUES (p_guest_id, p_new_user_id, p_fingerprint_hash, v_result);

    RETURN v_result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
REVOKE EXECUTE ON FUNCTION cld_migrate_guest_to_user_safe(UUID, UUID, TEXT) FROM PUBLIC, anon, authenticated;
GRANT EXECUTE ON FUNCTION cld_migrate_guest_to_user_safe(UUID, UUID, TEXT) TO service_role;


-- ------------------------------------------------------------
-- 11. ORGANIZATION_ID HOOK  (multi-tenancy foundation)
-- ------------------------------------------------------------
ALTER TABLE cld_files   ADD COLUMN IF NOT EXISTS organization_id UUID;
ALTER TABLE cld_folders ADD COLUMN IF NOT EXISTS organization_id UUID;
CREATE INDEX IF NOT EXISTS idx_cld_files_org   ON cld_files (organization_id) WHERE organization_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cld_folders_org ON cld_folders (organization_id) WHERE organization_id IS NOT NULL;

COMMENT ON COLUMN cld_files.organization_id IS
'Optional org/team id for multi-tenant accounts. NULL = personal scope.
RLS / permission resolution can be extended to honour this without breaking personal-scoped queries.';


-- ------------------------------------------------------------
-- 12. SYSTEM-FOLDER PROTECTION  (auto-created standard folders)
-- ------------------------------------------------------------
ALTER TABLE cld_folders ADD COLUMN IF NOT EXISTS is_system BOOLEAN NOT NULL DEFAULT false;

CREATE OR REPLACE FUNCTION cld_protect_system_folders()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_system = true AND (TG_OP = 'DELETE' OR (TG_OP = 'UPDATE' AND NEW.deleted_at IS NOT NULL)) THEN
        RAISE EXCEPTION 'cannot delete system folder %', OLD.folder_path
            USING ERRCODE = 'restrict_violation';
    END IF;
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_cld_folders_protect_system ON cld_folders;
CREATE TRIGGER trg_cld_folders_protect_system
BEFORE DELETE OR UPDATE OF deleted_at ON cld_folders
FOR EACH ROW EXECUTE FUNCTION cld_protect_system_folders();


-- ------------------------------------------------------------
-- 13. RPC helpers for trash views
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_list_trash(
    p_user_id UUID,
    p_limit INT DEFAULT 200,
    p_offset INT DEFAULT 0
) RETURNS JSONB AS $$
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden' USING ERRCODE = '42501';
    END IF;
    p_limit := LEAST(GREATEST(p_limit, 1), 1000);
    RETURN COALESCE((
        SELECT jsonb_build_object(
            'files', COALESCE((
                SELECT jsonb_agg(row_to_json(f)::jsonb ORDER BY f.deleted_at DESC)
                  FROM (
                    SELECT id, file_path, file_name, file_size, deleted_at
                      FROM cld_files
                     WHERE owner_id = p_user_id AND deleted_at IS NOT NULL
                     ORDER BY deleted_at DESC LIMIT p_limit OFFSET p_offset
                  ) f
            ), '[]'::jsonb),
            'folders', COALESCE((
                SELECT jsonb_agg(row_to_json(d)::jsonb ORDER BY d.deleted_at DESC)
                  FROM (
                    SELECT id, folder_path, folder_name, deleted_at
                      FROM cld_folders
                     WHERE owner_id = p_user_id AND deleted_at IS NOT NULL AND NOT is_system
                     ORDER BY deleted_at DESC LIMIT p_limit OFFSET p_offset
                  ) d
            ), '[]'::jsonb)
        )
    ), jsonb_build_object('files', '[]'::jsonb, 'folders', '[]'::jsonb));
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_list_trash(UUID, INT, INT) TO authenticated, service_role;


-- ------------------------------------------------------------
-- 14. SEARCH (filename / metadata)
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_cld_files_owner_created  ON cld_files (owner_id, created_at DESC) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_cld_files_owner_name     ON cld_files (owner_id, lower(file_name));

CREATE OR REPLACE FUNCTION cld_search_files(
    p_user_id UUID,
    p_query TEXT,
    p_limit INT DEFAULT 50,
    p_offset INT DEFAULT 0,
    p_mime_prefix TEXT DEFAULT NULL
) RETURNS JSONB AS $$
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden' USING ERRCODE = '42501';
    END IF;
    p_limit := LEAST(GREATEST(p_limit, 1), 200);
    RETURN COALESCE((
        SELECT jsonb_agg(row_to_json(t)::jsonb)
        FROM (
            SELECT id, file_path, file_name, mime_type, file_size, visibility,
                   current_version, parent_folder_id, created_at, updated_at
              FROM cld_files
             WHERE owner_id = p_user_id
               AND deleted_at IS NULL
               AND (p_mime_prefix IS NULL OR mime_type LIKE p_mime_prefix || '%')
               AND (
                     lower(file_name) LIKE '%' || lower(p_query) || '%'
                  OR lower(file_path) LIKE '%' || lower(p_query) || '%'
               )
             ORDER BY updated_at DESC
             LIMIT p_limit OFFSET p_offset
        ) t
    ), '[]'::jsonb);
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_search_files(UUID, TEXT, INT, INT, TEXT) TO authenticated, service_role;


-- ------------------------------------------------------------
-- 15. RATE LIMIT BUCKET TABLE  (sliding-window-ish, minute-grain)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS cld_rate_limit_buckets (
    actor_id     UUID NOT NULL,
    bucket_kind  TEXT NOT NULL,          -- 'upload' | 'download' | 'general'
    minute_bucket TIMESTAMPTZ NOT NULL,  -- truncated to minute
    counter      INT NOT NULL DEFAULT 0,
    PRIMARY KEY (actor_id, bucket_kind, minute_bucket)
);
CREATE INDEX IF NOT EXISTS idx_cld_rate_limit_buckets_time
    ON cld_rate_limit_buckets (minute_bucket);

CREATE OR REPLACE FUNCTION cld_check_rate_limit(
    p_actor_id UUID,
    p_kind TEXT,
    p_limit INT
) RETURNS JSONB AS $$
DECLARE
    v_minute TIMESTAMPTZ := date_trunc('minute', now());
    v_count INT;
BEGIN
    IF p_limit IS NULL THEN
        RETURN jsonb_build_object('allowed', true, 'remaining', NULL);
    END IF;

    INSERT INTO cld_rate_limit_buckets (actor_id, bucket_kind, minute_bucket, counter)
    VALUES (p_actor_id, p_kind, v_minute, 1)
    ON CONFLICT (actor_id, bucket_kind, minute_bucket)
    DO UPDATE SET counter = cld_rate_limit_buckets.counter + 1
    RETURNING counter INTO v_count;

    IF v_count > p_limit THEN
        RETURN jsonb_build_object('allowed', false, 'reason', 'rate_limited',
            'limit', p_limit, 'count', v_count, 'window', 'minute');
    END IF;
    RETURN jsonb_build_object('allowed', true, 'remaining', p_limit - v_count, 'limit', p_limit);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
GRANT EXECUTE ON FUNCTION cld_check_rate_limit(UUID, TEXT, INT) TO service_role;
