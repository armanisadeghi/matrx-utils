-- =============================================================================
-- 008 — Idempotency-key memoization for combined operations.
-- =============================================================================
--
-- Backs the ``X-Idempotency-Key`` header for combined-operation endpoints
-- (``POST /assets`` with bundled share/permissions/variants, ``PATCH /files/{id}``
-- union mutations, ``POST /files/bulk`` discriminator). The FE retries
-- with the same key after a flaky network and gets back the original
-- response envelope verbatim — no duplicate file_id, no duplicate share
-- token, no duplicate permission grants, no duplicate variants.
--
-- Lifecycle:
--   * Server records (owner_id, idempotency_key, request_hash) on first
--     completion, alongside the response_body it returned.
--   * On retry with the same (owner_id, key), if request_hash matches,
--     the cached response is returned without re-executing the op.
--   * If request_hash MISMATCHES (caller reused the key with different
--     body), the server returns 409 Conflict.
--   * Rows auto-expire after 24h via the partial index + a sweep job
--     (next migration / sweep is host-side cron).
--
-- The ``cld_uploads_inflight`` table already memoizes in-progress TUS
-- creates; this table is the COMPLETED-OPERATION sibling for everything
-- else.
--
-- Idempotent migration.
-- =============================================================================

BEGIN;

CREATE TABLE IF NOT EXISTS public.cld_idempotency (
    -- Caller-supplied key. Unique per owner.
    owner_id        UUID NOT NULL,
    idempotency_key TEXT NOT NULL,

    -- SHA-256 of the request envelope (path + canonical body). Lets us
    -- detect "same key, different request" and 409 instead of returning
    -- the wrong cached response.
    request_hash    TEXT NOT NULL,

    -- The endpoint that produced the response (e.g. "POST /assets").
    -- Lets ops slice by endpoint for hit-rate / replay analysis.
    endpoint        TEXT NOT NULL,

    -- HTTP status the cached response should replay with.
    status_code     INT NOT NULL,

    -- The response body, JSONB. The FE gets the exact same envelope on
    -- retry — same file_id, same share token, same errors[] entries.
    response_body   JSONB NOT NULL,

    -- Optional pointer to a primary resource so admin tools can find
    -- the originating file/asset/share-link without parsing the body.
    resource_id     UUID,
    resource_type   TEXT,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT (now() + INTERVAL '24 hours'),

    PRIMARY KEY (owner_id, idempotency_key)
);

-- Sweep index: pick up rows past their TTL for the daily cleanup job.
CREATE INDEX IF NOT EXISTS idx_cld_idempotency_expires
    ON public.cld_idempotency (expires_at)
    WHERE expires_at IS NOT NULL;

-- Optional resource index for forensic lookups ("which idempotency key
-- created this file_id?").
CREATE INDEX IF NOT EXISTS idx_cld_idempotency_resource
    ON public.cld_idempotency (resource_id)
    WHERE resource_id IS NOT NULL;

-- RLS — owners see only their own idempotency rows. Writes go through
-- the API (service-role) and bypass RLS.
ALTER TABLE public.cld_idempotency ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS cld_idempotency_owner_select ON public.cld_idempotency;
CREATE POLICY cld_idempotency_owner_select ON public.cld_idempotency
    FOR SELECT USING (owner_id = auth.uid());

COMMIT;
