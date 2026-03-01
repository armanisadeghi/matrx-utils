"""
End-to-end integration tests for CodeContextBuilder.

Uses pytest's tmp_path fixture to create realistic project structures and
verifies the full pipeline across all four output modes:
  tree_only / signatures / clean / original
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from matrx_utils.code_context.code_context import CodeContextBuilder, CodeContextResult


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def simple_project(tmp_path) -> Path:
    """
    myproject/
    ├── main.py
    ├── utils.py
    ├── node_modules/
    │   └── pkg.js        ← excluded
    └── src/
        ├── service.py
        └── __init__.py   ← excluded
    """
    root = tmp_path / "myproject"
    root.mkdir()
    (root / "main.py").write_text(
        "def main():\n    print('hello')\n\nmain()\n",
        encoding="utf-8",
    )
    (root / "utils.py").write_text(
        "# utility functions\ndef helper(x):\n    return x * 2\n",
        encoding="utf-8",
    )
    nm = root / "node_modules"
    nm.mkdir()
    (nm / "pkg.js").write_text("module.exports = {}", encoding="utf-8")
    src = root / "src"
    src.mkdir()
    (src / "service.py").write_text(
        "class Service:\n    def run(self):\n        pass\n",
        encoding="utf-8",
    )
    (src / "__init__.py").write_text("", encoding="utf-8")
    return root


@pytest.fixture()
def multi_lang_project(tmp_path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "app.py").write_text("def start(): pass\n", encoding="utf-8")
    (root / "index.ts").write_text("export function init() {}\n", encoding="utf-8")
    (root / "style.css").write_text("body { margin: 0; }\n", encoding="utf-8")
    (root / "readme.txt").write_text("docs\n", encoding="utf-8")
    return root


@pytest.fixture()
def nested_project(tmp_path) -> Path:
    root = tmp_path / "deep"
    root.mkdir()
    for depth_path, content in [
        ("a/b/c/deep.py", "def deep(): pass\n"),
        ("a/b/shallow.py", "def shallow(): pass\n"),
        ("top.py", "x = 1\n"),
    ]:
        p = root / depth_path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    return root


# ---------------------------------------------------------------------------
# Basic pipeline — shared across modes
# ---------------------------------------------------------------------------

class TestBasicPipeline:
    def test_build_returns_result(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="original")
        result = builder.build()
        assert isinstance(result, CodeContextResult)

    def test_included_files_excludes_node_modules(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project)
        result = builder.build()
        assert "pkg.js" not in {f.name for f in result.files}

    def test_included_files_excludes_init(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project)
        result = builder.build()
        assert "__init__.py" not in {f.name for f in result.files}

    def test_included_files_contains_python_files(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project)
        result = builder.build()
        names = {f.name for f in result.files}
        assert {"main.py", "utils.py", "service.py"} <= names

    def test_combined_text_contains_tree(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project)
        result = builder.build()
        assert "myproject/" in result.combined_text
        assert "src/" in result.combined_text

    def test_output_header_present(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="clean")
        result = builder.build()
        assert "Code Context" in result.combined_text
        assert "clean" in result.combined_text

    def test_stats_correct_file_count(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project)
        result = builder.build()
        assert result.stats["total_files"] == 3


# ---------------------------------------------------------------------------
# Mode: tree_only
# ---------------------------------------------------------------------------

class TestModeTreeOnly:
    def test_tree_only_contains_tree(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="tree_only")
        result = builder.build()
        assert result.output_mode == "tree_only"
        assert "myproject/" in result.combined_text
        assert "src/" in result.combined_text

    def test_tree_only_no_file_content(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="tree_only")
        result = builder.build()
        assert "def main():" not in result.combined_text
        assert "Filepath:" not in result.combined_text

    def test_tree_only_saves_file(self, simple_project, tmp_path):
        export_dir = tmp_path / "out"
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="tree_only",
            export_directory=str(export_dir),
        )
        result = builder.build()
        saved = builder.save(result)
        assert saved is not None
        assert saved.exists()
        assert "tree_only" in saved.name

    def test_tree_only_output_mode_recorded(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="tree_only")
        result = builder.build()
        assert result.output_mode == "tree_only"


# ---------------------------------------------------------------------------
# Mode: signatures
# ---------------------------------------------------------------------------

class TestModeSignatures:
    def test_signatures_contains_tree(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        result = builder.build()
        assert "myproject/" in result.combined_text

    def test_signatures_contains_function_names(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        result = builder.build()
        assert "main" in result.combined_text
        assert "helper" in result.combined_text

    def test_signatures_contains_class_name(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        result = builder.build()
        assert "Service" in result.combined_text

    def test_signatures_no_function_bodies(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        result = builder.build()
        assert "print('hello')" not in result.combined_text
        assert "return x * 2" not in result.combined_text

    def test_signatures_blocks_populated(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        result = builder.build()
        assert len(result.signature_blocks) > 0

    def test_signatures_filepath_labels_present(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        result = builder.build()
        assert "Filepath:" in result.combined_text

    def test_signatures_saves_file(self, simple_project, tmp_path):
        export_dir = tmp_path / "out"
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="signatures",
            export_directory=str(export_dir),
        )
        result = builder.build()
        saved = builder.save(result)
        assert saved is not None
        assert "signatures" in saved.name

    def test_signatures_much_smaller_than_clean(self, simple_project):
        sig_builder = CodeContextBuilder(project_root=simple_project, output_mode="signatures")
        clean_builder = CodeContextBuilder(project_root=simple_project, output_mode="clean")
        sig_result = sig_builder.build()
        clean_result = clean_builder.build()
        assert len(sig_result.combined_text) < len(clean_result.combined_text)


# ---------------------------------------------------------------------------
# Mode: clean
# ---------------------------------------------------------------------------

class TestModeClean:
    def test_clean_strips_python_comments(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="clean")
        result = builder.build()
        assert "utility functions" not in result.combined_text

    def test_clean_contains_code(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="clean")
        result = builder.build()
        assert "def main():" in result.combined_text

    def test_clean_contains_file_headers(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="clean")
        result = builder.build()
        assert "Filepath:" in result.combined_text

    def test_clean_saves_with_mode_in_filename(self, simple_project, tmp_path):
        export_dir = tmp_path / "out"
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="clean",
            export_directory=str(export_dir),
        )
        result = builder.build()
        saved = builder.save(result)
        assert "clean" in saved.name


# ---------------------------------------------------------------------------
# Mode: original
# ---------------------------------------------------------------------------

class TestModeOriginal:
    def test_original_preserves_comments(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="original")
        result = builder.build()
        assert "utility functions" in result.combined_text

    def test_original_saves_with_mode_in_filename(self, simple_project, tmp_path):
        export_dir = tmp_path / "out"
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="original",
            export_directory=str(export_dir),
        )
        result = builder.build()
        saved = builder.save(result)
        assert "original" in saved.name

    def test_original_output_mode_recorded(self, simple_project):
        builder = CodeContextBuilder(project_root=simple_project, output_mode="original")
        result = builder.build()
        assert result.output_mode == "original"


# ---------------------------------------------------------------------------
# Prompt wrapping (all modes)
# ---------------------------------------------------------------------------

class TestPromptWrapping:
    def test_prefix_prepended(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            prompt_prefix="SYSTEM: Please review the following code.",
        )
        result = builder.build()
        assert "SYSTEM: Please review" in result.combined_text

    def test_suffix_appended(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            prompt_suffix="Now provide your analysis.",
        )
        result = builder.build()
        assert "Now provide your analysis." in result.combined_text

    def test_prefix_appears_before_suffix(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            prompt_prefix="START",
            prompt_suffix="END",
        )
        result = builder.build()
        assert result.combined_text.index("START") < result.combined_text.index("END")

    def test_prefix_works_in_tree_only_mode(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="tree_only",
            prompt_prefix="CONTEXT_START",
        )
        result = builder.build()
        assert "CONTEXT_START" in result.combined_text


# ---------------------------------------------------------------------------
# Subdirectory scoping
# ---------------------------------------------------------------------------

class TestSubdirectoryScoping:
    def test_subdirectory_limits_scan(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            subdirectory="src",
        )
        result = builder.build()
        names = {f.name for f in result.files}
        assert "service.py" in names
        assert "main.py" not in names

    def test_subdirectory_tree_shows_scanned_dir(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            subdirectory="src",
        )
        result = builder.build()
        assert "src/" in result.combined_text or "service.py" in result.combined_text


# ---------------------------------------------------------------------------
# Additional files injection
# ---------------------------------------------------------------------------

class TestAdditionalFiles:
    def test_additional_file_included_in_file_list(self, simple_project, tmp_path):
        extra = tmp_path / "extra.py"
        extra.write_text("EXTRA = True\n", encoding="utf-8")
        builder = CodeContextBuilder(
            project_root=simple_project,
            additional_files=[str(extra)],
        )
        result = builder.build()
        assert "extra.py" in {f.name for f in result.files}

    def test_additional_file_content_appears_in_original_mode(self, simple_project, tmp_path):
        extra = tmp_path / "extra.py"
        extra.write_text("EXTRA_MARKER_12345 = True\n", encoding="utf-8")
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="original",
            additional_files=[str(extra)],
        )
        result = builder.build()
        assert "EXTRA_MARKER_12345" in result.combined_text


# ---------------------------------------------------------------------------
# Runtime overrides
# ---------------------------------------------------------------------------

class TestRuntimeOverrides:
    def test_add_extra_exclude_directory(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            overrides={"exclude_directories": {"add": ["src"], "remove": []}},
        )
        result = builder.build()
        assert "service.py" not in {f.name for f in result.files}

    def test_remove_default_exclude(self, simple_project):
        builder = CodeContextBuilder(
            project_root=simple_project,
            overrides={"exclude_files": {"add": [], "remove": ["__init__.py"]}},
        )
        result = builder.build()
        assert "__init__.py" in {f.name for f in result.files}

    def test_include_extensions_whitelist(self, multi_lang_project):
        builder = CodeContextBuilder(
            project_root=multi_lang_project,
            overrides={"include_extensions": {"add": [".py"], "remove": []}},
        )
        result = builder.build()
        names = {f.name for f in result.files}
        assert "app.py" in names
        assert "index.ts" not in names


# ---------------------------------------------------------------------------
# Save to disk
# ---------------------------------------------------------------------------

class TestSaveToDisk:
    def test_save_creates_combined_file(self, simple_project, tmp_path):
        export_dir = tmp_path / "output"
        builder = CodeContextBuilder(
            project_root=simple_project,
            export_directory=str(export_dir),
        )
        result = builder.build()
        saved = builder.save(result)
        assert saved is not None and saved.exists()

    def test_saved_file_contains_tree_and_content(self, simple_project, tmp_path):
        export_dir = tmp_path / "output"
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="original",
            export_directory=str(export_dir),
        )
        result = builder.build()
        saved = builder.save(result)
        text = saved.read_text(encoding="utf-8")
        assert "myproject/" in text
        assert "def main():" in text

    def test_save_creates_export_directory_if_missing(self, simple_project, tmp_path):
        export_dir = tmp_path / "does" / "not" / "exist"
        builder = CodeContextBuilder(
            project_root=simple_project,
            export_directory=str(export_dir),
        )
        result = builder.build()
        builder.save(result)
        assert export_dir.exists()

    def test_individual_save_creates_files(self, simple_project, tmp_path):
        export_dir = tmp_path / "individual_output"
        builder = CodeContextBuilder(
            project_root=simple_project,
            output_mode="clean",
            export_directory=str(export_dir),
        )
        builder.cfg.save_individual = True
        builder.cfg.save_combined = False
        result = builder.build()
        builder.save(result)
        saved_files = list(export_dir.glob("*.txt"))
        assert len(saved_files) == result.stats["total_files"]

    def test_filename_includes_output_mode(self, simple_project, tmp_path):
        for mode in ("tree_only", "signatures", "clean", "original"):
            export_dir = tmp_path / mode
            builder = CodeContextBuilder(
                project_root=simple_project,
                output_mode=mode,
                export_directory=str(export_dir),
            )
            result = builder.build()
            saved = builder.save(result)
            assert mode in saved.name, f"Expected mode '{mode}' in filename '{saved.name}'"


# ---------------------------------------------------------------------------
# Multi-language project
# ---------------------------------------------------------------------------

class TestMultiLangProject:
    def test_default_excludes_txt_and_css(self, multi_lang_project):
        builder = CodeContextBuilder(project_root=multi_lang_project)
        result = builder.build()
        names = {f.name for f in result.files}
        assert "readme.txt" not in names
        assert "style.css" not in names

    def test_py_and_ts_included_when_ts_not_excluded(self, multi_lang_project):
        builder = CodeContextBuilder(
            project_root=multi_lang_project,
            overrides={"exclude_extensions": {"add": [], "remove": [".ts"]}},
        )
        result = builder.build()
        names = {f.name for f in result.files}
        assert "app.py" in names
        assert "index.ts" in names


# ---------------------------------------------------------------------------
# Deep nesting
# ---------------------------------------------------------------------------

class TestDeepNesting:
    def test_all_deep_files_discovered(self, nested_project):
        builder = CodeContextBuilder(
            project_root=nested_project,
            overrides={"exclude_extensions": {"add": [], "remove": []}},
        )
        result = builder.build()
        names = {f.name for f in result.files}
        assert {"deep.py", "shallow.py", "top.py"} <= names

    def test_tree_shows_nested_structure(self, nested_project):
        builder = CodeContextBuilder(
            project_root=nested_project,
            overrides={"exclude_extensions": {"add": [], "remove": []}},
        )
        result = builder.build()
        assert "a/" in result.combined_text
        assert "b/" in result.combined_text

    def test_file_headers_use_relative_paths_original_mode(self, nested_project):
        builder = CodeContextBuilder(
            project_root=nested_project,
            output_mode="original",
            overrides={"exclude_extensions": {"add": [], "remove": []}},
        )
        result = builder.build()
        assert "a/b/c/deep.py" in result.combined_text
