# `src.matrx_utils.data_handling` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `src/matrx_utils/data_handling` |
| Last generated | 2026-02-28 14:46 |
| Output file | `src/matrx_utils/data_handling/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py src/matrx_utils/data_handling --mode signatures
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

> Auto-generated. 7 files across 2 directories.

```
src/matrx_utils/data_handling/
├── MODULE_README.md
├── __init__.py
├── data_transformer.py
├── utils.py
├── validation/
│   ├── __init__.py
│   ├── errors.py
│   ├── validators.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: src/matrx_utils/data_handling/__init__.py  [python]



---
Filepath: src/matrx_utils/data_handling/utils.py  [python]

  def get_random_text_entry()


---
Filepath: src/matrx_utils/data_handling/data_transformer.py  [python]

  class SingletonMeta(type):
      def __call__(cls, *args, **kwargs)
  class DataTransformer:
      def __init__(self)
      def set_enum_list(self, enum_list)
      def set_and_update_ts_enum_list(self, enum_list)
      def get_enum_list(self)
      def update_transformation_list_with_enums(self)
      def method_name(self)
      def to_rdx_model_format(self, value, data_type)
      def normalize_to_snake_case(self, s)
      def to_lower_case(self, s)
      def to_upper_case(self, s)
      def to_snake_case(self, s)
      def to_kebab_case(self, s)
      def to_camel_case(self, s)
      def to_pascal_case(self, s)
      def to_title_case(self, s)
      def to_space_case(self, s)
      def to_plural(self, s)
      def to_singular(self, s)
      def to_constant_case(self, s)
      def to_dot_notation(self, s)
      def to_acronym(self, s)
      def remove_special_characters(self, s)
      def to_valid_identifier(self, s)
      def to_quoted_string(self, s)
      def to_typescript_type(self, s)
      def to_typescript_type_enums_to_string(self, s, has_enum_labels = False)
      def to_matrx_schema_type(self, s)
      def to_python_models_field(self, s)
      def to_union_enum(self, values, for_enum = False)
      def backup_to_typescript_type(self, s)
      def to_python_type(self, s)
      def to_type_annotation(self, s, language = 'typescript')
      def to_comment(self, s, language = 'python')
      def to_url_safe(self, s)
      def convert_value_to_data_type(self, value, data_type)
      def class_name(self)
      def class_id(self)
      def method_id(self)
      def prettify_name(self, name: str) -> str
      def get_caller_method_name(self)
      def print_method_name(self)
      def print_class(self)
      def find_keys_without_terms(self, data, terms)
      def get_column_test_values(self, data_type, options)
      def replace_dict_keys(self, data, key_map, replace_in_lists = True)
      def convert_keys_to_camel_case(self, data, replace_in_lists = True)
      def python_dict_to_ts(self, obj, indent = 0)
      def python_dict_to_ts_with_updates(self, name, obj, keys_to_camel = True, export = True, as_const = False, ts_type = None, indent = 0)
  def check_key_or_value(key_or_value)
  def recursive_search(obj)


---
Filepath: src/matrx_utils/data_handling/validation/__init__.py  [python]



---
Filepath: src/matrx_utils/data_handling/validation/errors.py  [python]

  class ValidationError(ValueError):
      def __init__(self, message, code = None, params = None)


---
Filepath: src/matrx_utils/data_handling/validation/validators.py  [python]

  class RegexValidator:
      def __init__(self, regex = None, message = None, code = None, inverse_match = None, flags = None)
      def __call__(self, value)
      def __eq__(self, other)
  class BaseValidator:
      def __init__(self, limit_value, message = None)
      def __call__(self, value)
      def __eq__(self, other)
      def compare(self, a, b)
      def clean(self, x)
  class DomainNameValidator(RegexValidator):
      def __init__(self, accept_idna = True, message = None, code = None)
      def __call__(self, value)
  class URLValidator(RegexValidator):
      def __init__(self, schemes = None, message = None, code = None)
      def __call__(self, value)
  class EmailValidator:
      def __init__(self, message = None, code = None, allowlist = None)
      def __call__(self, value)
      def validate_domain_part(self, domain_part)
      def __eq__(self, other)
  class MaxValueValidator(BaseValidator):
      def compare(self, a, b)
  class MinValueValidator(BaseValidator):
      def compare(self, a, b)
  class StepValueValidator(BaseValidator):
      def __init__(self, limit_value, message = None, offset = None)
      def __call__(self, value)
      def compare(self, a, b)
  class MinLengthValidator(BaseValidator):
      def compare(self, a, b)
      def clean(self, x)
  class MaxLengthValidator(BaseValidator):
      def compare(self, a, b)
      def clean(self, x)
  class DecimalValidator:
      def __init__(self, max_digits, decimal_places)
      def __call__(self, value)
      def __eq__(self, other)
  class FileExtensionValidator:
      def __init__(self, allowed_extensions = None, message = None, code = None)
      def __call__(self, value)
      def __eq__(self, other)
  class ProhibitNullCharactersValidator:
      def __init__(self, message = None, code = None)
      def __call__(self, value)
      def __eq__(self, other)
  def compile_regex(regex, flags = 0)
  def punycode(domain)
  def validate_ipv4_address(value)
  def validate_ipv6_address(value)
  def validate_ipv46_address(value)
  def ip_address_validators(protocol, unpack_ipv4 = False)
  def validate_integer(value)
  def int_list_validator(sep = ',', message = None, code = 'invalid_list', allow_negative = False)
  def get_available_image_extensions()
  def validate_image_file_extension(value)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** PIL, inflect, matrx_utils
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "src/matrx_utils/data_handling",
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
