# `src.matrx_utils.fancy_prints` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_utils/fancy_prints` |
| Last generated | 2026-02-28 14:46 |
| Output file | `src/matrx_utils/fancy_prints/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_utils/fancy_prints --mode signatures
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

> Auto-generated. 8 files across 2 directories.

```
src/matrx_utils/fancy_prints/
├── MODULE_README.md
├── __init__.py
├── colors.py
├── fancy_prints.py
├── matrx_print_logger.py
├── redaction.py
├── utils/
│   ├── __init__.py
│   ├── matrx_json_converter.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_utils/fancy_prints/__init__.py  [python]



---
Filepath: src/matrx_utils/fancy_prints/redaction.py  [python]

  def is_sensitive(key, additional_keys = None)
  def redact_object(obj, redact_keys = None)
  def redact_string(value)
  def redact_value(value)


---
Filepath: src/matrx_utils/fancy_prints/colors.py  [python]

  COLORS = {32 keys}


---
Filepath: src/matrx_utils/fancy_prints/matrx_print_logger.py  [python]

  class MatrixPrintLog:
      def __init__(self, system_level, class_name, outro = None)
      def camel_case_to_title(name)
      def snake_case_to_title(name)
      def get_caller_info(self, number = 2)
      def method_into(self, number = 1, start_text = '')
      def method_name(self, number = 1, pretty = False)
      def simple_method_into(self, number = 1, start_text = '')
      def get_effective_level(self, message_level = None)
      def should_log(self, message_level = None)
      def should_print(self, message_level = None)
      def _clean_for_log(self)
      def log_message(self)
      def vcprint(self, data = None, title = 'no title', level = None, color = None, background = None, style = None, pretty = True, indent = 4, inline = False, chunks = False, exc_info = None)
      def pretty_print(self, data = None, title = None, level = None, color = None, background = None, style = None, pretty = True, indent = 4, inline = False, chunks = False, exc_info = None)
      def inline_print(self, data = None, title = None, level = None, color = None, background = None, style = None, pretty = False, indent = 4, inline = True, chunks = False, exc_info = None)
      def print(self, data = None, title = None, level = 'PRINT', color = None, background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, exc_info = None)
      def debug_print(self, data = None, title = None, level = 'DEBUG', color = 'gray', background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, exc_info = None)
      def info_print(self, data = None, title = 'Info', level = 'INFO', color = 'light_blue', background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, exc_info = None)
      def warning_print(self, data = None, title = 'Warning!', level = 'WARNING', color = 'yellow', background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, exc_info = None)
      def error_print(self, data = None, title = 'Error!', level = 'ERROR', color = 'red', background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, exc_info = None)
      def critical_print(self, data = None, title = 'critical!', level = 'CRITICAL', color = 'red', background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, exc_info = None)
      def _print_and_or_log(self, data = None, title = None, level = None, color = None, background = None, style = None, pretty = None, indent = None, inline = None, chunks = None, exc_info = None)
      def _print(self)
      def _pretty_print(self)
      def _colorize(self, text)
      def _color_print(self)
      def _is_vscode_terminal() -> bool
      def _format_file_link(path: str) -> str
      def print_link(self, path)
      def print_truncated(self, value, max_chars = 250)


---
Filepath: src/matrx_utils/fancy_prints/fancy_prints.py  [python]

  class InlinePrinter:
      def __init__(self, prefix = '', separator = ' | ')
      def print(self, item, color = 'blue', end = False)
  def clean_data_for_logging(data)
  def colorize(text, color = None, background = None, style = None)
  def vcprint(data = None, title = 'Unnamed Data', color = None, verbose = True, background = None, style = None, pretty = False, indent = 4, inline = False, chunks = False, simple = False, log_level = logging.INFO) -> None
  def pretty_print(data, title = 'Unnamed Data', color = 'white', background = 'black', style = None, indent = 4, inline = False, chunks = False)
  def _is_vscode_terminal() -> bool
  def _format_file_link(path: str) -> str
  def print_link(path)
  def plt(path, title)
  def print_truncated(value, max_chars = 250)
  def cool_print(text, color, background = None, style = None)
  def create_inline_printer(prefix = '[AI Matrix] ', separator = ' | ')
  def get_random_color()
  def is_empty(value)
  def vclist(data = None, title = 'Unnamed Data', color = None, verbose = True, background = None, style = None, pretty = False, indent = 4, inline = False)


---
Filepath: src/matrx_utils/fancy_prints/utils/__init__.py  [python]



---
Filepath: src/matrx_utils/fancy_prints/utils/matrx_json_converter.py  [python]

  LOCAL_DEBUG = False
  def _convert_recursive(data)
  def validate_basic_types(data, path = 'root')
  def to_matrx_json(data = None)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_utils, psycopg2
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_utils/fancy_prints",
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
