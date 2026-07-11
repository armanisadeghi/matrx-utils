-- Variant catalog lookup index.
--
-- VariantsService.list_existing_async(master_record) queries cld_files for
-- every row whose metadata.derived_from equals the master file_id. Without
-- an index this is a sequential scan over the entire cld_files table on
-- every variant render — which collapses to O(n) once any user accumulates
-- thousands of files.
--
-- B-tree on the expression so the equality lookup is O(log n). We don't
-- need a GIN index here because the query is always a single equality
-- check on a known scalar key, not a containment / path query.
--
-- Idempotent: IF NOT EXISTS, and the column is a JSONB-extracted text so
-- the partial WHERE keeps the index sparse (only rows that have a
-- derived_from at all — which is the variant subset).

CREATE INDEX IF NOT EXISTS idx_cld_files_derived_from
ON public.cld_files ((metadata->>'derived_from'))
WHERE metadata ? 'derived_from' AND deleted_at IS NULL;

-- Companion index for the (master, variant_key) tuple lookups some callers
-- may want to do directly. Composite expression index — cheap to maintain
-- because variant rows are write-once, then read-many.

CREATE INDEX IF NOT EXISTS idx_cld_files_variant_key
ON public.cld_files ((metadata->>'derived_from'), (metadata->>'variant_key'))
WHERE metadata ? 'variant_key' AND deleted_at IS NULL;
