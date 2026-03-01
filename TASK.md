# TASK: Replace LazySettings with pydantic-settings

**Owner:** Arman  
**Priority:** High  
**Affects:** All 17+ AI Matrx projects

---

## Context

All AI Matrx Python projects are being standardized on **pydantic-settings** as the single configuration system. Every project now has a `app/config.py` that defines a typed, validated `Settings` class with nested sub-models (`primary_db`, `supabase`, `llm`, `log`, `dirs`, etc.).

The current `matrx_utils.conf.LazySettings` is a parallel, incompatible config system that reads raw `os.environ`. This creates a two-system problem: pydantic-settings reads `.env` itself and exposes typed values; `LazySettings` only sees `os.environ`, which pydantic-settings deliberately does not populate.

The result: every project that uses matrx_utils currently requires a bootstrap shim (`app/bootstrap.py`) to manually bridge the two systems. This is a workaround, not the solution.

**Goal:** Eliminate `LazySettings` entirely. Make `matrx_utils` consume config the same way all other Matrx projects do.

---

## The Standard Pattern (enforce across all projects)

Every Python project in the Matrx ecosystem uses this pattern in `app/config.py`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr, Field
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "development"
    debug: bool = False
    matrx_python_root: Path = Path(__file__).resolve().parent.parent
    # ... sub-models for db, supabase, llm, log, dirs ...

@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
```

Usage everywhere:

```python
from app.config import settings

settings.matrx_python_root   # Path
settings.log.level           # "INFO"
settings.llm.openai_api_key.get_secret_value()
```

`matrx_utils` should consume config the same way — not invent its own system.

---

## What Needs to Change in matrx-utils

### 1. Delete `src/matrx_utils/conf.py`

The entire file. `LazySettings`, `configure_settings`, `NotConfiguredError` — all of it goes away. There is no replacement inside matrx-utils; the calling application owns its config.

### 2. Change `FileHandler` to accept `base_dir` explicitly

**Current** (`file_handler.py` line 26):
```python
self.base_dir = Path(settings.BASE_DIR)   # reads from LazySettings
```

**New:**
```python
def __init__(self, app_name: str, base_dir: Path, ...):
    self.base_dir = base_dir
```

`base_dir` is now a required parameter passed in by the calling application. The application knows its own base dir — it should pass it in, not have matrx-utils guess it from an env var.

### 3. Update `FileManager` the same way

`file_manager.py` also instantiates `FileHandler`. It should accept `base_dir` as a constructor argument and forward it.

### 4. Remove the `dotenv` dependency from `pyproject.toml`

`matrx_utils` should not load `.env` files — that is the application's responsibility via pydantic-settings.

```toml
# Remove this line from pyproject.toml:
"dotenv>=0.9.9",
```

Search for any `load_dotenv()` calls in the codebase and remove them.

### 5. Remove any remaining `os.getenv` / `os.environ` config reads

Search for `os.getenv`, `os.environ.get`, `os.environ[` in the source. Any that are reading application-level config (API keys, DB credentials, paths, etc.) need to be removed. The application passes those values in — matrx-utils does not read them directly.

```bash
rg "os\.getenv|os\.environ" src/matrx_utils/
```

Each hit is either:
- **Legitimate** (e.g. checking `PATH`, system vars) — keep it
- **App config** (e.g. `BASE_DIR`, `API_KEY`) — remove it; accept as parameter instead

### 6. Update any matrx-utils scripts / tooling entry points

Any standalone scripts in matrx-utils that previously called `configure_settings()` should instead instantiate settings directly:

```python
# Before
from matrx_utils.conf import configure_settings
configure_settings(my_obj)

# After — just pass what you need as arguments
file_handler = FileHandler(app_name="my_tool", base_dir=Path("/my/project"))
```

---

## What the Calling Application Does (no change needed after this)

Once matrx-utils is updated, the application's `app/config.py` and `app/bootstrap.py` shim are **deleted**. The application simply does:

```python
from app.config import settings
from matrx_utils.file_handling import FileHandler

handler = FileHandler(app_name="my_app", base_dir=settings.matrx_python_root)
```

Clean, explicit, no magic.

---

## Migration Checklist

- [ ] Remove `src/matrx_utils/conf.py`
- [ ] Update `FileHandler.__init__` — `base_dir: Path` required param, remove `settings.BASE_DIR`
- [ ] Update `FileManager` — pass `base_dir` through
- [ ] Remove `dotenv` from `pyproject.toml` dependencies
- [ ] Remove all `load_dotenv()` calls
- [ ] Audit and remove all `os.getenv` / `os.environ` reads for app-level config
- [ ] Update any internal scripts/tooling that used `configure_settings()`
- [ ] Search for all imports of `matrx_utils.conf` across all 17 projects and update them
- [ ] Bump version (breaking change — minor or major depending on semver policy)
- [ ] Update all 17 project `app/bootstrap.py` shims — delete them once the new version is deployed
- [ ] Verify `generate.py` in each project still works with the new explicit `base_dir` parameter

---

## Files to Audit in matrx-utils Source

```bash
# Find everything that touches conf or LazySettings
rg "from matrx_utils.conf|from matrx_utils import.*settings|configure_settings|LazySettings|BASE_DIR" src/

# Find env var reads
rg "os\.getenv|os\.environ" src/matrx_utils/

# Find dotenv usage
rg "load_dotenv|from dotenv|import dotenv" src/
```

---

## Version Bump

This is a **breaking change**. Any project using `configure_settings()` or `from matrx_utils.conf import settings` will break on upgrade.

Recommended approach:
1. Bump to `2.0.0`
2. Announce the change with a migration guide (this document serves as the guide)
3. Update all 17 projects in a single coordinated PR batch
