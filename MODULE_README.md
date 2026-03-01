# `` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `` |
| Last generated | 2026-02-28 14:46 |
| Output file | `MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`src/MODULE_README.md`](src/MODULE_README.md) | last generated 2026-02-28 14:46 |
| [`tests/MODULE_README.md`](tests/MODULE_README.md) | last generated 2026-02-28 14:46 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py  --mode signatures
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

> Auto-generated. 45 files across 12 directories.

```
./
├── .python-version
├── main.py
├── release.sh
├── src/
│   ├── MODULE_README.md
│   ├── matrx_utils/
│   │   ├── __init__.py
│   │   ├── conf.py
│   │   ├── data_handling/
│   │   │   ├── __init__.py
│   │   │   ├── data_transformer.py
│   │   │   ├── utils.py
│   │   │   ├── validation/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── errors.py
│   │   │   │   ├── validators.py
│   │   ├── fancy_prints/
│   │   │   ├── __init__.py
│   │   │   ├── colors.py
│   │   │   ├── fancy_prints.py
│   │   │   ├── matrx_print_logger.py
│   │   │   ├── redaction.py
│   │   │   ├── utils/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── matrx_json_converter.py
│   │   ├── field_processing/
│   │   │   ├── __init__.py
│   │   │   ├── dataclass_generator.py
│   │   │   ├── field_handler.py
│   │   ├── file_handling/
│   │   │   ├── __init__.py
│   │   │   ├── base_handler.py
│   │   │   ├── batch_handler.py
│   │   │   ├── file_handler.py
│   │   │   ├── file_manager.py
│   │   │   ├── local_files.py
│   │   │   ├── specific_handlers/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── code_handler.py
│   │   │   │   ├── html_handler.py
│   │   │   │   ├── image_handler.py
│   │   │   │   ├── json_handler.py
│   │   │   │   ├── markdown_handler.py
│   │   │   │   ├── text_handler.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── clear_terminal.py
│   │   │   ├── get_dir_structure.py
│   │   │   ├── testing.py
├── tests/
│   ├── MODULE_README.md
│   ├── field_generation.py
│   ├── field_processing.py
│   ├── get_dir_structure_test.py
│   ├── load_env_for_test.py
│   ├── print_link_test.py
# excluded: 8 .md, 1 (no ext), 1 .toml, 1 .lock
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: .python-version  [unknown ()]

  # signature extraction not supported for this language



---
Filepath: release.sh  [unknown (.sh)]

  # signature extraction not supported for this language



---
Filepath: main.py  [python]




---
Submodule: tests/  [5 files — full detail in tests/MODULE_README.md]

---
Submodule: src/  [35 files — full detail in src/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. All Python files
> Covered submodules shown as stubs — see child READMEs for full detail: `src`, `tests`
> Excluded from call graph: `tests`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: src.matrx_utils.conf

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.conf._ensure_configured → src.matrx_utils.conf.NotConfiguredError('Call matrx_utils.conf.configure() first.') (line 36)` → ... → `...clear() (line 208)`
```

### Call graph: src.matrx_utils.fancy_prints.redaction

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.fancy_prints.redaction.is_sensitive → sensitive_patterns.extend(additional_keys) (line 8)` → ... → `src.matrx_utils.fancy_prints.redaction.redact_object(item, redact_keys) (line 34)`
```

### Call graph: src.matrx_utils.fancy_prints.matrx_print_logger

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.fancy_prints.matrx_print_logger.__init__ → logging.getLogger('matrx_print_logger') (line 14)` → ... → `src.matrx_utils.fancy_prints.matrx_print_logger.urlparse(self.path) (line 370)`
```

### Call graph: src.matrx_utils.fancy_prints.fancy_prints

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → logging.getLogger('vcprint') (line 13)` → ... → `src.matrx_utils.fancy_prints.fancy_prints.is_empty(item) (line 388)`
```

### Call graph: src.matrx_utils.fancy_prints.utils.matrx_json_converter

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.fancy_prints.utils.matrx_json_converter._convert_recursive → src.matrx_utils.fancy_prints.utils.matrx_json_converter.is_dataclass(data) (line 27)` → ... → `src.matrx_utils.fancy_prints.utils.matrx_json_converter.validate_basic_types(converted_data) (line 203)`
```

### Call graph: src.matrx_utils.data_handling.utils

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.data_handling.utils.get_random_text_entry → random.choice(words) (line 14)`
```

### Call graph: src.matrx_utils.data_handling.data_transformer

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`Global Scope → strftime('%Y%m%d%H%M%S') (line 13)` → ... → `transformer.to_type_annotation(sql_type, 'python') (line 895)`
```

### Call graph: src.matrx_utils.data_handling.validation.validators

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.data_handling.validation.validators.compile_regex → re.compile(regex, flags) (line 13)` → ... → `src.matrx_utils.data_handling.validation.validators.Decimal('1.25') (line 1072)`
```

### Call graph: src.matrx_utils.file_handling.file_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.file_handler.__init__ → src.matrx_utils.file_handling.file_handler.Path(settings.BASE_DIR) (line 22)` → ... → `...add_print(full_path, _message, color) (line 249)`
```

### Call graph: src.matrx_utils.file_handling.batch_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.batch_handler.get_instance → src.matrx_utils.file_handling.batch_handler.cls(enable_batch) (line 17)` → ... → `...clear() (line 77)`
```

### Call graph: src.matrx_utils.file_handling.file_manager

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.file_manager.__init__ → BatchHandler.get_instance() (line 22)` → ... → `...public_get_full_path(root, path) (line 167)`
```

### Call graph: src.matrx_utils.file_handling.local_files

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.local_files.is_wsl → ...startswith('linux') (line 11)` → ... → `file_obj.close() (line 128)`
```

### Call graph: src.matrx_utils.file_handling.specific_handlers.code_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.specific_handlers.code_handler.print_all_batched → ...print_batch() (line 21)` → ... → `self.generate_and_save_code(temp_path, main_code, file_location, import_lines, additional_top_lines, additional_bottom_lines, additional_code, path) (line 107)`
```

### Call graph: src.matrx_utils.file_handling.specific_handlers.image_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.specific_handlers.image_handler.custom_read_image → Image.open(path) (line 14)` → ... → `self.write_image(root, path, flipped_image) (line 165)`
```

### Call graph: src.matrx_utils.file_handling.specific_handlers.markdown_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.specific_handlers.markdown_handler.custom_read_markdown → self.read(path) (line 12)` → ... → `escape_pattern.sub('\\\\\\1', text) (line 129)`
```

### Call graph: src.matrx_utils.file_handling.specific_handlers.text_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.specific_handlers.text_handler.custom_read_text → self.read(path) (line 10)` → ... → `content.split() (line 45)`
```

### Call graph: src.matrx_utils.file_handling.specific_handlers.json_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.specific_handlers.json_handler.custom_read_json → self.read(path) (line 12)` → ... → `json.dumps(serializable_data) (line 130)`
```

### Call graph: src.matrx_utils.file_handling.specific_handlers.html_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.file_handling.specific_handlers.html_handler.custom_read_html → self.read(path) (line 11)` → ... → `re.sub('<[^>]+>', '', content) (line 44)`
```

### Call graph: src.matrx_utils.utils.get_dir_structure

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.utils.get_dir_structure.generate_directory_structure → src.matrx_utils.utils.get_dir_structure.StringIO() (line 34)` → ... → `src.matrx_utils.utils.get_dir_structure.print_link(text_output_file) (line 238)`
```

### Call graph: src.matrx_utils.utils.clear_terminal

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.utils.clear_terminal.clear_terminal → os.system('cls') (line 6)` → ... → `os.system('clear') (line 8)`
```

### Call graph: src.matrx_utils.utils.testing

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.utils.testing.cleanup_async_resources → warnings.catch_warnings() (line 26)` → ... → `src.matrx_utils.utils.testing.cleanup_async_resources() (line 77)`
```

### Call graph: src.matrx_utils.field_processing.dataclass_generator

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.field_processing.dataclass_generator.to_snake_case → lower() (line 21)` → ... → `src.matrx_utils.field_processing.dataclass_generator.print_link(file_path) (line 292)`
```

### Call graph: src.matrx_utils.field_processing.field_handler

> Full detail in [`src/MODULE_README.md`](src/MODULE_README.md)

```
`src.matrx_utils.field_processing.field_handler.camel_to_snake → re.sub('(.)([A-Z][a-z]+)', '\\1_\\2', name) (line 7)` → ... → `src.matrx_utils.field_processing.field_handler.process_object_field_definitions(field_definitions, obj) (line 169)`
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** IPython, OpenSSL, PIL, PyQt6, PySide6, annotationlib, backports, brotli, brotlicffi, certifi, chardet, charset_normalizer, click, compression, cryptography, defusedxml, dotenv, dummy_threading, h2, idna, importlib_metadata, inflect, js, load_env_for_test, matrx_utils, more_itertools, numpy, olefile, packaging, psycopg2, pyodide, pytest, requests, simplejson, socks, typeguard, typeshed, typing_extensions, urllib3
**Internal modules:** src.matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": true,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
