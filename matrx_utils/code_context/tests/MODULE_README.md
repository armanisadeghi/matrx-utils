# `utils.code_context.tests` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `utils/code_context/tests` |
| Last generated | 2026-02-28 14:52 |
| Output file | `utils/code_context/tests/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py utils/code_context/tests --mode signatures
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

> Auto-generated. 7 files across 1 directories.

```
utils/code_context/tests/
├── MODULE_README.md
├── __init__.py
├── test_code_extractor.py
├── test_file_discovery.py
├── test_integration.py
├── test_output_modes.py
├── test_tree_generator.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: utils/code_context/tests/__init__.py  [python]



---
Filepath: utils/code_context/tests/test_integration.py  [python]

  class TestBasicPipeline:
      def test_build_returns_result(self, simple_project)
      def test_included_files_excludes_node_modules(self, simple_project)
      def test_included_files_excludes_init(self, simple_project)
      def test_included_files_contains_python_files(self, simple_project)
      def test_combined_text_contains_tree(self, simple_project)
      def test_output_header_present(self, simple_project)
      def test_stats_correct_file_count(self, simple_project)
  class TestModeTreeOnly:
      def test_tree_only_contains_tree(self, simple_project)
      def test_tree_only_no_file_content(self, simple_project)
      def test_tree_only_saves_file(self, simple_project, tmp_path)
      def test_tree_only_output_mode_recorded(self, simple_project)
  class TestModeSignatures:
      def test_signatures_contains_tree(self, simple_project)
      def test_signatures_contains_function_names(self, simple_project)
      def test_signatures_contains_class_name(self, simple_project)
      def test_signatures_no_function_bodies(self, simple_project)
      def test_signatures_blocks_populated(self, simple_project)
      def test_signatures_filepath_labels_present(self, simple_project)
      def test_signatures_saves_file(self, simple_project, tmp_path)
      def test_signatures_much_smaller_than_clean(self, simple_project)
  class TestModeClean:
      def test_clean_strips_python_comments(self, simple_project)
      def test_clean_contains_code(self, simple_project)
      def test_clean_contains_file_headers(self, simple_project)
      def test_clean_saves_with_mode_in_filename(self, simple_project, tmp_path)
  class TestModeOriginal:
      def test_original_preserves_comments(self, simple_project)
      def test_original_saves_with_mode_in_filename(self, simple_project, tmp_path)
      def test_original_output_mode_recorded(self, simple_project)
  class TestPromptWrapping:
      def test_prefix_prepended(self, simple_project)
      def test_suffix_appended(self, simple_project)
      def test_prefix_appears_before_suffix(self, simple_project)
      def test_prefix_works_in_tree_only_mode(self, simple_project)
  class TestSubdirectoryScoping:
      def test_subdirectory_limits_scan(self, simple_project)
      def test_subdirectory_tree_shows_scanned_dir(self, simple_project)
  class TestAdditionalFiles:
      def test_additional_file_included_in_file_list(self, simple_project, tmp_path)
      def test_additional_file_content_appears_in_original_mode(self, simple_project, tmp_path)
  class TestRuntimeOverrides:
      def test_add_extra_exclude_directory(self, simple_project)
      def test_remove_default_exclude(self, simple_project)
      def test_include_extensions_whitelist(self, multi_lang_project)
  class TestSaveToDisk:
      def test_save_creates_combined_file(self, simple_project, tmp_path)
      def test_saved_file_contains_tree_and_content(self, simple_project, tmp_path)
      def test_save_creates_export_directory_if_missing(self, simple_project, tmp_path)
      def test_individual_save_creates_files(self, simple_project, tmp_path)
      def test_filename_includes_output_mode(self, simple_project, tmp_path)
  class TestMultiLangProject:
      def test_default_excludes_txt_and_css(self, multi_lang_project)
      def test_py_and_ts_included_when_ts_not_excluded(self, multi_lang_project)
  class TestDeepNesting:
      def test_all_deep_files_discovered(self, nested_project)
      def test_tree_shows_nested_structure(self, nested_project)
      def test_file_headers_use_relative_paths_original_mode(self, nested_project)
  def simple_project(tmp_path) -> Path
  def multi_lang_project(tmp_path) -> Path
  def nested_project(tmp_path) -> Path


---
Filepath: utils/code_context/tests/test_code_extractor.py  [python]

  class TestFileReading:
      def test_reads_utf8_file(self, tmp_path)
      def test_original_char_count(self, tmp_path)
      def test_nonexistent_file_returns_none(self, tmp_path)
      def test_get_content_original_returns_original(self, tmp_path)
      def test_get_content_clean_before_strip_returns_original(self, tmp_path)
  class TestPythonCommentRemoval:
      def test_removes_hash_comment(self, tmp_path)
      def test_removes_standalone_hash_comment(self, tmp_path)
      def test_removes_triple_double_quote_docstring(self, tmp_path)
      def test_removes_triple_single_quote_docstring(self, tmp_path)
      def test_removes_multiline_docstring(self, tmp_path)
      def test_preserves_regular_strings(self, tmp_path)
      def test_clean_char_count_less_than_original(self, tmp_path)
  class TestJSCommentRemoval:
      def test_removes_single_line_comment(self, tmp_path)
      def test_removes_block_comment(self, tmp_path)
      def test_removes_multiline_block_comment(self, tmp_path)
      def test_removes_jsdoc_comment(self, tmp_path)
  class TestBlankLineNormalization:
      def test_collapses_three_blank_lines_to_two(self, tmp_path)
      def test_preserves_single_blank_line(self, tmp_path)
      def test_preserves_double_blank_line(self, tmp_path)
  class TestFileHeader:
      def test_header_contains_filepath(self, tmp_path)
      def test_header_contains_separator(self, tmp_path)
      def test_header_uses_relative_path_when_root_given(self, tmp_path)
      def test_header_uses_forward_slashes(self, tmp_path)
  class TestASTAnalyzer:
      def test_extracts_top_level_function(self, tmp_path)
      def test_extracts_class_with_methods(self, tmp_path)
      def test_methods_not_double_counted_as_functions(self, tmp_path)
      def test_async_function_extracted(self, tmp_path)
      def test_async_method_in_class(self, tmp_path)
      def test_non_python_file_returns_error(self, tmp_path)
      def test_syntax_error_returns_graceful_error(self, tmp_path)
      def test_to_text_output_format(self, tmp_path)
      def test_to_text_uses_relative_path(self, tmp_path)
      def test_analyze_files_batch(self, tmp_path)
      def test_empty_file_no_error(self, tmp_path)
      def test_multiple_classes_extracted(self, tmp_path)
  def make_extractor(content: str, suffix: str = '.py', tmp_path = None) -> CodeExtractor


---
Filepath: utils/code_context/tests/test_tree_generator.py  [python]

  class TestTreeBasicStructure:
      def test_empty_file_list(self)
      def test_single_file_in_root(self, tmp_path)
      def test_multiple_files_appear(self, tmp_path)
      def test_nested_files_appear(self, tmp_path)
      def test_unicode_box_drawing(self, tmp_path)
      def test_root_name_ends_with_slash(self, tmp_path)
  class TestSparseMode:
      def test_does_not_show_empty_sibling_dir(self, tmp_path)
      def test_only_shows_paths_that_lead_to_included_files(self, tmp_path)
  class TestFullMode:
      def test_shows_empty_sibling_dir(self, tmp_path)
      def test_excluded_dirs_not_shown_in_full_mode(self, tmp_path)
  class TestCustomRoot:
      def test_custom_root_overrides_common_prefix(self, tmp_path)
      def test_custom_root_different_from_file_location(self, tmp_path)
  class TestTreeOrdering:
      def test_entries_sorted_alphabetically(self, tmp_path)
      def test_directories_before_files(self, tmp_path)
  class TestTreeIndentation:
      def test_depth_indentation_uses_pipe_chars(self, tmp_path)
      def test_multiple_files_same_dir_all_appear(self, tmp_path)
  def make_cfg(**kwargs) -> CodeContextConfig
  def build_tree(files: list[Path], cfg: CodeContextConfig | None = None, custom_root = None, scan_root = None) -> str


---
Filepath: utils/code_context/tests/test_file_discovery.py  [python]

  class TestExactDirectoryExclusion:
      def test_excludes_exact_match(self)
      def test_case_insensitive_exact(self)
      def test_does_not_exclude_partial_name(self)
      def test_empty_list_excludes_nothing(self)
      def test_git_excluded(self)
  class TestDirectorySubstringExclusion:
      def test_word_boundary_match_exact_word(self)
      def test_word_boundary_match_prefix(self)
      def test_word_boundary_match_suffix(self)
      def test_word_boundary_does_not_match_mid_word(self)
      def test_word_boundary_dot_separator(self)
      def test_word_boundary_dash_separator(self)
      def test_multiple_patterns(self)
  class TestExactFileExclusion:
      def test_excludes_exact_filename(self)
      def test_case_insensitive_filename(self)
      def test_does_not_exclude_different_file(self)
  class TestFilenameSubstringExclusion:
      def test_word_boundary_match_in_filename(self)
      def test_word_boundary_no_false_positive(self)
  class TestExtensionFiltering:
      def test_extension_blacklist(self)
      def test_extension_case_insensitive(self)
      def test_whitelist_overrides_blacklist(self)
      def test_whitelist_only_allows_listed_extensions(self)
      def test_no_extension_file_with_blacklist(self)
  class TestDiscoverWithTempDir:
      def test_discovers_files_in_root(self, tmp_path)
      def test_skips_excluded_directory(self, tmp_path)
      def test_skips_excluded_file(self, tmp_path)
      def test_subdirectory_restricts_scan(self, tmp_path)
      def test_additional_files_injected(self, tmp_path)
      def test_nonexistent_root_returns_empty(self, tmp_path)
      def test_analyze_returns_correct_stats(self, tmp_path)
  class TestConfigOverrides:
      def test_add_exclude_directory(self)
      def test_remove_exclude_directory(self)
      def test_add_include_extension(self)
      def test_no_duplicate_on_repeated_add(self)
      def test_remove_nonexistent_is_safe(self)
  def make_cfg(**kwargs) -> CodeContextConfig


---
Filepath: utils/code_context/tests/test_output_modes.py  [python]

  class TestOutputModeOrdering:
      def real_project(self, tmp_path) -> Path
      def test_tree_only_smallest(self, real_project)
      def test_signatures_smaller_than_clean(self, real_project)
      def test_clean_smaller_than_original(self, real_project)
      def test_all_modes_contain_tree(self, real_project)
      def test_all_modes_contain_header(self, real_project)
  class TestPythonSignatures:
      def test_top_level_function(self, tmp_path)
      def test_class_with_methods(self, tmp_path)
      def test_function_body_absent(self, tmp_path)
      def test_async_function(self, tmp_path)
      def test_type_annotations_in_signature(self, tmp_path)
      def test_star_args(self, tmp_path)
      def test_base_class_in_signature(self, tmp_path)
      def test_syntax_error_returns_graceful_note(self, tmp_path)
      def test_empty_file_no_signatures_no_error(self, tmp_path)
      def test_language_tagged_as_python(self, tmp_path)
  class TestTypeScriptSignatures:
      def test_exported_function(self, tmp_path)
      def test_class_declaration(self, tmp_path)
      def test_interface_declaration(self, tmp_path)
      def test_arrow_function_const(self, tmp_path)
      def test_function_body_absent(self, tmp_path)
      def test_language_tagged_as_typescript(self, tmp_path)
      def test_tsx_tagged_as_typescript(self, tmp_path)
      def test_js_function(self, tmp_path)
  class TestGoSignatures:
      def test_func_declaration(self, tmp_path)
      def test_method_declaration(self, tmp_path)
      def test_struct_type(self, tmp_path)
      def test_interface_type(self, tmp_path)
  class TestRustSignatures:
      def test_pub_fn(self, tmp_path)
      def test_struct_declaration(self, tmp_path)
      def test_impl_block(self, tmp_path)
      def test_trait_declaration(self, tmp_path)
  class TestJavaSignatures:
      def test_class_declaration(self, tmp_path)
      def test_interface_declaration(self, tmp_path)
  class TestOtherLanguages:
      def test_ruby_method(self, tmp_path)
      def test_php_function(self, tmp_path)
      def test_lua_function(self, tmp_path)
      def test_kotlin_class(self, tmp_path)
      def test_swift_function(self, tmp_path)
      def test_dart_class(self, tmp_path)
  class TestUnsupportedLanguage:
      def test_unknown_extension_returns_note(self, tmp_path)
      def test_unknown_extension_no_crash(self, tmp_path)
      def test_no_extension_graceful(self, tmp_path)
  class TestSignatureBlockText:
      def test_to_text_contains_filepath(self, tmp_path)
      def test_to_text_contains_language_tag(self, tmp_path)
      def test_to_text_uses_relative_path(self, tmp_path)
      def test_to_text_indents_signatures(self, tmp_path)
      def test_to_text_note_shown_for_unsupported(self, tmp_path)
  class TestExtractFilesMulti:
      def test_batch_extraction(self, tmp_path)
      def test_batch_no_crash_on_mixed_supported_unsupported(self, tmp_path)
  def make_extractor() -> SignatureExtractor
  def extract(tmp_path, filename: str, content: str) -> SignatureBlock
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** pytest
**Internal modules:** utils.code_context
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "utils/code_context/tests",
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
