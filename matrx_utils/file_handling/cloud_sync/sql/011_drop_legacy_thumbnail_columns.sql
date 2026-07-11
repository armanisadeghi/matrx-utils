-- =============================================================================
-- 011 — Drop legacy ``cld_files.thumbnail_*`` columns (Phase 1b).
-- =============================================================================
--
-- Phase 1 (migration 010 + the UnifiedMediaBlock rollout) introduced the
-- universal variants pipeline: every uploaded file gets ``og_url`` /
-- ``thumbnail_url`` / ``tiny_url`` SOCIAL_BASELINE variants as cld_files
-- rows linked back to the master via ``metadata.derived_from``.
--
-- The legacy column-based thumbnail storage from migration 004
-- (``thumbnail_storage_uri`` + ``thumbnail_url``) is therefore obsolete.
-- Every reader has been migrated to ``thumbnail_resolver.resolve_thumbnail_url_async``
-- and the legacy ``generate_thumbnail_for_file`` writer was rewritten to
-- dispatch through ``SyncEngine.variants.render_async`` instead of
-- writing these columns.
--
-- This migration drops both columns. Data is intentionally NOT migrated:
-- any cld_files row that was previously thumbnailed via the old column-
-- write path can be re-thumbnailed on demand by re-running
-- ``run_thumbnail_backfill(fm)``, which is now idempotent at the variant
-- level via VariantsService.
--
-- Idempotent (DROP COLUMN IF EXISTS).
-- =============================================================================

BEGIN;

ALTER TABLE public.cld_files
    DROP COLUMN IF EXISTS thumbnail_storage_uri,
    DROP COLUMN IF EXISTS thumbnail_url;

COMMIT;
