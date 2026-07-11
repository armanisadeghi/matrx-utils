# code_context

Unified, single-file module (`code_context.py`) that produces LLM-ready code context from a directory. Supersedes `structured_fetcher`, `code_fetcher_6`, and `fetch_file_structure`.

## Class map

```
CodeContextConfig          # dataclass — base config.yaml → named preset → runtime overrides
FileDiscovery              # 7-layer filter: exact dir, word-boundary dir, dir allowlist,
                           #   exact file, word-boundary file, file allowlist, ext blacklist/whitelist
DirectoryTree              # ASCII tree: sparse | full | prune-empty modes
CodeExtractor              # reads one file; strips comments for 10+ language families;
                           #   update_contents() / refresh_contents() for programmatic use
SignatureExtractor          # extracts signatures — Python via AST (full types/defaults/returns),
  SignatureBlock            #   16 other languages via curated regex patterns
FunctionCallAnalyzer       # Python AST function-call graph (caller→callee, args, line numbers)
  FunctionCallGraph         #   with highlight/ignore lists and concise/detailed output
ASTAnalyzer                # Python-only structural analysis: class/method/function names + args
  ModuleAST / ClassInfo / FunctionInfo
CodeContextBuilder         # orchestrator: discovery → parallel file load → tree → assemble → save
  CodeContextResult        # returned by build(): combined_text, files, stats, extractors,
                           #   sig_blocks, ast_modules, call_graphs, to_json_structure()
```

## Four output modes (single `output_mode` knob)

| Mode | Content | ~Token cost |
|---|---|---|
| `tree_only` | directory tree, no file content | ~1% |
| `signatures` | tree + function/class/method signatures, no bodies | ~5–10% |
| `clean` | tree + full content, comments stripped | ~70–80% |
| `original` | tree + raw content, unmodified | 100% |

## Core flow

```python
from matrx_utils.code_context import CodeContextBuilder

builder = CodeContextBuilder(
    project_root="/path/to/project",
    subdirectory="src",                 # optional
    output_mode="signatures",           # "tree_only"|"signatures"|"clean"|"original"
    preset="python_only",              # optional: named preset from config.yaml
    overrides={
        "exclude_directories": {"add": ["scratch"], "remove": ["docs"]},
        "include_extensions":  {"add": [".py"]},        # whitelist mode
        "include_directories": {"add": ["src", "lib"]}, # dir allowlist
    },
    additional_files=["/abs/path/extra.py"],
    show_all_tree_directories=False,
    prune_empty_directories=True,
    prompt_prefix="Please review...",
    prompt_suffix="What needs fixing?",
    parallel_workers=8,                # threaded file loading
    call_graph=True,                   # optional: build Python call graphs
    call_graph_ignore=["print", "len"],
    call_graph_highlight=["my_func"],
)
result = builder.build()
builder.save(result)           # writes .txt + structure .json
builder.print_summary(result)

# Use result directly (no save needed)
print(result.combined_text)
structure = result.to_json_structure()  # JSON-serialisable dir tree
```

## Config

`config.yaml` (next to the module) holds defaults. Three-level merge priority:
1. `config.yaml` base
2. Named `preset` (if given) — stored in `config.yaml` under `presets:`
3. Runtime `overrides` dict — highest priority

All list fields support `{"add": [...], "remove": [...]}` patch operations; no full replacement needed.

**Eight filter fields:**
- `exclude_directories` / `exclude_directories_containing`
- `exclude_files` / `exclude_files_containing`
- `exclude_extensions`
- `include_extensions` — whitelist; overrides blacklist when non-empty
- `include_directories` — allowlist; only these dirs are traversed
- `include_files` — allowlist; only these filenames are kept

**Built-in presets** (add your own in `config.yaml`):
- `python_only` — `.py` files only, `signatures` mode
- `frontend` — `.ts/.tsx/.js/.jsx` only, `clean` mode
- `tree_overview` — tree only, all dirs shown, empty dirs pruned

## Outputs

| File | When |
|---|---|
| `<mode>_<timestamp>.txt` | `save_combined=True` (default) |
| `<mode>_<timestamp>_structure.json` | always alongside combined txt |
| `<stem>_<timestamp>.txt` per file | `save_individual=True` |

## Signature extraction language coverage

Python (AST — precise), TypeScript, JavaScript, Go, Rust, Java, Kotlin, Swift, C, C++, C#, Ruby, PHP, Lua, Scala, Dart — plus a fallback note for unsupported types.
