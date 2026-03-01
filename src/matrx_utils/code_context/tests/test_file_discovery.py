"""
Tests for FileDiscovery — the 5-layer exclusion system.

Layer 1: exact directory name match
Layer 2: word-boundary substring match on directory names
Layer 3: exact filename match
Layer 4: word-boundary substring match on filenames
Layer 5: extension blacklist (or whitelist if include_extensions is set)
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from matrx_utils.code_context.code_context import CodeContextConfig, FileDiscovery


def make_cfg(**kwargs) -> CodeContextConfig:
    cfg = CodeContextConfig()
    for k, v in kwargs.items():
        setattr(cfg, k, v)
    return cfg


# ---------------------------------------------------------------------------
# Layer 1: Exact directory name exclusion
# ---------------------------------------------------------------------------

class TestExactDirectoryExclusion:
    def test_excludes_exact_match(self):
        cfg = make_cfg(exclude_directories=["node_modules"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("node_modules") is True

    def test_case_insensitive_exact(self):
        cfg = make_cfg(exclude_directories=["Node_Modules"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("node_modules") is True
        assert fd.should_exclude_directory("NODE_MODULES") is True

    def test_does_not_exclude_partial_name(self):
        cfg = make_cfg(exclude_directories=["test"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("test") is True
        # "test" exact should not affect "mytest" as a whole name
        # (exact match only checks equality, not containment)
        assert fd.should_exclude_directory("mytest") is False

    def test_empty_list_excludes_nothing(self):
        cfg = make_cfg(exclude_directories=[])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("anything") is False

    def test_git_excluded(self):
        cfg = make_cfg(exclude_directories=[".git", "venv", "__pycache__"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory(".git") is True
        assert fd.should_exclude_directory("venv") is True
        assert fd.should_exclude_directory("__pycache__") is True
        assert fd.should_exclude_directory("src") is False


# ---------------------------------------------------------------------------
# Layer 2: Word-boundary substring match on directory names
# ---------------------------------------------------------------------------

class TestDirectorySubstringExclusion:
    def test_word_boundary_match_exact_word(self):
        cfg = make_cfg(exclude_directories_containing=["test"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("test") is True

    def test_word_boundary_match_prefix(self):
        cfg = make_cfg(exclude_directories_containing=["test"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("test_utils") is True
        assert fd.should_exclude_directory("tests") is False  # "tests" — 's' is not a boundary char

    def test_word_boundary_match_suffix(self):
        cfg = make_cfg(exclude_directories_containing=["test"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("unit_test") is True

    def test_word_boundary_does_not_match_mid_word(self):
        cfg = make_cfg(exclude_directories_containing=["test"])
        fd = FileDiscovery(cfg)
        # "protest" — "test" is at the end but preceded by "ro" (not a boundary char)
        assert fd.should_exclude_directory("protest") is False

    def test_word_boundary_dot_separator(self):
        cfg = make_cfg(exclude_directories_containing=["temp"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("my.temp.dir") is True

    def test_word_boundary_dash_separator(self):
        cfg = make_cfg(exclude_directories_containing=["temp"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("my-temp-dir") is True

    def test_multiple_patterns(self):
        cfg = make_cfg(exclude_directories_containing=["temp", "cache"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_directory("temp_files") is True
        assert fd.should_exclude_directory("cache_dir") is True
        assert fd.should_exclude_directory("src") is False


# ---------------------------------------------------------------------------
# Layer 3: Exact filename exclusion
# ---------------------------------------------------------------------------

class TestExactFileExclusion:
    def test_excludes_exact_filename(self):
        cfg = make_cfg(exclude_files=["debug.log", "__init__.py"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("debug.log") is True
        assert fd.should_exclude_file("__init__.py") is True

    def test_case_insensitive_filename(self):
        cfg = make_cfg(exclude_files=["README.md"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("readme.md") is True
        assert fd.should_exclude_file("README.MD") is True

    def test_does_not_exclude_different_file(self):
        cfg = make_cfg(exclude_files=["debug.log"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("app.log") is False
        assert fd.should_exclude_file("main.py") is False


# ---------------------------------------------------------------------------
# Layer 4: Filename substring pattern exclusion
# ---------------------------------------------------------------------------

class TestFilenameSubstringExclusion:
    def test_word_boundary_match_in_filename(self):
        cfg = make_cfg(exclude_files_containing=["initial"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("initial.py") is True
        assert fd.should_exclude_file("initial_setup.py") is True

    def test_word_boundary_no_false_positive(self):
        cfg = make_cfg(exclude_files_containing=["init"])
        fd = FileDiscovery(cfg)
        # "init" at a word boundary
        assert fd.should_exclude_file("init.py") is True
        assert fd.should_exclude_file("init_db.py") is True
        # "initialize" — "init" followed by 'i' (not a boundary char) => no match
        assert fd.should_exclude_file("initialize.py") is False


# ---------------------------------------------------------------------------
# Layer 5: Extension blacklist / whitelist
# ---------------------------------------------------------------------------

class TestExtensionFiltering:
    def test_extension_blacklist(self):
        cfg = make_cfg(exclude_extensions=[".log", ".tmp", ".jpg"], include_extensions=[])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("error.log") is True
        assert fd.should_exclude_file("photo.jpg") is True
        assert fd.should_exclude_file("app.py") is False

    def test_extension_case_insensitive(self):
        cfg = make_cfg(exclude_extensions=[".jpg"], include_extensions=[])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("photo.JPG") is True
        assert fd.should_exclude_file("photo.Jpg") is True

    def test_whitelist_overrides_blacklist(self):
        cfg = make_cfg(
            exclude_extensions=[".py", ".ts"],
            include_extensions=[".py"],
        )
        fd = FileDiscovery(cfg)
        # Only .py is whitelisted — .ts should be excluded
        assert fd.should_exclude_file("app.py") is False
        assert fd.should_exclude_file("app.ts") is True
        assert fd.should_exclude_file("style.css") is True  # not in whitelist

    def test_whitelist_only_allows_listed_extensions(self):
        cfg = make_cfg(include_extensions=[".py", ".ts"])
        fd = FileDiscovery(cfg)
        assert fd.should_exclude_file("main.py") is False
        assert fd.should_exclude_file("component.ts") is False
        assert fd.should_exclude_file("image.png") is True
        assert fd.should_exclude_file("data.json") is True

    def test_no_extension_file_with_blacklist(self):
        cfg = make_cfg(exclude_extensions=[".py"], include_extensions=[])
        fd = FileDiscovery(cfg)
        # File with no extension — not in blacklist, so included
        assert fd.should_exclude_file("Makefile") is False
        assert fd.should_exclude_file("script") is False


# ---------------------------------------------------------------------------
# FileDiscovery.discover() integration tests using temp directories
# ---------------------------------------------------------------------------

class TestDiscoverWithTempDir:
    def test_discovers_files_in_root(self, tmp_path):
        (tmp_path / "main.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def foo(): pass")
        cfg = make_cfg(exclude_extensions=[])
        fd = FileDiscovery(cfg)
        found = fd.discover(tmp_path)
        names = {f.name for f in found}
        assert "main.py" in names
        assert "utils.py" in names

    def test_skips_excluded_directory(self, tmp_path):
        excl = tmp_path / "node_modules"
        excl.mkdir()
        (excl / "pkg.js").write_text("module.exports = {}")
        (tmp_path / "main.py").write_text("pass")
        cfg = make_cfg(exclude_directories=["node_modules"], exclude_extensions=[])
        fd = FileDiscovery(cfg)
        found = fd.discover(tmp_path)
        names = {f.name for f in found}
        assert "main.py" in names
        assert "pkg.js" not in names

    def test_skips_excluded_file(self, tmp_path):
        (tmp_path / "app.py").write_text("pass")
        (tmp_path / "__init__.py").write_text("")
        cfg = make_cfg(exclude_files=["__init__.py"], exclude_extensions=[])
        fd = FileDiscovery(cfg)
        found = fd.discover(tmp_path)
        names = {f.name for f in found}
        assert "app.py" in names
        assert "__init__.py" not in names

    def test_subdirectory_restricts_scan(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        (src / "app.py").write_text("pass")
        (tmp_path / "top.py").write_text("pass")
        cfg = make_cfg(exclude_extensions=[])
        fd = FileDiscovery(cfg)
        found = fd.discover(tmp_path, subdirectory="src")
        names = {f.name for f in found}
        assert "app.py" in names
        assert "top.py" not in names

    def test_additional_files_injected(self, tmp_path):
        (tmp_path / "main.py").write_text("pass")
        extra = tmp_path / "extra" / "special.py"
        extra.parent.mkdir()
        extra.write_text("pass")
        cfg = make_cfg(exclude_extensions=[])
        fd = FileDiscovery(cfg)
        found = fd.discover(tmp_path, additional_files=[str(extra)])
        names = {f.name for f in found}
        assert "main.py" in names
        assert "special.py" in names

    def test_nonexistent_root_returns_empty(self, tmp_path):
        cfg = make_cfg()
        fd = FileDiscovery(cfg)
        found = fd.discover(tmp_path / "does_not_exist")
        assert found == []

    def test_analyze_returns_correct_stats(self, tmp_path):
        (tmp_path / "a.py").write_text("pass")
        (tmp_path / "b.py").write_text("pass")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "c.ts").write_text("const x = 1;")
        cfg = make_cfg(exclude_extensions=[])
        fd = FileDiscovery(cfg)
        files = fd.discover(tmp_path)
        stats = fd.analyze(files)
        assert stats["total_files"] == 3
        assert stats["total_directories"] == 2
        assert stats["file_types"][".py"] == 2
        assert stats["file_types"][".ts"] == 1


# ---------------------------------------------------------------------------
# Dynamic exclusion override (add/remove)
# ---------------------------------------------------------------------------

class TestConfigOverrides:
    def test_add_exclude_directory(self):
        cfg = CodeContextConfig.from_yaml(overrides={
            "exclude_directories": {"add": ["my_custom_dir"], "remove": []},
        })
        assert "my_custom_dir" in cfg.exclude_directories

    def test_remove_exclude_directory(self):
        cfg = CodeContextConfig.from_yaml(overrides={
            "exclude_directories": {"add": [], "remove": ["migrations"]},
        })
        assert "migrations" not in cfg.exclude_directories

    def test_add_include_extension(self):
        cfg = CodeContextConfig.from_yaml(overrides={
            "include_extensions": {"add": [".py", ".ts"], "remove": []},
        })
        assert ".py" in cfg.include_extensions
        assert ".ts" in cfg.include_extensions

    def test_no_duplicate_on_repeated_add(self):
        cfg = CodeContextConfig.from_yaml(overrides={
            "exclude_directories": {"add": [".git", ".git"], "remove": []},
        })
        assert cfg.exclude_directories.count(".git") == 1

    def test_remove_nonexistent_is_safe(self):
        cfg = CodeContextConfig.from_yaml(overrides={
            "exclude_directories": {"add": [], "remove": ["definitely_not_here"]},
        })
        assert "definitely_not_here" not in cfg.exclude_directories
