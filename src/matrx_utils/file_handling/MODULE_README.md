# `src.matrx_utils.file_handling` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_utils/file_handling` |
| Last generated | 2026-02-28 14:46 |
| Output file | `src/matrx_utils/file_handling/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/matrx_utils/file_handling/specific_handlers/MODULE_README.md`](src/matrx_utils/file_handling/specific_handlers/MODULE_README.md) | last generated 2026-02-28 14:46 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_utils/file_handling --mode signatures
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

> Auto-generated. 15 files across 2 directories.

```
src/matrx_utils/file_handling/
├── MODULE_README.md
├── __init__.py
├── base_handler.py
├── batch_handler.py
├── file_handler.py
├── file_manager.py
├── local_files.py
├── specific_handlers/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── code_handler.py
│   ├── html_handler.py
│   ├── image_handler.py
│   ├── json_handler.py
│   ├── markdown_handler.py
│   ├── text_handler.py
# excluded: 2 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: src/matrx_utils/file_handling/__init__.py  [python]




---
Filepath: src/matrx_utils/file_handling/file_handler.py  [python]

  class FileHandler(BaseHandler):
      def __init__(self, app_name, new_instance = False, batch_print = False, print_errors = True, batch_handler = None)
      def get_instance(cls, app_name, new_instance = False, batch_print = False, print_errors = True, batch_handler = None)
      def _get_full_path(self, root, path)
      def public_get_full_path(self, root, path)
      def _ensure_directory(self, path)
      def _print(self, path, message = None, color = None)
      def _print_link(self, path, message = None, color = None)
      def print_batch(self)
      def enable_batch_print(self)
      def disable_batch_print(self)
      def read(self, path, mode = 'r', encoding = 'utf-8')
      def write(self, path, content, **kwargs)
      def append(self, path, content)
      def delete(self, path)
      def read_from_base(self, root, path)
      def write_to_base(self, root, path, content, clean = True, remove_html = False, normalize_whitespace = False)
      def append_to_base(self, root, path, content)
      def delete_from_base(self, root, path)
      def clean(self, content, remove_html = False, normalize_whitespace = False)
      def _remove_html_tags(self, content)
      def _normalize_unicode(self, content)
      def _filter_unwanted_characters(self, content)
      def _normalize_whitespace(self, content)
      def file_exists(self, root, path)
      def delete_file(self, root, path)
      def list_files(self, root, path = '')
      def add_to_batch(self, full_path, message = None, color = None)



---
Filepath: src/matrx_utils/file_handling/batch_handler.py  [python]

  class BatchHandler:
      def __init__(self, enable_batch = False)
      def get_instance(cls, enable_batch = False)
      def add_print(self, path, message = None, color = None)
      def _print(self, path, message = None, color = None)
      def _print_link(self, path, message = None, color = None)
      def print_batch(self)
      def enable_batch(self)
      def disable_batch(self)
      def is_batch_print_enabled(self)



---
Filepath: src/matrx_utils/file_handling/file_manager.py  [python]

  class FileManager:
      def __init__(self, app_name, new_instance = False, batch_print = False, print_errors = True, batch_handler = None)
      def get_instance(cls, app_name, new_instance = False, batch_print = False, print_errors = True, batch_handler = None)
      def read(self, root, path, file_type = 'text')
      def write(self, root, path, content, file_type = 'text', clean = True)
      def file_exists(self, root, path, file_type = 'text')
      def delete_file(self, root, path, file_type = 'text')
      def list_files(self, root, path = '', file_type = 'text')
      def print_batch(self)
      def read_json(self, root, path)
      def write_json(self, root, path, data, clean = True)
      def append_json(self, root, path, data, clean = True)
      def read_temp_json(self, path)
      def write_temp_json(self, path, data, clean = True)
      def get_config_json(self, path)
      def read_text(self, root, path)
      def write_text(self, root, path, data, clean = True)
      def read_temp_text(self, path)
      def write_temp_text(self, path, data, clean = True)
      def read_html(self, root, path)
      def write_html(self, root, path, data, clean = True)
      def read_temp_html(self, path)
      def write_temp_html(self, path, data, clean = True)
      def read_markdown(self, root, path)
      def write_markdown(self, root, path, data, clean = True)
      def read_temp_markdown(self, path)
      def write_temp_markdown(self, path, data, clean = True)
      def read_markdown_lines(self, root, path)
      def write_markdown_lines(self, root, path, data, clean = True)
      def read_image(self, root, path)
      def write_image(self, root, path, data)
      def read_temp_image(self, path)
      def write_temp_image(self, path, data, clean = True)
      def generate_filename(self, extension, sub_dir = '', prefix = '', suffix = '', random = False)
      def generate_directoryname(self, sub_dir = '', prefix = '', suffix = '', random = False)
      def add_to_batch(self, full_path = None, message = None, color = None)
      def get_full_path_from_base(self, root, path)



---
Filepath: src/matrx_utils/file_handling/local_files.py  [python]

  def is_wsl() -> bool
  def convert_windows_to_wsl_path(windows_path: str) -> str
  def resolve_local_path(input_path: str | os.PathLike) -> Path
  def open_any_file(source: str) -> Tuple[str, BinaryIO]



---
Filepath: src/matrx_utils/file_handling/base_handler.py  [python]

  class BaseHandler(ABC):
      def read(self, path)
      def write(self, path, content)
      def append(self, path, content)
      def delete(self, path)



---
Submodule: src/matrx_utils/file_handling/specific_handlers/  [7 files — full detail in src/matrx_utils/file_handling/specific_handlers/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** PIL, matrx_utils, requests
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_utils/file_handling",
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
