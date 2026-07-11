# `utils.react_analysis` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `utils/react_analysis` |
| Last generated | 2026-02-28 14:52 |
| Output file | `utils/react_analysis/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py utils/react_analysis --mode signatures
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

> Auto-generated. 14 files across 1 directories.

```
utils/react_analysis/
├── MODULE_README.md
├── __init__.py
├── analyze_react_imports.py
├── collision_summary.py
├── extract_all_exports.py
├── extract_exports.py
├── find_invalid_imports.py
├── generate_full_index_with_files.py
├── generate_full_index_with_structure.py
├── generate_react_index.py
├── get_and_analyze.py
├── name_collision_analyer.py
├── utils.py
├── z_configs.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: utils/react_analysis/__init__.py  [python]



---
Filepath: utils/react_analysis/generate_react_index.py  [python]

  def generate_index_ts(directory_structure, analysis_results, root_directory, output_file = 'index-gen.ts')
  def get_import_path(file_path)


---
Filepath: utils/react_analysis/extract_all_exports.py  [python]

  def extract_and_analyze_all_exports(directory_structure, config)
  def traverse_structure(structure, current_path)


---
Filepath: utils/react_analysis/analyze_react_imports.py  [python]

  def analyze_imports(file_path, alias_map, config)
  def analyze_imports_from_directory_structure(directory_structure, config)
  def traverse_structure(structure, current_path)


---
Filepath: utils/react_analysis/utils.py  [python]

  def get_supported_extensions(config)
  def read_file_content(file_path, config, remove_comments = False)
  def remove_comments_from_content(content, file_extension)
  def file_extension_supported(file_path, config)
  def normalize_path(path)
  def resolve_alias(alias_path, config)
  def should_process_file(file_path, config)
  def load_json(file_path)
  def save_structure_to_json(structure, output_file)
  def save_combined_structure_to_txt(combined_structure, output_file)
  def write_recursive(structure, level = 0)


---
Filepath: utils/react_analysis/find_invalid_imports.py  [python]

  def find_invalid_imports(combined_structure, config)
  def _normalize(path)
  def collect_valid_paths(sub_structure)
  def check_imports(sub_structure)
  def validate_imports(import_list, import_type)


---
Filepath: utils/react_analysis/name_collision_analyer.py  [python]

  def find_name_collisions(combined_structure)
  def analyze_file_collisions(combined_structure, name_collisions)
  def traverse_structure(sub_structure)
  def traverse_structure(sub_structure)
  def check_imports(import_list)


---
Filepath: utils/react_analysis/generate_full_index_with_files.py  [python]

  def save_summary_to_txt(structure, output_file)
  def save_combined_structure(export_analysis, import_analysis, config)
  def write_import_list(import_type, imports)


---
Filepath: utils/react_analysis/extract_exports.py  [python]

  def preprocess_content(content)
  def analyze_react_exports(file_path, config)


---
Filepath: utils/react_analysis/generate_full_index_with_structure.py  [python]

  def create_combined_structure(config, directory_structure, export_analysis, import_analysis)
  def add_structure_recursive(current_dir, path)


---
Filepath: utils/react_analysis/z_configs.py  [python]

  def get_default_configs_with_overrides(overrides = None)


---
Filepath: utils/react_analysis/get_and_analyze.py  [python]

  class ReactAnalysisConfig:
      def to_dict(self) -> dict[str, Any]
  def _build_directory_structure(config: dict) -> dict
  def get_full_index_structure(config: dict, save_json: bool = False, save_text: bool = False) -> dict


---
Filepath: utils/react_analysis/collision_summary.py  [python]

  def summarize_collisions(name_collisions)
  def summarize_file_collisions(page_collisions)
  def get_full_collision_summary(combined_structure, config, verbose = True)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**Internal modules:** utils.code_context
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "utils/react_analysis",
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
