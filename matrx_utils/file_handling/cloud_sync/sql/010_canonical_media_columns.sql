-- =============================================================================
-- 010 — Canonical media columns: size_bytes rename + image/video/audio shape.
-- =============================================================================
--
-- Part of the UnifiedMediaBlock contract rollout. Three changes:
--
--   1. Rename ``file_size`` → ``size_bytes`` on cld_files AND cld_file_versions.
--      ``size_bytes`` is unambiguous (no chance of confusion with the file
--      object as a whole) and aligns the wire shape with the FE's
--      UnifiedImageBlock contract. Done now, before legacy callers
--      accumulate.
--
--   2. Promote ``width`` and ``height`` from metadata JSONB to first-class
--      INT columns. Currently surfaced ad-hoc from metadata.image.dimensions
--      — promoting them lets us index, filter, and aggregate (e.g. "show
--      me all 16:9 images") and makes them a typed first-class field on
--      every UnifiedMediaBlock projection.
--
--   3. Add ``duration_ms`` INT column for audio/video. Same reasoning —
--      queryable + typed, no longer buried inside metadata.media.duration.
--
-- All statements idempotent (DO $$ guards / IF EXISTS / IF NOT EXISTS).
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Rename cld_files.file_size → cld_files.size_bytes.
-- ---------------------------------------------------------------------------
-- Postgres ``ALTER TABLE ... RENAME COLUMN ... TO ...`` is NOT idempotent
-- (errors when the source column doesn't exist or the target already does).
-- Guard with a DO block so the migration is replay-safe.

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cld_files'
          AND column_name = 'file_size'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cld_files'
          AND column_name = 'size_bytes'
    ) THEN
        ALTER TABLE public.cld_files RENAME COLUMN file_size TO size_bytes;
    END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- 2. Rename cld_file_versions.file_size → cld_file_versions.size_bytes
--    (mirror for consistency — one canonical name across the whole subsystem).
-- ---------------------------------------------------------------------------

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cld_file_versions'
          AND column_name = 'file_size'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'cld_file_versions'
          AND column_name = 'size_bytes'
    ) THEN
        ALTER TABLE public.cld_file_versions RENAME COLUMN file_size TO size_bytes;
    END IF;
END
$$;

-- ---------------------------------------------------------------------------
-- 3. Promote width / height to first-class columns on cld_files.
-- ---------------------------------------------------------------------------
-- For images: pixel width/height of the master file.
-- For video : pixel dimensions of the source frame.
-- NULL for non-visual files (audio, documents without dimensions, generic
-- attachments) — UnifiedMediaBlock surfaces them as Optional accordingly.

ALTER TABLE public.cld_files
    ADD COLUMN IF NOT EXISTS width  INT NULL,
    ADD COLUMN IF NOT EXISTS height INT NULL;

COMMENT ON COLUMN public.cld_files.width IS
'Pixel width for image/video masters. NULL when not applicable
(non-visual files) or not yet probed.';

COMMENT ON COLUMN public.cld_files.height IS
'Pixel height for image/video masters. NULL when not applicable
(non-visual files) or not yet probed.';

-- ---------------------------------------------------------------------------
-- 4. Add duration_ms for audio/video on cld_files.
-- ---------------------------------------------------------------------------
-- Milliseconds (INT — max ~24 days; we will never store anything close).
-- NULL for non-temporal media.

ALTER TABLE public.cld_files
    ADD COLUMN IF NOT EXISTS duration_ms INT NULL;

COMMENT ON COLUMN public.cld_files.duration_ms IS
'Playback duration in milliseconds for audio/video masters. NULL when
not applicable or not yet probed.';

-- ---------------------------------------------------------------------------
-- 5. Update SQL function bodies that referenced the old ``file_size`` column.
-- ---------------------------------------------------------------------------
-- PostgreSQL's ``RENAME COLUMN`` does NOT propagate into function bodies
-- stored in pg_proc — they keep their textual reference to the old name
-- and start failing at call time. CREATE OR REPLACE the three affected
-- functions from migration 003 with ``size_bytes`` in place of
-- ``file_size``. Bodies are otherwise verbatim copies of the 003 originals.

-- 5a. cld_get_user_file_tree — file tree projection used by GET /files.
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

-- 5b. cld_list_trash — soft-deleted file listing.
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

-- 5c. cld_search_files — filename / metadata search.
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

COMMIT;
