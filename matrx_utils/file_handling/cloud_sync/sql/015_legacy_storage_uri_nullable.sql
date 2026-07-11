-- =============================================================================
-- 015 — Make _legacy_storage_uri nullable (fixes 007 fallout).
-- =============================================================================
--
-- Migration 007 renamed the legacy `storage_uri` column to `_legacy_storage_uri`.
-- A column RENAME carries its constraints, so `_legacy_storage_uri` inherited
-- the original NOT NULL. But it is a ROLLBACK-ONLY preservation column: rows
-- created AFTER 007 have no legacy value, and the write path does not populate
-- it. The result was every new INSERT failing with:
--
--   null value in column "_legacy_storage_uri" of relation "cld_files"
--   violates not-null constraint
--
-- Drop the NOT NULL so new rows may omit it. (`_legacy_storage_uri` is dropped
-- entirely in a later migration once the 007 bake window closes.)

BEGIN;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
         WHERE table_schema = 'public'
           AND table_name = 'cld_files'
           AND column_name = '_legacy_storage_uri'
           AND is_nullable = 'NO'
    ) THEN
        ALTER TABLE public.cld_files ALTER COLUMN _legacy_storage_uri DROP NOT NULL;
    END IF;
END
$$;

COMMIT;
