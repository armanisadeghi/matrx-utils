-- =============================================================================
-- 014 — User-tree privacy fix + usability improvements.
-- =============================================================================
--
-- Two fixes bundled because both touch ``cld_get_user_file_tree``:
--
-- 1. PRIVACY (FE item 0a) — drop the ``OR f.visibility = 'public'`` clause
--    from the file-leg WHERE. ``visibility = 'public'`` is the share-link
--    policy ("anyone with the URL can read") — it is NOT a tree-membership
--    signal. Before this fix, every authenticated user saw every public
--    file in the entire system inside their own ``/files`` view (podcast
--    covers, OG images, social-baseline variants of other users' uploads,
--    etc.). Reported leak: 50 public files from 5 owners visible to one
--    test user after migration 012's system-files filter.
--
--    The folder leg never had this bug — it correctly uses
--    ``AND d.owner_id = p_user_id``. The file leg now matches.
--
--    Sharing of public files still works: anyone with the URL can read,
--    explicit grants via ``cld_file_permissions`` still grant tree
--    visibility via ``cld_get_effective_permission``. The change is
--    just that "public" alone no longer means "include in every user's
--    tree".
--
-- 2. USABILITY (FE item 0c) — three small improvements:
--    a. Bump ``p_limit`` DEFAULT from 200 → 5000 (the FE always passes
--       5000 explicitly so this matches reality; ad-hoc callers no
--       longer silently truncate at 200).
--    b. Add ``p_order_by`` parameter accepting ``'name'`` (default,
--       back-compat) | ``'updated_at_desc'`` | ``'created_at_desc'``.
--       Lets "Recents" surfaces order by recency instead of alphabet
--       (the previous ``zebra.png`` upload was last-page only).
--    c. Add ``cld_count_user_files`` companion so the FE can show
--       "loading 3 of N pages" progress instead of a spinner.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- cld_get_user_file_tree — privacy fix + p_order_by + bumped default.
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION cld_get_user_file_tree(
    p_user_id UUID,
    p_limit INT DEFAULT 5000,
    p_offset INT DEFAULT 0,
    p_include_folders BOOLEAN DEFAULT TRUE,
    p_include_deleted BOOLEAN DEFAULT FALSE,
    p_order_by TEXT DEFAULT 'name'
) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
    v_order  TEXT;
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden: p_user_id does not match auth.uid()'
            USING ERRCODE = '42501';
    END IF;

    p_limit := LEAST(GREATEST(p_limit, 1), 5000);

    -- Resolve the requested ordering to a safe ORDER BY expression.
    -- The inner SELECT's column list always exposes name (5), updated_at
    -- (13), created_at (12) — order numbers shared by both legs of the
    -- UNION ALL — so the same numbered ORDER BY works for files +
    -- folders.
    v_order := CASE lower(coalesce(p_order_by, 'name'))
        WHEN 'updated_at_desc' THEN '13 DESC NULLS LAST'
        WHEN 'created_at_desc' THEN '12 DESC NULLS LAST'
        WHEN 'name'            THEN '5'
        ELSE '5'  -- unknown values silently fall back to name (back-compat)
    END;

    EXECUTE format($q$
        SELECT COALESCE(jsonb_agg(row_to_json(t)::jsonb), '[]'::jsonb)
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
                    WHEN f.owner_id = %L THEN 'admin'
                    ELSE cld_get_effective_permission(f.id, %L)
                END AS effective_permission
            FROM cld_files f
            WHERE (%L OR f.deleted_at IS NULL)
              AND f.parent_file_id IS NULL
              AND f.file_path NOT LIKE 'system-files/%%'
              -- PRIVACY FIX (014): owner OR explicit grant only.
              -- ``visibility = 'public'`` does NOT grant tree
              -- membership — it grants URL-read only.
              AND (
                  f.owner_id = %L
                  OR cld_get_effective_permission(f.id, %L) IS NOT NULL
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
                    WHEN d.owner_id = %L THEN 'admin'
                    ELSE NULL
                END AS effective_permission
            FROM cld_folders d
            WHERE %L
              AND (%L OR d.deleted_at IS NULL)
              AND d.owner_id = %L
            ORDER BY %s
            LIMIT %s OFFSET %s
        ) t
    $q$,
        p_user_id, p_user_id, p_include_deleted, p_user_id, p_user_id,
        p_user_id, p_include_folders, p_include_deleted, p_user_id,
        v_order, p_limit, p_offset
    ) INTO v_result;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- ---------------------------------------------------------------------------
-- cld_count_user_files — companion for FE pagination-progress UX.
-- ---------------------------------------------------------------------------
-- Returns the total count of rows ``cld_get_user_file_tree`` would
-- yield for the same user / include_folders / include_deleted args.
-- Used by the FE to show "loading page 3 of N" instead of an unbounded
-- spinner when a tree is large enough to require pagination.
CREATE OR REPLACE FUNCTION cld_count_user_files(
    p_user_id UUID,
    p_include_folders BOOLEAN DEFAULT TRUE,
    p_include_deleted BOOLEAN DEFAULT FALSE
) RETURNS JSONB AS $$
DECLARE
    v_files   INT;
    v_folders INT;
BEGIN
    IF auth.uid() IS NOT NULL AND auth.uid() <> p_user_id THEN
        RAISE EXCEPTION 'forbidden: p_user_id does not match auth.uid()'
            USING ERRCODE = '42501';
    END IF;

    -- File leg — mirrors cld_get_user_file_tree's filters EXACTLY.
    -- Owner OR explicit grant. No public-OR, no system-files, no derived rows.
    SELECT COUNT(*) INTO v_files
    FROM cld_files f
    WHERE (p_include_deleted OR f.deleted_at IS NULL)
      AND f.parent_file_id IS NULL
      AND f.file_path NOT LIKE 'system-files/%'
      AND (
          f.owner_id = p_user_id
          OR cld_get_effective_permission(f.id, p_user_id) IS NOT NULL
      );

    IF p_include_folders THEN
        SELECT COUNT(*) INTO v_folders
        FROM cld_folders d
        WHERE (p_include_deleted OR d.deleted_at IS NULL)
          AND d.owner_id = p_user_id;
    ELSE
        v_folders := 0;
    END IF;

    RETURN jsonb_build_object(
        'files', v_files,
        'folders', v_folders,
        'total', v_files + v_folders
    );
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

COMMIT;
