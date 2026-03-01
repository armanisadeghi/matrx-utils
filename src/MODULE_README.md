# `src` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src` |
| Last generated | 2026-02-28 14:46 |
| Output file | `src/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/matrx_utils/MODULE_README.md`](src/matrx_utils/MODULE_README.md) | last generated 2026-02-28 14:46 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 37 files across 10 directories.

```
src/
├── MODULE_README.md
├── matrx_utils/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── conf.py
│   ├── data_handling/
│   │   ├── __init__.py
│   │   ├── data_transformer.py
│   │   ├── utils.py
│   │   ├── validation/
│   │   │   ├── __init__.py
│   │   │   ├── errors.py
│   │   │   ├── validators.py
│   ├── fancy_prints/
│   │   ├── __init__.py
│   │   ├── colors.py
│   │   ├── fancy_prints.py
│   │   ├── matrx_print_logger.py
│   │   ├── redaction.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── matrx_json_converter.py
│   ├── field_processing/
│   │   ├── __init__.py
│   │   ├── dataclass_generator.py
│   │   ├── field_handler.py
│   ├── file_handling/
│   │   ├── __init__.py
│   │   ├── base_handler.py
│   │   ├── batch_handler.py
│   │   ├── file_handler.py
│   │   ├── file_manager.py
│   │   ├── local_files.py
│   │   ├── specific_handlers/
│   │   │   ├── __init__.py
│   │   │   ├── code_handler.py
│   │   │   ├── html_handler.py
│   │   │   ├── image_handler.py
│   │   │   ├── json_handler.py
│   │   │   ├── markdown_handler.py
│   │   │   ├── text_handler.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── clear_terminal.py
│   │   ├── get_dir_structure.py
│   │   ├── testing.py
# excluded: 6 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Submodule: src/matrx_utils/  [35 files — full detail in src/matrx_utils/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** PIL, inflect, matrx_utils, psycopg2, requests
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
