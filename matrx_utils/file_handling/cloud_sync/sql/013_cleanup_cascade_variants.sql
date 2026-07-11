-- migrate: skip: obsolete — 0 cascade-junk rows remain in prod and lineage
--   (parent_file_id/derivation_kind) is already backfilled (verified 2026-05-20).
--   The incident this cleaned up no longer exists in the data. Kept for history.
-- =============================================================================
-- 013 — Cleanup cascade-junk variants + backfill native lineage columns.
-- =============================================================================
--
-- Companion to migration 012. The backfill incident wrote ~7,700 variant
-- rows, of which:
--
--   - 1,565 are legitimate first-level variants (derived directly from
--     a master). These KEEP their data — we just stamp the native
--     ``parent_file_id`` + ``derivation_kind`` columns from
--     ``metadata.derived_from`` so consumers can identify them by
--     data shape (Phase 1d.3 forward-write parity).
--
--   - 6,152 are cascade junk (derived from another variant, up to 12
--     levels deep). These get SOFT-DELETED — ``deleted_at = NOW()``
--     and a ``metadata.cascade_cleanup = true`` marker so a future
--     janitor job can identify them for S3 cleanup.
--
-- Classification key: a row is cascade junk iff its
-- ``metadata.derived_from`` points to another row whose
-- ``metadata.derived_from`` is also set (parent is itself a variant).
--
-- Reversible: ``UPDATE cld_files SET deleted_at = NULL WHERE
-- metadata ? 'cascade_cleanup'`` undoes the soft-delete.
--
-- Idempotent: re-runs only touch rows that haven't been classified yet.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 0. Extend the derivation_kind enum to recognise 'variant'.
-- ---------------------------------------------------------------------------
-- The original constraint (added in migration 004) listed only the
-- intent-named derivation kinds the page-extraction pipeline produces
-- (manual_upload, extracted_pages, cropped, etc.). Variants are a new
-- kind that didn't exist when 004 shipped; add it now so the
-- forward-write path in VariantsService can stamp it on every new
-- variant row.
ALTER TABLE public.cld_files
    DROP CONSTRAINT IF EXISTS cld_files_derivation_kind_known;

ALTER TABLE public.cld_files
    ADD CONSTRAINT cld_files_derivation_kind_known
    CHECK (
        derivation_kind IS NULL
        OR derivation_kind = ANY (ARRAY[
            'manual_upload',
            'extracted_pages',
            'cropped',
            'rotated',
            'pages_deleted',
            'merged',
            'split_part',
            'compressed',
            'rendered_page_image',
            'cleaned',
            'variant'
        ])
    );

-- Classify every variant row once. The two updates below read from this
-- materialised CTE so the join is computed once.
WITH classified AS (
  SELECT
    v.id                                          AS variant_id,
    (v.metadata->>'derived_from')::uuid           AS direct_parent_id,
    (p.metadata->>'derived_from') IS NOT NULL     AS parent_is_variant
  FROM cld_files v
  JOIN cld_files p ON p.id = (v.metadata->>'derived_from')::uuid
  WHERE v.deleted_at IS NULL
    AND (v.metadata->>'derived_from') IS NOT NULL
),

-- Step 1: backfill native lineage columns on legitimate first-level
-- variants (parent is a master, not another variant). Only updates
-- rows whose columns aren't already set so re-runs are no-ops.
backfilled AS (
  UPDATE cld_files target
  SET
    parent_file_id  = c.direct_parent_id,
    derivation_kind = 'variant'
  FROM classified c
  WHERE target.id = c.variant_id
    AND NOT c.parent_is_variant
    AND target.parent_file_id IS NULL
  RETURNING target.id
),

-- Step 2: soft-delete cascade junk + mark with cascade_cleanup tag so a
-- future S3-janitor job knows which storage objects to remove.
soft_deleted AS (
  UPDATE cld_files target
  SET
    deleted_at = NOW(),
    metadata   = jsonb_set(
      COALESCE(target.metadata, '{}'::jsonb),
      '{cascade_cleanup}',
      'true'::jsonb
    )
  FROM classified c
  WHERE target.id = c.variant_id
    AND c.parent_is_variant
    AND target.deleted_at IS NULL
  RETURNING target.id
)

-- Final counts (visible in the migration log when the migration runs).
SELECT
  (SELECT COUNT(*) FROM backfilled)   AS variants_backfilled,
  (SELECT COUNT(*) FROM soft_deleted) AS cascade_junk_soft_deleted;

COMMIT;
