-- =============================================================================
-- 005 — TUS resumable upload state + Supabase Realtime publication.
-- =============================================================================
--
-- Consolidates two aidream-side migrations (0036 + 0002 + 0032) that
-- belong in the packaged SQL because they're pure cloud-sync features:
--
--   1. cld_uploads_inflight — TUS protocol state registry. Tracks
--      in-progress multipart uploads (S3 multipart upload-id, parts
--      ACKed so far, idempotency key, expires_at). The matrx-utils
--      TUS transport reads/writes this table directly.
--
--   2. Supabase Realtime publication for cld_files / cld_share_links /
--      cld_file_permissions. Lets the FE subscribe to file mutations
--      without polling. Optional — gated by the publication existing
--      (which it always does on Supabase projects).
--
-- NOTE: The aidream host migration 0032 ALSO publishes the host-only
-- ``processed_documents`` table. That stays in aidream — it's a host
-- concern, not a matrx-utils concept.
--
-- NOTE: aidream migrations 0039 (file_analysis) and 0040 (redaction_mapping)
-- are NOT included here. Their RLS policies depend on the host-side
-- ``public.is_resource_owner`` and ``public.shareable_resource_registry``
-- which matrx-utils doesn't ship. Those remain aidream host migrations.
--
-- All statements idempotent.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. cld_uploads_inflight — TUS resumable upload state.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.cld_uploads_inflight (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL,

    -- The eventual cld_files row. Allocated up-front so the canonical
    -- storage URI can be computed before the bytes land.
    file_id         UUID NOT NULL,

    -- Logical path the user supplied at create time.
    file_path       TEXT NOT NULL,

    -- S3-side tracking.
    bucket          TEXT NOT NULL,
    key             TEXT NOT NULL,
    multipart_upload_id TEXT NOT NULL,

    -- TUS-protocol state.
    upload_length   BIGINT NOT NULL,            -- Total expected bytes; from Upload-Length header.
    upload_offset   BIGINT NOT NULL DEFAULT 0,  -- Bytes acknowledged by the server.
    visibility      TEXT NOT NULL DEFAULT 'private',
    mime_type       TEXT,
    file_name       TEXT NOT NULL,

    -- Idempotency: a TUS create with X-Idempotency-Key matching an
    -- in-progress row from the same owner returns that row's id rather
    -- than creating a new multipart upload.
    idempotency_key TEXT,

    -- jsonb for the TUS Upload-Metadata header (already parsed) plus
    -- any FE-supplied metadata that should be merged into cld_files
    -- on completion.
    metadata        JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- Completed S3 parts: [{"PartNumber": int, "ETag": str}, ...] in
    -- upload order. Consumed by complete_multipart_upload at the end.
    parts           JSONB NOT NULL DEFAULT '[]'::jsonb,

    -- 'in_progress' | 'completed' | 'aborted'.
    status          TEXT NOT NULL DEFAULT 'in_progress'
                       CHECK (status IN ('in_progress', 'completed', 'aborted')),

    expires_at      TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '7 days'),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cld_uploads_inflight_owner
    ON public.cld_uploads_inflight (owner_id, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_cld_uploads_inflight_expires
    ON public.cld_uploads_inflight (expires_at)
    WHERE status = 'in_progress';
CREATE UNIQUE INDEX IF NOT EXISTS uq_cld_uploads_inflight_idempotency
    ON public.cld_uploads_inflight (owner_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL AND status = 'in_progress';

-- RLS — owners can read their own in-flight uploads (the FE may show
-- a "resume your upload?" prompt). Writes go through the API.
ALTER TABLE public.cld_uploads_inflight ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS cld_uploads_inflight_owner_select ON public.cld_uploads_inflight;
CREATE POLICY cld_uploads_inflight_owner_select ON public.cld_uploads_inflight
    FOR SELECT USING (owner_id = auth.uid());


-- ---------------------------------------------------------------------------
-- 2. Supabase Realtime publication for cld_* tables.
-- ---------------------------------------------------------------------------
-- Idempotent — every ADD TABLE is guarded by a publication-table existence
-- check. REPLICA IDENTITY FULL is required for UPDATE events to deliver
-- the previous row state so the subscriber can detect soft-deletes /
-- visibility flips without an extra round-trip.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime') THEN
        -- Not on Supabase (or publication not created yet) — skip silently.
        -- Hosts can re-run this migration after creating the publication.
        RETURN;
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime'
          AND schemaname = 'public' AND tablename = 'cld_files'
    ) THEN
        EXECUTE 'ALTER PUBLICATION supabase_realtime ADD TABLE public.cld_files';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime'
          AND schemaname = 'public' AND tablename = 'cld_share_links'
    ) THEN
        EXECUTE 'ALTER PUBLICATION supabase_realtime ADD TABLE public.cld_share_links';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables
        WHERE pubname = 'supabase_realtime'
          AND schemaname = 'public' AND tablename = 'cld_file_permissions'
    ) THEN
        EXECUTE 'ALTER PUBLICATION supabase_realtime ADD TABLE public.cld_file_permissions';
    END IF;
END $$;

ALTER TABLE public.cld_files REPLICA IDENTITY FULL;
ALTER TABLE public.cld_share_links REPLICA IDENTITY FULL;
ALTER TABLE public.cld_file_permissions REPLICA IDENTITY FULL;

COMMIT;
