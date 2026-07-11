# `src.matrx_utils` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_utils` |
| Last generated | 2026-02-28 14:46 |
| Output file | `src/matrx_utils/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/matrx_utils/data_handling/MODULE_README.md`](src/matrx_utils/data_handling/MODULE_README.md) | last generated 2026-02-28 14:46 |
| [`src/matrx_utils/fancy_prints/MODULE_README.md`](src/matrx_utils/fancy_prints/MODULE_README.md) | last generated 2026-02-28 14:46 |
| [`src/matrx_utils/file_handling/MODULE_README.md`](src/matrx_utils/file_handling/MODULE_README.md) | last generated 2026-02-28 14:46 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_utils --mode signatures
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

> Auto-generated. 39 files across 9 directories.

```
src/matrx_utils/
├── MODULE_README.md
├── __init__.py
├── conf.py
├── data_handling/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── data_transformer.py
│   ├── utils.py
│   ├── validation/
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── validators.py
├── fancy_prints/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── colors.py
│   ├── fancy_prints.py
│   ├── matrx_print_logger.py
│   ├── redaction.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── matrx_json_converter.py
├── field_processing/
│   ├── __init__.py
│   ├── dataclass_generator.py
│   ├── field_handler.py
├── file_handling/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── base_handler.py
│   ├── batch_handler.py
│   ├── file_handler.py
│   ├── file_manager.py
│   ├── local_files.py
│   ├── specific_handlers/
│   │   ├── __init__.py
│   │   ├── code_handler.py
│   │   ├── html_handler.py
│   │   ├── image_handler.py
│   │   ├── json_handler.py
│   │   ├── markdown_handler.py
│   │   ├── text_handler.py
├── utils/
│   ├── __init__.py
│   ├── clear_terminal.py
│   ├── get_dir_structure.py
│   ├── testing.py
# excluded: 5 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: src/matrx_utils/__init__.py  [python]




---
Filepath: src/matrx_utils/conf.py  [python]

  class NotConfiguredError(Exception):
  class LazySettings:
      def __init__(self, env_first = False)
      def _ensure_configured(self)
      def _load_env_cache(self)
      def _get_env_with_fallback(self, name)
      def _convert_to_bool(self, value)
      def __getattr__(self, name)
      def reset_env_variables(self)
      def list_settings(self)
      def list_settings_redacted(self)
      def set_env_setting(self, name, value)
      def get_env_setting(self, name)
      def list_env_settings(self)
  def configure_settings(settings_object, env_first = False, verbose = False)



---
Submodule: src/matrx_utils/fancy_prints/  [7 files — full detail in src/matrx_utils/fancy_prints/MODULE_README.md]

---
Submodule: src/matrx_utils/data_handling/  [6 files — full detail in src/matrx_utils/data_handling/MODULE_README.md]

---
Submodule: src/matrx_utils/file_handling/  [13 files — full detail in src/matrx_utils/file_handling/MODULE_README.md]

---
Filepath: src/matrx_utils/utils/__init__.py  [python]




---
Filepath: src/matrx_utils/utils/get_dir_structure.py  [python]

  class Settings:
  def generate_directory_structure(root_dir, ignore_dirs = None, include_dirs = None, ignore_files = None, include_files = None, ignore_extensions = None, include_extensions = None, include_files_override = True, include_text_output = False, text_output_file = None, project_root = None)
  def prune_empty_directories(directory_structure)
  def save_structure_to_json(structure, output_file)
  def generate_and_save_directory_structure(config)
  def has_files_or_subdirectories(d)
  def prune(d)



---
Filepath: src/matrx_utils/utils/clear_terminal.py  [python]

  def clear_terminal()



---
Filepath: src/matrx_utils/utils/testing.py  [python]

  def cleanup_async_resources()
  def async_test_wrapper(async_test_func, *args, **kwargs)



---
Filepath: src/matrx_utils/field_processing/__init__.py  [python]




---
Filepath: src/matrx_utils/field_processing/dataclass_generator.py  [python]

  SAMPLE_DATA_TYPE_TO_VALUE_MAP = {str: 'This is a string', int: 123, bool: True, list: ['a', 'b'], dict: {'a': 'b'}}
  def to_snake_case(name: str) -> str
  def get_type_str(field_spec: Dict[str, Any]) -> str
  def needs_field_factory(default_value: Any) -> bool
  def generate_dataclass_code(class_name: str, fields_spec: Dict[str, Dict[str, Any]]) -> str
  def generate_build_function_code(class_name: str) -> str
  def generate_build_function_code_from_object(class_name: str) -> str
  def generate_build_function_code_from_batch_objects(class_name: str) -> str
  def format_field_definitions(fields_spec: Dict[str, Dict[str, Any]]) -> str
  def format_field_map(field_map: Dict[str, str]) -> str
  def generate_test_block(class_name: str, fields_spec: Dict[str, Dict[str, Any]]) -> str
  def generate_complete_code(class_name: str, fields_spec: Dict[str, Dict[str, Any]], additional_imports: str, path_from_base: str = None, field_map: Dict[str, str] = None) -> str



---
Filepath: src/matrx_utils/field_processing/field_handler.py  [python]

  def camel_to_snake(name: str) -> str
  def snake_to_camel(name: str) -> str
  def convert_list_elements(value: list, target_type: type) -> list
  def process_field_definitions(field_definitions: Dict[str, Dict[str, Any]], convert_camel_case: bool = False, fieldname_map: Optional[Dict[str, str]] = None, **kwargs) -> Dict[str, Any]
  def process_object_field_definitions(field_definitions: Dict[str, Dict[str, Any]], obj: Any, convert_camel_case: bool = False, fieldname_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]
  def process_batch_field_definitions(field_definitions: Dict[str, Dict[str, Any]], objects: List[Any], convert_camel_case: bool = False, fieldname_map: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]
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
  "subdirectory": "src/matrx_utils",
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
