-- =============================================================================
-- 006 — Canonical storage URI on cld_files.
-- =============================================================================
--
-- Adds canonical_storage_uri to cld_files so renames and moves become pure
-- DB operations (no S3 copy). The matrx-utils upload pipeline writes to
-- the canonical key from day one of v1.1.0; reads prefer canonical and
-- fall back to legacy ``storage_uri`` for any pre-1.1.0 rows that haven't
-- been backfilled yet.
--
-- WHY CANONICAL KEYS
-- ------------------
-- Legacy S3 keys are ``<owner>/<file_path>``, which bakes the logical
-- path into the physical key. Every rename re-copies bytes (or accepts
-- drift between ``cld_files.file_path`` and ``storage_uri``). The
-- canonical scheme ``<owner>/<file_id>`` makes:
--   * renames pure DB ops (UPDATE cld_files SET file_path = ...).
--   * tenant migration a single UPDATE of owner_id (S3 stays put).
--   * checksum-based de-dupe trivial.
--
-- ROLLOUT
-- -------
-- 1. This migration runs. Adds the column nullable + unique index.
-- 2. New writes from matrx-utils v1.1.0 onwards go to the canonical key
--    AND populate canonical_storage_uri at insert time.
-- 3. Legacy rows (pre-1.1.0) keep storage_uri pointing at the legacy
--    key. The backfill job (matrx_utils.file_handling.cloud_sync.backfill.rekey)
--    walks them: server-side S3 copy from legacy to canonical, then
--    UPDATE the row. Idempotent + resumable.
-- 4. After the backfill confirms zero NULL canonical rows for the
--    bake window, migration 007 drops the legacy column and renames
--    canonical_storage_uri → storage_uri.
--
-- Idempotent.
-- =============================================================================

BEGIN;

ALTER TABLE public.cld_files
    ADD COLUMN IF NOT EXISTS canonical_storage_uri TEXT;

-- Unique to prevent two rows accidentally pointing at the same canonical
-- key. Null values do not violate UNIQUE.
CREATE UNIQUE INDEX IF NOT EXISTS uq_cld_files_canonical_storage_uri
    ON public.cld_files (canonical_storage_uri)
    WHERE canonical_storage_uri IS NOT NULL;

COMMENT ON COLUMN public.cld_files.canonical_storage_uri IS
'Canonical S3 URI keyed by file_id (<backend>://<bucket>/<owner_id>/<file_id>).
matrx-utils v1.1.0+ writes here at insert time. Legacy pre-1.1.0 rows have
NULL — backfill via matrx_utils.file_handling.cloud_sync.backfill.rekey.
Migration 007 (run after backfill completes) drops the legacy storage_uri
column and renames this column back to storage_uri.';

COMMIT;
