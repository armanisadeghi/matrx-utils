# `src.matrx_utils.file_handling.specific_handlers` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_utils/file_handling/specific_handlers` |
| Last generated | 2026-02-28 14:46 |
| Output file | `src/matrx_utils/file_handling/specific_handlers/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_utils/file_handling/specific_handlers --mode signatures
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

> Auto-generated. 8 files across 1 directories.

```
src/matrx_utils/file_handling/specific_handlers/
├── MODULE_README.md
├── __init__.py
├── code_handler.py
├── html_handler.py
├── image_handler.py
├── json_handler.py
├── markdown_handler.py
├── text_handler.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_utils/file_handling/specific_handlers/code_handler.py  [python]

  class CodeHandler(FileManager):
      def __init__(self, batch_print = True, save_direct = False)
      def print_all_batched(self)
      def _generate_session_filename(self)
      def _validate_filename_extension(self, filename)
      def add_generated_code(self, code_object)
      def get_json(self, file_name)
      def save_json(self, file_name, data)
      def write_to_json(self, path, data, root = 'temp', clean = True)
      def append_json(self, file_name, new_data, root = 'temp', clean = True)
      def get_list(self, directory, file_type = 'json')
      def save_code_file(self, file_path, content)
      def save_code_anywhere(self, path, content)
      def read_code_file(self, file_path)
      def append_code_file(self, file_path, content)
      def delete_code_file(self, file_path)
      def code_file_exists(self, file_path)
      def generate_and_save_code(self, temp_path, main_code, file_location = None, import_lines = None, additional_top_lines = None, additional_bottom_lines = None, additional_code = None, path = None)
      def generate_and_save_code_from_object(self, config_obj, main_code, additional_code = None)


---
Filepath: src/matrx_utils/file_handling/specific_handlers/__init__.py  [python]



---
Filepath: src/matrx_utils/file_handling/specific_handlers/image_handler.py  [python]

  class ImageHandler(FileHandler):
      def __init__(self, app_name, batch_print = False)
      def custom_read_image(self, path)
      def custom_write_image(self, path, image)
      def custom_append_image(self, path, image, position = (0, 0))
      def custom_delete_image(self, path)
      def read_image(self, root, path)
      def write_image(self, root, path, image)
      def append_image(self, root, path, image, position = (0, 0))
      def delete_image(self, root, path)
      def get_image_size(self, root, path)
      def get_image_format(self, root, path)
      def get_image_mode(self, root, path)
      def resize_image(self, root, path, width, height)
      def convert_image_format(self, root, path, target_format)
      def crop_image(self, root, path, left, top, right, bottom)
      def rotate_image(self, root, path, angle)
      def merge_images(self, root, path_list, output_path)
      def add_watermark(self, root, path, watermark_path, position = (0, 0), opacity = 128)
      def adjust_brightness(self, root, path, factor)
      def convert_to_grayscale(self, root, path)
      def create_thumbnail(self, root, path, size)
      def flip_image(self, root, path, direction = 'horizontal')


---
Filepath: src/matrx_utils/file_handling/specific_handlers/markdown_handler.py  [python]

  class MarkdownHandler(FileHandler):
      def __init__(self, app_name, batch_print = False)
      def custom_read_markdown(self, path)
      def custom_write_markdown(self, path, content)
      def custom_append_markdown(self, path, content)
      def custom_delete_markdown(self, path)
      def read_markdown(self, root, path)
      def write_markdown(self, root, path, content, clean = True)
      def append_markdown(self, root, path, content)
      def delete_markdown(self, root, path)
      def read_lines(self, root, path)
      def write_lines(self, root, path, lines, clean = True)
      def read_words(self, root, path)
      def extract_sections(self, root, path)
      def extract_headers(self, root, path, level = 1)
      def set_xhtml_output(self, xhtml = True)
      def get_paragraphs(self, root, path)
      def get_blockquotes(self, root, path)
      def get_lists(self, root, path)
      def get_code_blocks(self, root, path)
      def get_horizontal_rules(self, root, path)
      def get_links(self, root, path)
      def get_images(self, root, path)
      def get_automatic_links(self, root, path)
      def escape_special_characters(self, text)


---
Filepath: src/matrx_utils/file_handling/specific_handlers/text_handler.py  [python]

  class TextHandler(FileHandler):
      def __init__(self, app_name, batch_print = False)
      def custom_read_text(self, path)
      def custom_write_text(self, path, content)
      def custom_append_text(self, path, content)
      def custom_delete_text(self, path)
      def read_text(self, root, path)
      def write_text(self, root, path, content, clean = True)
      def append_text(self, root, path, content)
      def delete_text(self, root, path)
      def read_lines(self, root, path)
      def write_lines(self, root, path, lines, clean = True)
      def read_words(self, root, path)


---
Filepath: src/matrx_utils/file_handling/specific_handlers/json_handler.py  [python]

  class JsonHandler(FileHandler):
      def __init__(self, app_name, batch_print = False)
      def custom_read_json(self, path)
      def custom_write_json(self, path, data, clean = True)
      def custom_append_json(self, path, data, clean = True)
      def custom_delete_json(self, path)
      def read_json(self, root, path)
      def write_json(self, root, path, data, clean = True, report_errors = True)
      def append_json(self, root, path, data, clean = True)
      def delete_json(self, root, path)
      def get_keys(self, root, path)
      def get_values(self, root, path)
      def get_items(self, root, path)
      def ensure_json_extension(self, path)
      def make_serializable(self, data, report_errors = False)
      def _log_and_serialize(self, data)


---
Filepath: src/matrx_utils/file_handling/specific_handlers/html_handler.py  [python]

  class HtmlHandler(FileHandler):
      def __init__(self, app_name, batch_print = False)
      def custom_read_html(self, path)
      def custom_write_html(self, path, content)
      def custom_append_html(self, path, content)
      def custom_delete_html(self, path)
      def read_html(self, root, path)
      def write_html(self, root, path, content, clean = False)
      def append_html(self, root, path, content)
      def delete_html(self, root, path)
      def extract_links(self, root, path)
      def extract_text(self, root, path)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** PIL, matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_utils/file_handling/specific_handlers",
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
