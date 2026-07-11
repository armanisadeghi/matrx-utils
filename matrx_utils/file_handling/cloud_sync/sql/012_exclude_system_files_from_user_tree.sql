-- =============================================================================
-- 012 — Exclude system-files/* + variant rows from user-facing file queries.
-- =============================================================================
--
-- Variants (the rows written by VariantsService under
-- ``system-files/variants/<master_id>/<key>.<ext>``) live in the same
-- ``cld_files`` table as user-uploaded masters. The user-tree /
-- search / trash RPCs from migration 003 + 010 didn't filter them out,
-- so a user's ``/files`` page showed every variant alongside their real
-- uploads — for one large account, ~6,000 variants alongside ~5,000
-- real files (63.8% noise).
--
-- Fix: every user-facing read RPC excludes rows that are derived from
-- another file. Two complementary filters:
--
--   1. ``f.parent_file_id IS NULL`` — the canonical lineage check.
--      Phase 1d.3 added a forward-write path that stamps this column
--      on every new variant. Pre-existing variants get backfilled via
--      migration 013 (separately).
--
--   2. ``f.file_path NOT LIKE 'system-files/%'`` — path-based defense.
--      Catches any row that lives in the system-files namespace
--      regardless of how it got there.
--
-- Both checks together — defense in depth.
--
-- This migration also fixes the same gap on:
--   - ``cld_search_files`` (003)
--   - ``cld_list_trash`` (003, updated in 010)
--
-- Idempotent: CREATE OR REPLACE.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. cld_get_user_file_tree — user's primary file listing.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_get_user_file_tree(
    p_user_id UUID,
    p_limit INT DEFAULT 200,
    p_offset INT DEFAULT 0,
    p_include_folders BOOLEAN DEFAULT TRUE,
    p_include_deleted BOOLEAN DEFAULT FALSE
) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden: p_user_id does not match auth.uid()'
            USING ERRCODE = '42501';
    END IF;

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
            f.size_bytes,
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
          -- Phase 1d.3 — exclude derived rows (variants etc.) from user view.
          AND f.parent_file_id IS NULL
          AND f.file_path NOT LIKE 'system-files/%'
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
        ORDER BY 5
        LIMIT p_limit OFFSET p_offset
    ) t;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ---------------------------------------------------------------------------
-- 2. cld_search_files — filename / metadata search.
-- ---------------------------------------------------------------------------
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
            SELECT id, file_path, file_name, mime_type, size_bytes, visibility,
                   current_version, parent_folder_id, created_at, updated_at
              FROM cld_files
             WHERE owner_id = p_user_id
               AND deleted_at IS NULL
               -- Phase 1d.3 — exclude derived rows from search results.
               AND parent_file_id IS NULL
               AND file_path NOT LIKE 'system-files/%'
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

-- ---------------------------------------------------------------------------
-- 3. cld_list_trash — soft-deleted file listing.
-- ---------------------------------------------------------------------------
-- Variants the user never explicitly "deleted" shouldn't show in trash
-- either — they're maintained alongside their masters via cascade rules
-- (or wherever the master goes). Same exclusion as the live tree.
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
                    SELECT id, file_path, file_name, size_bytes, deleted_at
                      FROM cld_files
                     WHERE owner_id = p_user_id AND deleted_at IS NOT NULL
                       -- Phase 1d.3 — exclude derived rows from trash view.
                       AND parent_file_id IS NULL
                       AND file_path NOT LIKE 'system-files/%'
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

COMMIT;
