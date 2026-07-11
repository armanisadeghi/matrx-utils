-- =============================================================================
-- 007 — Drop legacy storage_uri after rekey backfill completes.
-- =============================================================================
--
-- ONLY APPLY THIS MIGRATION AFTER the backfill has completed and you have
-- verified the precondition below (zero NULL canonical_storage_uri rows
-- with non-NULL legacy storage_uri).
--
-- PRECONDITION CHECK
-- ------------------
--   SELECT count(*) FROM public.cld_files
--    WHERE canonical_storage_uri IS NULL
--      AND storage_uri IS NOT NULL
--      AND deleted_at IS NULL;
--
-- Expected: 0. If non-zero, run the rekey backfill until it reaches 0:
--
--   python -m aidream.cli.rekey_backfill                    # or
--   python -m matrx_utils.file_handling.cloud_sync.backfill rekey   # standalone
--
-- WHAT IT DOES
-- ------------
-- 1. Renames the legacy ``storage_uri`` column to ``_legacy_storage_uri``
--    (kept temporarily for rollback safety; can be dropped in a later
--    migration after the bake window).
-- 2. Renames ``canonical_storage_uri`` to ``storage_uri``.
-- 3. Adds NOT NULL constraint on the new ``storage_uri`` so all rows
--    going forward carry the canonical URI from day one.
--
-- After this migration:
--   * ``cld_files.storage_uri`` IS the canonical URI keyed by file_id.
--   * ``_legacy_storage_uri`` is preserved for one bake cycle.
--   * All matrx-utils code that previously read
--     ``record.get("canonical_storage_uri") or record["storage_uri"]``
--     now just reads ``record["storage_uri"]``.
--
-- This migration is GATED — runs only when the precondition is satisfied.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- Hard precondition check. Fails the transaction if backfill is incomplete.
-- ---------------------------------------------------------------------------
DO $$
DECLARE
    pending_count BIGINT;
BEGIN
    -- Skip the check entirely if we've already applied this migration
    -- (canonical_storage_uri column no longer exists).
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = 'canonical_storage_uri'
    ) THEN
        RETURN;
    END IF;

    EXECUTE 'SELECT count(*) FROM public.cld_files
              WHERE canonical_storage_uri IS NULL
                AND storage_uri IS NOT NULL
                AND deleted_at IS NULL'
        INTO pending_count;

    IF pending_count > 0 THEN
        RAISE EXCEPTION
            'Cannot apply migration 007: % rows still have NULL canonical_storage_uri.
             Run the rekey backfill first:
                 python -m aidream.cli.rekey_backfill
             then re-apply this migration.',
            pending_count;
    END IF;
END
$$;


-- ---------------------------------------------------------------------------
-- Rename: legacy storage_uri → _legacy_storage_uri (preserved for rollback).
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = 'storage_uri'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = '_legacy_storage_uri'
    ) THEN
        ALTER TABLE public.cld_files RENAME COLUMN storage_uri TO _legacy_storage_uri;
    END IF;
END
$$;


-- ---------------------------------------------------------------------------
-- Rename: canonical_storage_uri → storage_uri.
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = 'canonical_storage_uri'
    ) AND NOT EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = 'storage_uri'
    ) THEN
        ALTER TABLE public.cld_files RENAME COLUMN canonical_storage_uri TO storage_uri;
    END IF;
END
$$;


-- ---------------------------------------------------------------------------
-- Rename the unique index alongside the column.
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_indexes
         WHERE schemaname = 'public' AND indexname = 'uq_cld_files_canonical_storage_uri'
    ) AND NOT EXISTS (
        SELECT 1 FROM pg_indexes
         WHERE schemaname = 'public' AND indexname = 'uq_cld_files_storage_uri'
    ) THEN
        ALTER INDEX public.uq_cld_files_canonical_storage_uri
            RENAME TO uq_cld_files_storage_uri;
    END IF;
END
$$;


-- ---------------------------------------------------------------------------
-- Enforce NOT NULL on the new storage_uri.
-- ---------------------------------------------------------------------------
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = 'storage_uri'
           AND is_nullable = 'YES'
    ) THEN
        ALTER TABLE public.cld_files ALTER COLUMN storage_uri SET NOT NULL;
    END IF;
END
$$;

COMMENT ON COLUMN public.cld_files.storage_uri IS
'Canonical S3 URI keyed by file_id (<backend>://<bucket>/<owner_id>/<file_id>).
After migration 007 this is the ONLY storage URI; the legacy path-keyed URI
lives in _legacy_storage_uri for the rollback window.';

COMMIT;
