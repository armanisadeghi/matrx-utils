# MODULE_README Generator — Roadmap

This document tracks what has been built, what is working, and what remains.
It is the single source of truth for planned improvements to the auto-documentation system.

---

## What is built and working today

| Feature | Where | Status |
|---------|-------|--------|
| AST-based Python signature extraction (functions, classes, methods) | `code_context.py` | ✅ |
| Pydantic field extraction with types and defaults | `code_context.py` | ✅ |
| Module-level constants and type aliases (`Literal`, `StrEnum`, `ALL_CAPS`) | `code_context.py` | ✅ |
| Large collection constants collapsed to `[N items]` / `{N keys}` (120-char threshold) | `code_context.py` | ✅ |
| Private constant filtering (`_prefixed` names excluded) | `code_context.py` | ✅ |
| Surgical AUTO-block merging (human content never overwritten) | `generate_module_readme.py` | ✅ |
| `__init__.py` included in signatures | `config.yaml` | ✅ |
| Excluded file count footer in tree (`# excluded: 5 .md`) | `code_context.py` / `generate_module_readme.py` | ✅ |
| Directory tree with `MODULE_README.md` files always visible | `generate_module_readme.py` | ✅ |
| Upstream callers table (who calls this module's entry points) | `generate_module_readme.py` | ✅ |
| External package dependencies (third-party only, stdlib filtered) | `generate_module_readme.py` | ✅ |
| Internal module dependencies (cross-module project imports) | `generate_module_readme.py` | ✅ |
| Relative import filtering in dependency scanner | `generate_module_readme.py` | ✅ |
| Child README detection — collapses covered submodules in signatures | `generate_module_readme.py` | ✅ |
| Child README links in meta section with last-generated timestamps | `generate_module_readme.py` | ✅ |
| Staleness check — directory mtime used (catches additions/deletions too) | `generate_module_readme.py` | ✅ |
| Minute-granularity staleness comparison (no false positives from sub-minute runs) | `generate_module_readme.py` | ✅ |
| `<!-- AUTO:config -->` block — embedded JSON config in every README | `generate_module_readme.py` | ✅ |
| Auto-refresh stale children using embedded config when parent runs | `generate_module_readme.py` | ✅ |
| `--cascade` flag — auto-discovers qualifying subdirs, generates children first | `generate_module_readme.py` | ✅ |
| `--cascade-min-files N` — threshold for cascade discovery (default: 5) | `generate_module_readme.py` | ✅ |
| `--cascade-child-mode` — signature mode for auto-generated children | `generate_module_readme.py` | ✅ |
| Call graph (function-level, scoped, noise-filtered) | `generate_module_readme.py` | ✅ |
| `--root` flag for running against other projects | `generate_readme.py` | ✅ |
| Auto-discovery of upstream callers — no `ENTRY_POINTS` config needed on first run | `generate_module_readme.py` | ✅ |
| `[]` disables callers; `None` auto-discovers; `["fn"]` pins specific names | `generate_readme.py` | ✅ |
| Call graph auto-excludes files in covered submodules (those with child READMEs) | `generate_module_readme.py` | ✅ |
| `INCLUDE_CALL_GRAPH` flag separates "run call graph" from "scope" in trigger script | `generate_readme.py` | ✅ |
| `CASCADE` / `CASCADE_MIN_FILES` / `CASCADE_CHILD_MODE` settings in trigger script | `generate_readme.py` | ✅ |
| Cascade is fully recursive (depth-first) — handles arbitrarily deep trees | `generate_module_readme.py` | ✅ |
| `FORCE_REFRESH_CHILDREN` — unconditionally regenerate all child READMEs | `generate_readme.py` | ✅ |
| `CALL_GRAPH_EXCLUDE` — drop dirs from call graph only; tree/signatures unaffected | `generate_readme.py` | ✅ |
| Bare-name segment matching in `CALL_GRAPH_EXCLUDE` (e.g. `"tests"` catches all test dirs) | `generate_module_readme.py` | ✅ |

---

## Remaining tasks

### Priority 1 — High value, straightforward

#### ~~1.1 Call graph filtering for parent modules with child READMEs~~ ✅

Implemented. `_build_call_graph` now accepts `child_readmes` and derives a scope
limited to files that are NOT inside any covered subdirectory. Covered submodule
names are listed in the README's call graph note so it's clear what was excluded.

---

#### 1.2 CLI `--entry-points` support in `generate_module_readme.py`

**Problem:** The upstream callers section only appears when running via `generate_readme.py`
(which has `ENTRY_POINTS` configured). The direct CLI has no way to pass entry points,
so any README generated via CLI will never have a callers section — including children
auto-refreshed from their embedded config.

**Fix:** Add `--entry-points FUNC1,FUNC2,...` argument to `main()`. Wire to the existing
`entry_points` parameter in `run()`. The embedded `AUTO:config` block already stores
`entry_points` correctly — this just closes the CLI gap.

**Effort:** ~10 lines.

---

#### ~~1.3 Cascade support in `generate_readme.py` trigger script~~ ✅

Implemented. `CASCADE`, `CASCADE_MIN_FILES`, `CASCADE_CHILD_MODE` added to settings.
Script calls `run_cascade()` when `CASCADE=True`, `run()` otherwise. All other
settings (`ENTRY_POINTS`, `CALL_GRAPH_EXCLUDE`, `FORCE_REFRESH_CHILDREN`, etc.)
are fully threaded through both paths. No CLI knowledge required.

---

#### 1.4 Auto-detect oversized modules and suggest or trigger cascade

**Problem:** When a module has many Python files (e.g. 50+), the generated README
becomes 5,000–10,000 lines — too large to be useful. Currently nothing detects this
and the user has no warning. They have to manually realize the output is too large
and know to use `--cascade`.

**Fix (two parts):**
1. After generating, if the output exceeds a threshold (e.g. 500 lines), print a warning:
   `⚠ README is N lines — consider running with CASCADE=True to auto-split by submodule.`
2. Optionally: if a `CASCADE_AUTO_THRESHOLD` is set (Python file count, e.g. 30),
   automatically switch to cascade mode instead of generating a single giant file.

**Effort:** ~20 lines. Part 1 (warning only) is ~5 lines.

---

### Priority 2 — Quality improvements

#### 2.1 Smarter dependency deduplication for internal modules

**Problem:** The internal module list can show both `seo.utils` and `seo.utils.meta_calculators`
when multiple files import from the same package at different depths.

**Fix:** After collecting all internal module strings, collapse any path that is a strict
prefix of another already-present path. Truncate unknown-depth paths to 2 segments.

**Effort:** ~15 lines in `_build_dependencies()`.

---

#### 2.2 Exclude `tests/` subdirectories from cascade by default

**Problem:** Cascade picks up `tests/` subdirectories (as seen with `ai/tests/`). Test
files have fundamentally different value than production code and shouldn't be
auto-documented the same way.

**Fix:** Skip directories named `tests/` or `test/` in `run_cascade()` by default.
Add `--cascade-include-tests` flag to opt back in.

**Effort:** ~5 lines in `run_cascade()`.

---

### Priority 3 — Nice to have

#### 3.1 Thread `project_root` explicitly through `run()` and `run_cascade()`

**Problem:** Both functions rely on the module-level `PROJECT_ROOT` global, which is
patched by `generate_readme.py` but not by the CLI `main()`. This makes cross-project
`--cascade` unreliable from the CLI and makes the functions hard to unit-test.

**Fix:** Add `project_root: Path | None = None` parameter to `run()` and `run_cascade()`,
defaulting to the module global. No logic changes — just threading the value.

**Effort:** Medium refactor (~50 lines touched, zero logic changes).

---

#### 3.2 Machine-readable manifest

**Problem:** No easy programmatic way to know which directories have MODULE_README.md
files and when they were last generated (useful for CI staleness checks).

**Fix:** Optionally write `.module_readme_manifest.json` to project root after any run,
listing all known READMEs with subdirectory, last-generated timestamp, and stale status.

**Effort:** ~30 lines.

---

#### 3.3 CI / GitHub Actions integration guide

A doc or example workflow that runs the cascade generator on PRs and fails if any
child README is stale. No code changes — documentation only.

---

## Non-goals (deliberately excluded)

| Item | Reason |
|------|--------|
| Docstring extraction | Violates the project's "no docstrings" standard. Signatures + Pydantic fields carry the same contract information. |
| TypeScript / frontend module READMEs | Possible (extractor handles TS/JS), but Python is the priority. Revisit if needed. |
| Version pinning or changelogs in READMEs | Out of scope for a code context tool. |
