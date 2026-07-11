# Multi-Module README Generation — Next Level Task

**Status:** Not yet built. This document captures the design so it can be
implemented in a follow-up session. The core system (single-module generation)
must be working first — it is, as of Feb 2026.

**Prerequisite:** `utils/code_context/generate_module_readme.py` (complete).

---

## Goal

A single command that walks the entire project, finds all Python modules,
generates a `MODULE_README.md` for each, and handles large modules by
splitting them into a parent summary + child detail documents.

---

## Part 1 — Bulk Generation Script

**New file:** `utils/code_context/generate_all_readmes.py`

### What it does

1. Walk the project root (or a specified subtree)
2. Find all Python packages: directories containing `__init__.py`
3. For each package, check if it should be skipped (too shallow, excluded, etc.)
4. Run the generator (`generate_module_readme.py` logic) for each
5. Report: created / updated / skipped / errored

### CLI interface

```bash
python utils/code_context/generate_all_readmes.py [root] [options]

# Examples:
python utils/code_context/generate_all_readmes.py          # entire project
python utils/code_context/generate_all_readmes.py ai/      # subtree only
python utils/code_context/generate_all_readmes.py ai/ --dry-run
python utils/code_context/generate_all_readmes.py ai/ --skip-unchanged
```

Options:
- `root` — subtree to scan (default: project root)
- `--dry-run` — print what would be generated without writing
- `--skip-unchanged` — skip modules where no `.py` file is newer than the README
- `--char-budget N` — character threshold for splitting (default: 50000)
- `--exclude DIR` — directory names to skip (merged with config.yaml defaults)
- `--min-files N` — skip modules with fewer than N Python files (default: 2)

### Staleness detection

Compare the max `mtime` of all `.py` files in the module against the `mtime`
of `MODULE_README.md`. If the README is newer, skip.

```python
def is_stale(module_dir: Path, readme: Path) -> bool:
    if not readme.exists():
        return True
    readme_mtime = readme.stat().st_mtime
    return any(
        f.stat().st_mtime > readme_mtime
        for f in module_dir.rglob("*.py")
    )
```

---

## Part 2 — Intelligent Splitting (Parent/Child)

When a module's signatures output exceeds the character budget, the system
splits into a parent summary + per-subdirectory child documents.

### Threshold check

```python
CHAR_BUDGET = 50_000  # configurable via CLI

result = builder.build()  # output_mode="signatures"
if len(result.combined_text) > CHAR_BUDGET:
    generate_split_docs(module_dir, subdirs)
else:
    generate_single_doc(module_dir)
```

### Split structure

For a module like `ai/` that exceeds the budget:

```
ai/
├── MODULE_README.md          ← parent: summary + tree + links to children
├── tools/
│   └── MODULE_README.md      ← child: full detail for ai/tools
├── prompts/
│   └── MODULE_README.md      ← child: full detail for ai/prompts
└── ...
```

### Parent document structure

The parent `MODULE_README.md` gets a special `<!-- AUTO:children -->` section:

```markdown
## Sub-Modules

This module is split into sub-module READMEs due to size.

| Sub-module | Files | Summary |
|---|---|---|
| [ai/tools](tools/MODULE_README.md) | 39 | Tool execution system |
| [ai/prompts](prompts/MODULE_README.md) | 12 | Prompt and session management |
```

The parent also gets the full tree of the parent directory but only top-level
signatures (not recursing into sub-packages that have their own READMEs).

### Child document structure

Each child's `MODULE_README.md` gets a back-link in the `meta` section:

```markdown
| Parent module | [`ai/`](../MODULE_README.md) |
```

### Split algorithm

```python
def generate_split_docs(parent_dir: Path, char_budget: int) -> None:
    subdirs = [d for d in parent_dir.iterdir() if d.is_dir() and (d / "__init__.py").exists()]

    children: list[ChildInfo] = []
    for subdir in subdirs:
        rel = subdir.relative_to(PROJECT_ROOT)
        generate_module_readme(str(rel))  # recurse — child may itself split
        children.append(ChildInfo(path=subdir, file_count=count_py_files(subdir)))

    generate_parent_readme(parent_dir, children)
```

---

## Part 3 — Config

Add to `config.yaml`:

```yaml
# Multi-module generation settings
multi_module:
  char_budget: 50000          # signatures char count threshold for splitting
  min_files: 2                # skip modules with fewer Python files than this
  exclude_module_dirs:        # directory names to never generate READMEs for
    - "tests"
    - "migrations"
    - "tmp"
```

---

## Implementation Order

1. `generate_all_readmes.py` with dry-run and staleness detection (no splitting yet)
2. Validate on the full project — check which modules are generated, which skipped
3. Add the char budget check and splitting logic
4. Test on `ai/` (likely to exceed budget given its size)
5. Add the parent `<!-- AUTO:children -->` section and back-links

---

## Edge Cases to Handle

| Case | Handling |
|---|---|
| Module has no `.py` files (only subdirs) | Generate tree-only README or skip |
| Nested packages both exceed budget | Recurse — each level splits independently |
| README has human content from previous split | Preserve as always — AUTO blocks only |
| Module dir IS the project root | Use project name as title, no back-link |
| Circular symlinks | `rglob` with follow_symlinks=False |
