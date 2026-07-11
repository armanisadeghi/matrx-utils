-- =============================================================================
-- 015 — System-namespace visibility: classify + hide ALL system-created content.
-- =============================================================================
--
-- Provenance rule (canonical): a user's "files" are ONLY what the user
-- physically uploaded or added by hand. Everything the system created lives
-- under one of the two system roots and must NEVER clutter the user's
-- workspace browser or the recents stream:
--
--   generations/   — content the system PRODUCED   (AI images/audio/video/docs)
--   system-files/  — content the system DERIVED/FETCHED (scraper captures,
--                    variants, thumbnails, OCR/page renders, analysis, …)
--
-- These two roots mirror matrx_utils.file_handling.system_paths._ALLOWED_ROOTS.
--
-- Prior state (migrations 012 + 014): only system-files/ *files* were excluded
-- from cld_get_user_file_tree. That left (a) every system-files/ FOLDER and
-- (b) all of generations/ (files AND folders) leaking into the user's tree —
-- the source of thousands of empty system folders + generated images cluttering
-- a real user's workspace.
--
-- This migration:
--   1. cld_is_system_path(text) — ONE SQL source of truth for "is this a
--      system-managed path", matching the Python registry roots.
--   2. Auto-stamp trigger so cld_folders.is_system is ALWAYS correct on insert
--      and rename. No folder-create path can produce an unflagged system
--      folder (this is the structural chokepoint — SyncEngine._ensure_folder,
--      the router _ensure_folder_chain, the SQL cld_ensure_folder_chain, and
--      the tus/presigned transports all funnel through a cld_folders write).
--   3. Backfill is_system on existing rows so the flag matches the path.
--   4. cld_get_user_file_tree — exclude BOTH system roots from BOTH the file
--      leg and the folder leg. Body is otherwise identical to migration 014.
--
-- Idempotent. Reversible: DROP the trigger + function, and restore the
-- migration-014 body of cld_get_user_file_tree.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Canonical system-path predicate (matches SystemPathRegistry._ALLOWED_ROOTS)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_is_system_path(p_path TEXT)
RETURNS BOOLEAN
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT p_path IS NOT NULL
       AND split_part(ltrim(p_path, '/'), '/', 1) IN ('system-files', 'generations');
$$;

COMMENT ON FUNCTION cld_is_system_path(TEXT) IS
'True iff the logical path is under a system-managed root (system-files/ or
generations/). Single SQL source of truth for system-vs-user provenance;
mirrors matrx_utils.file_handling.system_paths._ALLOWED_ROOTS. Used by the
is_system auto-stamp trigger and cld_get_user_file_tree.';

-- ---------------------------------------------------------------------------
-- 2. Auto-stamp is_system on every folder write (the structural chokepoint).
--    BEFORE INSERT OR UPDATE OF folder_path → a fresh insert can never land
--    unflagged, and a relocate (folder_path change) re-derives the flag.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_folders_set_is_system()
RETURNS TRIGGER AS $$
BEGIN
    NEW.is_system := cld_is_system_path(NEW.folder_path);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_cld_folders_set_is_system ON cld_folders;
CREATE TRIGGER trg_cld_folders_set_is_system
BEFORE INSERT OR UPDATE OF folder_path ON cld_folders
FOR EACH ROW EXECUTE FUNCTION cld_folders_set_is_system();

-- ---------------------------------------------------------------------------
-- 3. Backfill: make the flag match the path on every existing row.
-- ---------------------------------------------------------------------------
UPDATE cld_folders
   SET is_system = cld_is_system_path(folder_path)
 WHERE is_system IS DISTINCT FROM cld_is_system_path(folder_path);

-- ---------------------------------------------------------------------------
-- 4. Rebuild cld_get_user_file_tree so BOTH legs hide BOTH system roots.
--    Identical to migration 014 except:
--      - file leg:   `f.file_path NOT LIKE 'system-files/%'`
--                  → `NOT cld_is_system_path(f.file_path)`
--      - folder leg: + `AND NOT cld_is_system_path(d.folder_path)`
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_get_user_file_tree(
    p_user_id        UUID,
    p_limit          INTEGER DEFAULT 5000,
    p_offset         INTEGER DEFAULT 0,
    p_include_folders BOOLEAN DEFAULT true,
    p_include_deleted BOOLEAN DEFAULT false,
    p_order_by       TEXT DEFAULT 'name'
) RETURNS JSONB
LANGUAGE plpgsql
STABLE SECURITY DEFINER
AS $function$
DECLARE
    v_result JSONB;
    v_order  TEXT;
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden: p_user_id does not match auth.uid()'
            USING ERRCODE = '42501';
    END IF;

    p_limit := LEAST(GREATEST(p_limit, 1), 5000);

    v_order := CASE lower(coalesce(p_order_by, 'name'))
        WHEN 'updated_at_desc' THEN '13 DESC NULLS LAST'
        WHEN 'created_at_desc' THEN '12 DESC NULLS LAST'
        WHEN 'name'            THEN '5'
        ELSE '5'
    END;

    EXECUTE format($q$
        SELECT COALESCE(jsonb_agg(row_to_json(t)::jsonb), '[]'::jsonb)
        FROM (
            SELECT
                'file'::text      AS kind,
                f.id, f.owner_id,
                f.file_path       AS path,
                f.file_name       AS name,
                f.parent_folder_id AS parent_id,
                f.mime_type, f.size_bytes, f.visibility, f.current_version,
                f.metadata, f.created_at, f.updated_at, f.deleted_at,
                CASE WHEN f.owner_id = %L THEN 'admin'
                     ELSE cld_get_effective_permission(f.id, %L) END AS effective_permission
            FROM cld_files f
            WHERE (%L OR f.deleted_at IS NULL)
              AND f.parent_file_id IS NULL
              AND NOT cld_is_system_path(f.file_path)
              AND (
                  f.owner_id = %L
                  OR cld_get_effective_permission(f.id, %L) IS NOT NULL
              )
            UNION ALL
            SELECT
                'folder'::text    AS kind,
                d.id, d.owner_id,
                d.folder_path     AS path,
                d.folder_name     AS name,
                d.parent_id,
                NULL::text        AS mime_type, NULL::bigint AS size_bytes,
                d.visibility, NULL::int AS current_version,
                d.metadata, d.created_at, d.updated_at, d.deleted_at,
                CASE WHEN d.owner_id = %L THEN 'admin' ELSE NULL END AS effective_permission
            FROM cld_folders d
            WHERE %L AND (%L OR d.deleted_at IS NULL) AND d.owner_id = %L
              AND NOT cld_is_system_path(d.folder_path)
            ORDER BY %s LIMIT %s OFFSET %s
        ) t
    $q$,
        p_user_id, p_user_id, p_include_deleted, p_user_id, p_user_id,
        p_user_id, p_include_folders, p_include_deleted, p_user_id,
        v_order, p_limit, p_offset
    ) INTO v_result;

    RETURN v_result;
END;
$function$;

GRANT EXECUTE ON FUNCTION cld_get_user_file_tree(UUID, INTEGER, INTEGER, BOOLEAN, BOOLEAN, TEXT)
    TO authenticated, service_role;

COMMIT;
