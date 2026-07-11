-- migrate: skip: cld_files.thumbnail_url / thumbnail_storage_uri are intentionally absent (dropped by 011); false-positive PARTIAL otherwise.
-- =============================================================================
-- 004 — Lineage, thumbnails, webhook dispatcher.
-- =============================================================================
--
-- Consolidates three concerns that aidream previously shipped as separate
-- host migrations (0006 / 0033 / 0034) but which are pure file-handling
-- features. Bundling them into matrx-utils means any host that runs the
-- packaged SQL gets:
--
--   1. Binary lineage on cld_files (parent_file_id + derivation_kind +
--      derivation_metadata) — every derived file (PDF extract, crop,
--      rotate, merge, compress, page render) tracks its ancestor.
--
--   2. Thumbnail columns on cld_files (thumbnail_storage_uri +
--      thumbnail_url) — the upload pipeline's fire-and-forget thumbnail
--      generator persists its output here so the FE grid view shows
--      real thumbnails instead of category icons.
--
--   3. Webhook dispatcher schema (cld_events.processed_at + cld_webhooks
--      + cld_webhook_deliveries) — the long-running async dispatcher in
--      cloud_sync.events drains cld_events to subscribed webhooks with
--      HMAC-SHA256 signatures and exponential-backoff retry.
--
-- All statements idempotent — guarded by IF NOT EXISTS / DO $$ checks.
-- =============================================================================

BEGIN;

-- ---------------------------------------------------------------------------
-- 1. Binary lineage on cld_files (formerly aidream/db/migrations/0006).
-- ---------------------------------------------------------------------------

ALTER TABLE public.cld_files
    ADD COLUMN IF NOT EXISTS parent_file_id      UUID
        REFERENCES public.cld_files(id) ON DELETE SET NULL,
    ADD COLUMN IF NOT EXISTS derivation_kind     TEXT,
    ADD COLUMN IF NOT EXISTS derivation_metadata JSONB NOT NULL DEFAULT '{}'::jsonb;

-- Soft constraint: if parent_file_id is set, derivation_kind SHOULD be set
-- too. CHECK rather than NOT NULL because legacy rows have both NULL.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'cld_files_lineage_consistency'
          AND  conrelid = 'public.cld_files'::regclass
    ) THEN
        ALTER TABLE public.cld_files
            ADD CONSTRAINT cld_files_lineage_consistency
            CHECK (
                (parent_file_id IS NULL)
                OR (derivation_kind IS NOT NULL)
            );
    END IF;
END
$$;

-- Open enum of derivation_kind values. Application layer extends without
-- a migration when new tags are added in lockstep.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE  conname = 'cld_files_derivation_kind_known'
          AND  conrelid = 'public.cld_files'::regclass
    ) THEN
        ALTER TABLE public.cld_files
            ADD CONSTRAINT cld_files_derivation_kind_known
            CHECK (
                derivation_kind IS NULL
                OR derivation_kind IN (
                    'manual_upload',
                    'extracted_pages',
                    'cropped',
                    'rotated',
                    'pages_deleted',
                    'merged',
                    'split_part',
                    'compressed',
                    'rendered_page_image',
                    'cleaned'
                )
            );
    END IF;
END
$$;

-- Lineage queries: "all derivatives of file X".
CREATE INDEX IF NOT EXISTS idx_cld_files_parent
    ON public.cld_files (parent_file_id)
    WHERE deleted_at IS NULL AND parent_file_id IS NOT NULL;

-- "What kind of derivative is this?" filters.
CREATE INDEX IF NOT EXISTS idx_cld_files_derivation_kind
    ON public.cld_files (derivation_kind)
    WHERE deleted_at IS NULL AND derivation_kind IS NOT NULL;


-- ---------------------------------------------------------------------------
-- 2. Thumbnail columns on cld_files (formerly aidream/db/migrations/0033).
-- ---------------------------------------------------------------------------

ALTER TABLE public.cld_files
    ADD COLUMN IF NOT EXISTS thumbnail_storage_uri text,
    ADD COLUMN IF NOT EXISTS thumbnail_url         text;

COMMENT ON COLUMN public.cld_files.thumbnail_storage_uri IS
'Storage URI of the generated thumbnail. NULL means no thumbnail yet
(FE falls back to category icon).';

COMMENT ON COLUMN public.cld_files.thumbnail_url IS
'Direct URL for the thumbnail. CDN URL when public + CDN configured,
NULL otherwise (FE asks the API for a signed URL on demand).';


-- ---------------------------------------------------------------------------
-- 3. Webhook dispatcher (formerly aidream/db/migrations/0034).
-- ---------------------------------------------------------------------------
-- The cld_events audit-log table itself already exists from 003 (security
-- and quotas). Here we add the dispatcher cursor + subscriber registry +
-- per-attempt delivery log so the matrx-utils webhook dispatcher worker
-- can drain cld_events.

-- Dispatcher cursor on the audit log.
ALTER TABLE public.cld_events
    ADD COLUMN IF NOT EXISTS processed_at TIMESTAMPTZ;

-- Partial index for the dispatcher's hot loop.
CREATE INDEX IF NOT EXISTS idx_cld_events_unprocessed
    ON public.cld_events (occurred_at)
    WHERE processed_at IS NULL;

-- Subscriber registry.
CREATE TABLE IF NOT EXISTS public.cld_webhooks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_id        UUID NOT NULL,
    target_url      TEXT NOT NULL,
    secret          TEXT NOT NULL,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT true,
    event_types     TEXT[] DEFAULT NULL,
    resource_types  TEXT[] DEFAULT NULL,
    last_attempt_at TIMESTAMPTZ,
    last_success_at TIMESTAMPTZ,
    consecutive_failures INT NOT NULL DEFAULT 0,
    max_consecutive_failures INT NOT NULL DEFAULT 50,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cld_webhooks_owner
    ON public.cld_webhooks (owner_id, is_active);
CREATE INDEX IF NOT EXISTS idx_cld_webhooks_active
    ON public.cld_webhooks (is_active)
    WHERE is_active = true;

-- Per-attempt delivery log.
CREATE TABLE IF NOT EXISTS public.cld_webhook_deliveries (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id      UUID NOT NULL REFERENCES public.cld_webhooks(id) ON DELETE CASCADE,
    event_id        UUID NOT NULL REFERENCES public.cld_events(id) ON DELETE CASCADE,
    attempt         INT NOT NULL DEFAULT 1,
    status          TEXT NOT NULL DEFAULT 'pending'
                       CHECK (status IN ('pending', 'delivered', 'failed', 'abandoned')),
    http_status     INT,
    latency_ms      INT,
    error_message   TEXT,
    next_attempt_at TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at    TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_cld_webhook_deliveries_pending
    ON public.cld_webhook_deliveries (next_attempt_at)
    WHERE status = 'failed' AND next_attempt_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cld_webhook_deliveries_event
    ON public.cld_webhook_deliveries (event_id);
CREATE INDEX IF NOT EXISTS idx_cld_webhook_deliveries_webhook_time
    ON public.cld_webhook_deliveries (webhook_id, created_at DESC);

-- RLS — owners see their own webhooks + delivery logs.
ALTER TABLE public.cld_webhooks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS cld_webhooks_owner_all ON public.cld_webhooks;
CREATE POLICY cld_webhooks_owner_all ON public.cld_webhooks
    FOR ALL USING (owner_id = auth.uid())
    WITH CHECK (owner_id = auth.uid());

ALTER TABLE public.cld_webhook_deliveries ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS cld_webhook_deliveries_owner_select ON public.cld_webhook_deliveries;
CREATE POLICY cld_webhook_deliveries_owner_select ON public.cld_webhook_deliveries
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.cld_webhooks w
             WHERE w.id = cld_webhook_deliveries.webhook_id
               AND w.owner_id = auth.uid()
        )
    );

COMMIT;
