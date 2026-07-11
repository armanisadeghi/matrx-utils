# matrx-utils

Foundation utilities for the Matrx ecosystem — cloud file handling (AWS S3, Supabase Storage, local/server filesystems), a pluggable settings + request-context layer, and a set of developer helpers (fancy printing, data transforms, field-processing, code analysis).

`matrx-utils` is the bottom of the Matrx dependency graph. It has **no sibling dependencies**. Everything else (`matrx-connect`, `matrx-orm`, `matrx-graph`, `matrx-scraper`, `matrx-ai`) depends on it, directly or transitively.

## Install

```bash
pip install matrx-utils
```

Python 3.13+ required.

## What's in the box

| Module | What it does |
|---|---|
| `matrx_utils.conf` | `configure_settings(obj)` + a lazy `settings` proxy that falls back to env vars |
| `matrx_utils.ctx` | `UserContext` protocol, `SimpleUserContext`, `configure_context(getter)`, `get_active_context()` |
| `matrx_utils.fancy_prints` | `vcprint`, `vclist`, `print_link`, `MatrixPrintLog`, `to_matrx_json` |
| `matrx_utils.data_handling` | `DataTransformer`, URL and value validators |
| `matrx_utils.file_handling` | `FileManager`, `FileHandler`, `BatchHandler`, `open_any_file` |
| `matrx_utils.file_handling.cloud_sync` | `S3Backend`, `SupabaseBackend`, `ServerBackend`, `CloudSyncConfig`, `SyncEngine` + permissions and versioning |
| `matrx_utils.field_processing` | `camel_to_snake`, `process_field_definitions`, `generate_complete_code` |
| `matrx_utils.code_context`, `matrx_utils.package_analysis`, `matrx_utils.react_analysis` | Developer utilities for scanning codebases |

## Usage — standalone

Out of the box, `matrx-utils` reads its configuration from environment variables via a lazy `settings` proxy, and returns a minimal `SimpleUserContext` when no request context is available:

```python
from matrx_utils import vcprint, settings
from matrx_utils.file_handling.cloud_sync import SupabaseBackend

vcprint("hello")
vcprint(settings.SUPABASE_URL)           # read from env
backend = SupabaseBackend()              # credentials resolved from settings
backend.write("reports/today.json", b"{}")
```

## Usage — inside a host application

A parent app (like aidream) can inject its own settings object and request-context resolver so every downstream helper picks up the right user/project/emitter automatically:

```python
from matrx_utils import configure_settings, configure_context
from matrx_connect import try_get_app_context  # optional, only if you use matrx-connect
from myapp.settings import settings

configure_settings(settings)
configure_context(try_get_app_context)
```

After `configure_context(...)`, any code that calls `get_active_context()` inside a request will get the caller's `UserContext` without that code having to accept it as a parameter. This is the "capability-within, injection-without" pattern that the other Matrx packages follow.

## Standalone-friendliness

This package is designed to work with zero Matrx siblings present. It references `matrx-connect` in exactly one place — the PDF handler — and that import is **lazy with a dict fallback**, so `pip install matrx-utils` followed by `import matrx_utils` works in any Python project.

## Contributing

See [CLAUDE.md](CLAUDE.md) for package-specific rules (import rules, configuration pattern, known issues). This package lives in the aidream monorepo at [github.com/AI-Matrix-Engine/aidream-current](https://github.com/AI-Matrix-Engine/aidream-current/tree/main/packages/matrx-utils).

## License

MIT.
