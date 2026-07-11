# CLAUDE.md — matrx-utils

> **Operating Principle: Build the platform, not the artifact.** Every task is a probe that exposes a missing capability — build it, then consume it. Code that only serves one artifact is forbidden. Full doctrine: [/PRINCIPLES.md](../../PRINCIPLES.md).

**Package:** `matrx-utils` (PyPI) — Python 3.13+ — currently v1.0.20
**Role in the graph:** **Foundation.** Nothing else in the Matrx family may depend below this; this package may not depend on any sibling.

---

## Read this first

`matrx-utils` is the bottom of the Matrx dependency graph. It is `pip install`ed into projects that know nothing about aidream, matrx-orm, matrx-connect, or any other sibling. **It MUST NOT import from aidream or any other `matrx-*` package at module top-level.**

If you catch yourself writing `from matrx_connect import …` at the top of a file in this package, stop. That import belongs behind a `configure_*` injection point, a lazy import inside a function body, or a `try / except ImportError` with a fallback.

> Historic violation — already fixed: the legacy `matrx_utils/file_handling/specific_handlers/pdf_handler.py` used to top-level-import `from matrx_connect.context.events import InfoPayload`. As of Stage 2 the PDF subsystem lives in `specific_handlers/pdf/` and `pdf_handler.py` is a re-export shim; the `InfoPayload` lookup happens inside `pdf/internal.py::build_info_payload` behind a function-local `try / except ImportError` with a plain-dict fallback. **Do not regress this pattern** when adding new optional integrations under the `pdf/` subpackage.

---

## What this package provides

- **Settings / config registry** (`matrx_utils.conf`): `configure_settings(obj)`, `settings` — a lazy proxy that falls back to env vars.
- **Context protocol** (`matrx_utils.ctx`): `UserContext`, `SimpleUserContext`, `configure_context(getter)`, `get_active_context()`, `set_manual_context(...)`.
- **Fancy printing** (`matrx_utils.fancy_prints`): `vcprint`, `vclist`, `print_link`, `MatrixPrintLog`, `to_matrx_json`.
- **Data handling** (`matrx_utils.data_handling`): `DataTransformer`, validators, URL tools.
- **File handling** (`matrx_utils.file_handling`): `FileManager`, `FileHandler`, `BatchHandler`, `open_any_file`.
- **Image variant presets** (`matrx_utils.file_handling`): `PODCAST_VARIANTS`, `SOCIAL_VARIANTS`, `WEB_VARIANTS`, `EMAIL_VARIANTS`, `LOGO_VARIANTS`, `AVATAR_VARIANTS`, `FAVICON_VARIANTS`, `SOCIAL_BASELINE`, plus the `PRESETS` registry and the composer helpers `compose_preset(name, include_baseline, extra_variants)`, `get_preset(name)`, `list_preset_names()`. Hosts consume these to render the same variant set everywhere — every public asset gets the social baseline (og + thumbnail + tiny) appended automatically unless explicitly disabled.
- **Cloud storage** (`matrx_utils.file_handling.cloud_sync`): `S3Backend`, `SupabaseBackend`, `ServerBackend`, `CloudSyncConfig`, `SyncEngine`, permissions + versioning.
- **Centralized URL minting** — `SyncEngine.build_urls_for_record(_async)` is the **single source of truth** for the `{url, cdn_url, signed_url, download_url}` contract a file response carries. `managed_write_async` and `replace_file_async` populate the same shape on every `SyncResult`. Callers MUST consume `result.url` / `result.cdn_url` directly and never re-mint via `_router.get_url_async(...)`. The backends accept `response_content_disposition` and `response_content_type` kwargs so attachment-URLs flow through to S3 unchanged.
- **Field / schema processing** (`matrx_utils.field_processing`): `camel_to_snake`, `process_field_definitions`, `generate_complete_code`.
- **Code analysis tools** (`matrx_utils.code_context`, `matrx_utils.package_analysis`, `matrx_utils.react_analysis`): developer utilities for scanning codebases.
- **Local dev utils** (`matrx_utils.local_dev_utils`): module-readme generation, import checks, package usage scanning. These are explicitly for this monorepo's maintainers and are allowed to have some monorepo-aware behavior; keep them isolated.
- **Canonical primitives — the single way to do four ubiquitous things.** These exist because a repo scan found each reimplemented 100–390× with no shared helper; **never hand-roll these again — import from the root.**
  - `matrx_utils.hashing` — `stable_hash` / `stable_json` (deterministic content/idempotency/cache keys), `hash_text` / `hash_bytes` / `hash_chunks`. `stable_json` is byte-faithful to the legacy `cloud_sync/idempotency.py` form, so migrating existing keys is a no-op.
  - `matrx_utils.ids` — `new_id` (bare or `new_id("req")`-prefixed), `new_uuid`, `new_hex`. One place to swap uuid4→uuid7 later.
  - `matrx_utils.timeutils` — `utcnow` (aware, never naive), `parse_iso` (always aware UTC, tolerates `Z`), `to_iso`. Kills the scattered `.replace("Z","+00:00")` workaround.
  - `matrx_utils.http_client` — `async_client` (real timeout + `trust_env` + pooling), `request_with_retries` (429/5xx + transport-error backoff, honours `Retry-After`), `fetch_json`. **🚫 NOT for user media URLs** — those go through `FileManager.resolve_media_async` (file-contract rule 1).
  - `matrx_utils.rendezvous` — `Rendezvous` / the `rendezvous` singleton: an **order-independent meeting point** between a producer that commits a keyed resource and a consumer that must act once it's real. Kills the "poll sees the still-queued row → UPDATE hits zero committed rows" race class. `announce(kind, id)` on commit (fired generically from `Session.flush`); `on_present(kind, id, do=..., verify=..., ttl=...)` any time — cache-hit-or-hold, with a **committed-read DB fallback** that runs-with-a-leak-warning or drops-with-a-critical-alarm. **Never hand-roll a "wait for the row before I touch it" poll again.** Contract: [`RENDEZVOUS_FEATURE.md`](matrx_utils/RENDEZVOUS_FEATURE.md).
- **Secure RNG** (`matrx_utils.secure_random`) + **quality math** (`matrx_utils.quality_engine`) + **host identity** (`matrx_utils.runtime_env`): three more single-purpose primitives — see their module docstrings.

The public API is the union of what `matrx_utils/__init__.py` re-exports (~140 symbols). Keep that surface stable — external projects depend on it.

---

## The configuration pattern (canonical)

This package is where the "capability-within, injection-without" pattern is most clearly established. Other packages copy it.

```python
# In a host application (aidream, or any third-party project):
from matrx_utils import configure_settings, configure_context

configure_settings(my_settings_object)     # any object with attribute access
configure_context(lambda: my_request_ctx)  # any callable returning a UserContext-shaped object
```

Inside this package:

- **Never** read `os.environ["…"]` directly outside `conf.py`. Route through `settings`, which already falls back to env vars.
- **Never** reach into a specific host's context shape. The `UserContext` protocol defines what we need; if you need more, extend the protocol and provide defaults.
- The `CloudSyncConfig` / `SupabaseBackend` / `S3Backend` classes must accept explicit credentials in their constructors and only fall back to `settings` if the caller didn't pass them in. See `file_handling/cloud_sync/` for the pattern.

---

## Dependency rules specific to this package

- ❌ No `from matrx_ai import …`
- ❌ No `from matrx_orm import …`
- ❌ No `from matrx_connect import …` at module top level (lazy-import inside functions only, and only when the capability is genuinely optional)
- ❌ No `from matrx_graph import …`, `from matrx_scraper import …`
- ❌ No `from aidream import …`, no root-module imports (`common`, `config`, `api_management`, etc.)
- ✅ External libs: boto3, supabase, pydantic, pandas, pillow, httpx, requests, pyyaml, dotenv, pypdfium2, pytesseract, python-pptx.

---

## Python standards (same as root)

- Full type hints. Pydantic for data models where structured validation is needed.
- No docstrings except on genuinely public API functions, where a one-line summary is useful for IDE tooltips.
- Explicit exception handling. Don't swallow errors — re-raise or surface via an emitter.
- Hot paths (cloud sync, batch file handling, printing in tight loops) must stay allocation-light.

---

## Testing this package in isolation

```bash
uv run pytest packages/matrx-utils/tests
```

The tests MUST pass without any sibling package installed beyond what `pyproject.toml` declares. If a test needs `matrx-connect` to run, mark it with a skip guard that checks for the import.

---

## Known issues (see root PACKAGES_MIGRATION_PLAN.md for context)

1. ~~`pdf_handler.py` hard-imports `matrx_connect`~~ — **resolved in Stage 2 PDF refactor**. `pdf_handler.py` is now a re-export shim; the optional matrx-connect lookup lives behind a function-local try/except in `pdf/internal.py`.
2. **`local_dev_utils` has some hardcoded paths** (e.g. `/Users/armanisadeghi/code/aidream/...` in `generate_readme.py`, monorepo-root assumptions in `package_usage_scanner.py`). These tools are for this repo's maintainers; keep them behind explicit CLI args rather than constants.
