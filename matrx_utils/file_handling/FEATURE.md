# FEATURE — Client-facing file references (the OUT contract)

**The native storage location never reaches a client.** `storage_uri` /
`file_uri` (`s3://bucket/owner/key`) is server-only — a client can do nothing
with it and exposing one is info-disclosure. The lean client reference is
**`FileRef`**. Verified against code 2026-07-04.

## Reading a file — the ONE access gate (the IN contract)

🔒 **The server bypasses Postgres RLS** — cloud_sync connects with the
service-role key (`db.py`), so `db.get_file*` returns ANY user's row. The ONLY
thing between one user and another user's file is a **code-level access check**.
Therefore: **every read of a file's bytes / lookup of a record for a REQUEST
must go through the authorized gate**, which enforces owner / public / shared
(`SyncEngine.get_authorized_record_async` → `PermissionsManager`).

- **Media (chat attachments, tool/agent media, references, preview sources):**
  `FileManager.resolve_media[_async]` — the ACCESS GATE lives inside it
  (`cloud_sync/_media_resolution.py::_authorized_or_error_{sync,async}`). It reads
  the request user from the ambient context (`matrx_utils.ctx.get_active_user_id`,
  wired to `AppContext`), enforces access, **trusts a valid share token**, and
  **refuses a raw `s3://` path from a user**. A denial stamps
  `resolver_error="access_denied"`; aidream's `media_normalizer` turns that into a
  **403** (`_raise_if_access_denied`). Test: `tests/test_media_access_gate.py`.
- **Record-first byte reads (preview, pdf-compress, and any request handler that
  turns a client `file_id` into bytes):** `FileService.read_record_for_active_user`
  (enforces for the request user, trusts internal jobs) — NOT raw `db.get_file*`.
- **Internal trust is EXPLICIT and fail-CLOSED (2026-07-09).** With NO request
  context at all, the gate allows the read ONLY when the caller declared itself
  with `matrx_utils.ctx.system_file_access("<reason>")` (a scoped context
  manager; logged at debug). Unmarked no-context resolution DENIES with a loud
  self-identifying red banner (`matrx_validation_gate` style) and stamps
  `resolver_error="access_denied_no_actor"` (also a 403 via
  `_raise_if_access_denied`). A request context that carries NO user (anonymous
  HTTP) is denied outright — the marker does not apply; and a request USER
  always authorizes as that user, marker or not. Stamped internal callers:
  matrx-rag ingest/stages/table-derivation/image-caption, the podcast pipeline,
  the docproc / assets.upload / image-pipeline workflow nodes, and
  `scripts/backfill_audio_video_mime.py`. Never wrap a USER-supplied ref in the
  marker on a request path.

**Guard — `scripts/check_file_access_gate.py`** (loud in `release.sh`, ratchets
vs `file_access_gate_baseline.json`): screams if any code adds a NEW raw
`router.read/write` / `db.get_file*` / `afiles_table(...)` door OUTSIDE the gate
module — and (second layer, 2026-07-09) ratchets every `resolve_media[_async]`
caller (`media_caller` kind), so each NEW caller must be classified:
request-scoped (user rides AppContext) or wrapped in `system_file_access(...)`.
The count only goes down — route a grandfathered door through the gate,
then `--update-baseline`. This is what makes a second unguarded door impossible.
Context: the download path (`/files/{id}`) was always gated; a later "cld makeover"
refactor added preview/chat-media/etc. paths that bypassed it — the gate + guard
close that class. (2026-07-07)

## The two shapes

- **IN — `MediaRef`** ([cloud_sync/media_ref.py](cloud_sync/media_ref.py)):
  a client *references* a file to send us. Exactly one of `file_id | url |
  file_uri`. `file_uri` is a legitimate **input** identifier here (an
  `s3://`/`gs://` URI the caller owns) — this is the ONLY place `file_uri` is
  allowed on a client-facing shape, because it's inbound, not outbound.
- **OUT — `FileRef`** ([asset_envelope.py](asset_envelope.py)): what a client
  *receives* to point at a stored file. `file_id` + the URL contract + display
  metadata, and **nothing else**. Round-trips: the `file_id` a client gets
  back in a `FileRef` is exactly what it sends in a `MediaRef`.

`FileRef` fields: `file_id, visibility, file_name, mime_type, size_bytes, url,
cdn_url, signed_url, signed_url_expires_at, download_url, thumbnail_url`.
Populate the URL flavours via `SyncEngine.build_urls_for_record_async` — **never
hand-mint URLs.**

## The rule, stated absolutely

- **No `storage_uri` / `file_uri` on ANY OUT shape** — response model, stream
  event, or embedded reference. Render/download via `url` / `cdn_url` /
  `signed_url` (+ `signed_url_expires_at`) / `download_url`; identify by
  `file_id`.
- **`file_path` (virtual folder path) is NOT the storage location** — it's the
  user-facing tree key. It stays on the file-*browser* shape (`FileRecord` in
  aidream); the lean `FileRef` omits it.
- **Internal result/entity models keep `storage_uri`** — `SyncResult`,
  `CloudFile`, `CloudFileVersion` are server-side and read it to mint URLs /
  read bytes. They are NOT client-facing. Do not copy their `storage_uri` onto
  a wire shape.

## The four leak channels (all closed)

A client can receive a file description through four structurally distinct
channels. Every one must stay clean:

1. **REST response models** (aidream) — `FileRecord`, `FileUploadResponse`,
   `PresignedUploadResponse`, `AssetVariant`, `VisionMediaUploadResponse`,
   `ResearchUploadResponse`, `DocumentDetail`, `LibraryDocDetail`,
   `LibraryDocOut`. All strip the field; the version endpoints return a
   projected `FileVersionRecord` (never a raw `select("*")` row).
2. **Stream events** — cx-chat `UnifiedMediaBlock` + persisted media parts.
   ✅ **CLOSED**. `file_uri` is REMOVED from the wire type entirely (not just
   nulled): the `MediaBlockShared` subclasses (matrx-connect) and the
   `_StoredMediaPartBase` subclasses (matrx-ai `db/message_parts.py`) no longer
   declare it, so it's gone from `generated/stream-events.ts` (count: 0). Both
   carry a `mode="before"` validator that drops a stale `file_uri` from a
   historical `cx_message.content[]` row (past `extra="forbid"`), and the part
   rescues a genuine external URI into `url`. The 9 content builders that set
   `file_uri=envelope.storage_uri` (matrx-ai `config/media_config.py` ×3,
   `providers/base_media.py`, groq/xai/openai/elevenlabs/openai_image) now set
   only `file_id` + `url`. `file_uri` stays valid ONLY as an INPUT identifier on
   `MediaRef` / `PreviewSource` (still in `api-types.ts`, correctly) and on the
   internal provider content classes (Gemini `gs://` / OpenAI `input_file`) —
   never on an OUT shape. Regenerate after any change: `python
   scripts/generate_types.py`. Test:
   `packages/matrx-connect/tests/test_media_block_no_storage_uri.py`.
3. **Direct client access** — the frontend reads `files.files` as `authenticated`
   (and could write it). ✅ **CLOSED** at the DB for read AND write: table-level
   SELECT/UPDATE/INSERT dropped, re-granted as explicit column lists that omit
   `storage_uri` (a column REVOKE alone is a no-op against a table grant — see
   0147 for SELECT, 0149 for UPDATE/INSERT). The write half matters: an owner
   could otherwise repoint their row's `storage_uri` at another user's S3 object
   (write-side IDOR).
4. **Supabase Realtime WAL** — `files.files` was published full-row. ✅ **CLOSED**:
   `REPLICA IDENTITY DEFAULT` + a column-list publication that omits
   `storage_uri`.

Channels 3+4 are DB-level, **applied to Matrx Main 2026-07-06**:
[0146](../../../../db/migrations/0146_files_storage_uri_isolation.sql) (publication
+ replica identity) + [0147](../../../../db/migrations/0147_files_storage_uri_column_grant.sql)
(SELECT column-grant) + [0149](../../../../db/migrations/0149_files_storage_uri_write_lockdown.sql)
(UPDATE/INSERT column-grant). Deploy order was FE-first (frontend stopped
selecting `storage_uri`) → then the migrations.

> ⚠️ Still OPEN — the **read-side media IDOR**: `resolve_media_async` trusts a
> client `file_id`/`file_uri` with no owner check. That's the resolution *auth
> model*, a separate broad decision — see [KNOWN_DEFECTS.md](../../../../KNOWN_DEFECTS.md).
> The DB grants above stop the FE from *reading/writing* the column; they don't
> make resolution authorize the source ref.

## The guards (two independent layers, each screams)

1. **Static** — [scripts/audit_api_types.py](../../../../scripts/audit_api_types.py)
   `FORBIDDEN_WIRE_FIELDS`: any `storage_uri`/`file_uri` on a **response**
   model fails the CI ratchet. Plus the exhaustive per-shape test
   [aidream/api/tests/test_no_storage_uri_on_wire.py](../../../../aidream/api/tests/test_no_storage_uri_on_wire.py)
   (covers nested + matrx-utils shapes CI's default scope skips), and the media-
   block test above. **Add a new client-facing file shape → add it to the test's
   `WIRE_SHAPES`.**
2. **Live-DB** —
   [scripts/validate_storage_uri_isolation.py](../../../../scripts/validate_storage_uri_isolation.py)
   (loud, non-blocking, in `release.sh`): screams if `authenticated`/`anon`
   regain `SELECT` **or** `UPDATE`/`INSERT` on `storage_uri`, or the realtime
   publication re-includes it. Green as of 2026-07-06.

## Hard-delete — the ONE purge primitive (no orphaned S3 objects)

A cloud file's bytes live in S3; its row + versions + permissions + share-links
live in Postgres. Hard-delete must remove **both**. The Postgres RPC
`hard_delete_file(p_file_id)` cascades the DB side and **returns the storage
URIs still to be purged** (`{main, versions}`, handed only to the service-role
backend caller — a JWT caller never sees them). The DB wrapper
`SyncEngine.db.hard_delete_file[_async]` does the DB half **and nothing else** —
so any code that calls it directly and forgets to delete the returned objects
strands them in S3 **forever** (the row is gone; nothing ever reconciles them).
This is the **C10 orphan-data leak**.

**The rule:** every hard-delete routes through the ONE primitive —
`SyncEngine.hard_delete_and_purge[_async](file_id, storage_uri)` — which
cascades the DB rows, purges the main object + every version + `purge["main"]`
(deduped), and invalidates the byte cache. **Never call
`db.hard_delete_file[_async]` directly.** Callers: `managed_delete[_async]`,
`FileService.hard_delete`, the matrx-ai `cloud_file` tool, and the pdf orphan-
cleanup all go through it.

**Guard (loud, non-blocking, in `release.sh`):**
[scripts/audit_hard_delete_purge.py](../../../../scripts/audit_hard_delete_purge.py)
AST-scans every `.hard_delete_file[_async](...)` call and fails on any outside
the primitive (allowlist: `sync_engine.py` + the wrapper's own `db.py`). This is
the second, screaming layer that keeps the leak extinct.

## Storage ⟷ DB reconciliation (the standing detector)

[scripts/reconcile_orphan_objects.py](../../../../scripts/reconcile_orphan_objects.py)
diffs the buckets against the DB in **both** directions. A healthy system trends
to zero on both; a non-zero number is a bug, not a chore.

- **ORPHAN** — an object no row claims. Costs money forever; nothing will ever
  reconcile it (the row that pointed at it is gone). This is what a hard-delete
  leak produces.
- **MISSING** — a row pointing at a **non-existent** object: a BROKEN FILE the
  user sees but cannot open. The worse direction.

**The rule that makes it safe: over-claim, always.** Under-claiming DELETES USER
DATA; over-claiming merely leaves an orphan behind. The claim set is derived
**empirically from the live DB** (every text/jsonb column scanned for bucket
references), never from memory — a new table that stores a storage reference and
isn't registered will get its objects called orphans.

**Two invariants that are easy to get catastrophically wrong:**
1. **Soft-deleted rows still own their bytes** — a trashed file is restorable.
   Filtering `deleted_at` out of the claim set purges the trash.
2. **Row-less-by-design prefixes exist** (`UNMANAGED_PREFIXES`). Image Studio
   (`staged-variants/`) writes renders with **no DB row** and finds them by S3
   **prefix listing**; ephemeral previews and legal-opinion blobs (derived keys,
   rows in a *separate* DB) do the same. Inside these prefixes "no row ⇒ dead"
   is FALSE. **Writing bytes that only a prefix-listing can find is an
   antipattern** — it makes storage unreconcilable, which is exactly how the C10
   leak stayed hidden. Every entry in that registry is a standing invitation to
   give the feature real rows.

Public/CDN objects are **held back by default** (`--include-public`): a public URL
is permanent and works with no row behind it, so it may be referenced from the CMS
(a separate database), the frontend, or an external site the script cannot see.
Private objects have no permanent URL — access requires a signed URL minted *from
the row* — so "no row" genuinely means unreachable.

## Change Log
- **2026-07-10** — C10 orphan-leak eradicated. `FileService.hard_delete` (and the
  matrx-ai `cloud_file` tool) called the raw DB fn and never purged S3 — orphaning
  the main object + every version. Collapsed all 4 hard-delete paths onto the ONE
  `SyncEngine.hard_delete_and_purge[_async]` primitive; added the boundary guard
  `scripts/audit_hard_delete_purge.py` + regression test. Live RPC contract
  verified unchanged (returns `{main, versions}` to service-role).
- **2026-07-06** — All 4 channels CLOSED. matrx-ai stream media-block leak fixed
  (9 sources + builder + validator + test). Migrations 0146+0147 applied to
  Matrx Main (FE verified clean first); isolation validator green.
- **2026-07-04** — Created. Introduced `FileRef`; stripped `storage_uri`/
  `file_uri` from every OUT shape (incl. 3 RAG/document models the static
  guard surfaced); added both guards; wrote staged migration 0146.
