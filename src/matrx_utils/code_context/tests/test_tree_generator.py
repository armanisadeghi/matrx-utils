"""
Tests for DirectoryTree.

Covers:
- Sparse mode (only dirs with included files)
- Full mode (all dirs under root, with exclusion filtering)
- Custom root override
- Unicode box-drawing characters
- Single file / empty file list edge cases
- Cross-platform path handling (Path objects)
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from utils.code_context.code_context import CodeContextConfig, DirectoryTree


def make_cfg(**kwargs) -> CodeContextConfig:
    cfg = CodeContextConfig()
    for k, v in kwargs.items():
        setattr(cfg, k, v)
    return cfg


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def build_tree(
    files: list[Path],
    cfg: CodeContextConfig | None = None,
    custom_root=None,
    scan_root=None,
) -> str:
    if cfg is None:
        cfg = make_cfg(show_all_tree_directories=False)
    return DirectoryTree(files, cfg, custom_root, scan_root=scan_root).generate()


# ---------------------------------------------------------------------------
# Basic structure tests
# ---------------------------------------------------------------------------

class TestTreeBasicStructure:
    def test_empty_file_list(self):
        cfg = make_cfg()
        result = build_tree([], cfg)
        assert "(no files included)" in result

    def test_single_file_in_root(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("pass")
        result = build_tree([f])
        assert "main.py" in result
        # Root directory name should appear
        assert tmp_path.name + "/" in result

    def test_multiple_files_appear(self, tmp_path):
        files = []
        for name in ["a.py", "b.py", "c.ts"]:
            p = tmp_path / name
            p.write_text("pass")
            files.append(p)
        result = build_tree(files)
        assert "a.py" in result
        assert "b.py" in result
        assert "c.ts" in result

    def test_nested_files_appear(self, tmp_path):
        sub = tmp_path / "src" / "utils"
        sub.mkdir(parents=True)
        f = sub / "helpers.py"
        f.write_text("pass")
        # Pass scan_root=tmp_path so the tree is rooted at tmp_path, not the deepest common path
        result = build_tree([f], scan_root=tmp_path)
        assert "src/" in result
        assert "utils/" in result
        assert "helpers.py" in result

    def test_unicode_box_drawing(self, tmp_path):
        f = tmp_path / "app.py"
        f.write_text("pass")
        result = build_tree([f])
        assert "├──" in result

    def test_root_name_ends_with_slash(self, tmp_path):
        f = tmp_path / "main.py"
        f.write_text("pass")
        result = build_tree([f])
        first_line = result.splitlines()[0]
        assert first_line.endswith("/")


# ---------------------------------------------------------------------------
# Sparse mode (default: show_all_tree_directories=False)
# ---------------------------------------------------------------------------

class TestSparseMode:
    def test_does_not_show_empty_sibling_dir(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        empty = tmp_path / "empty_dir"
        empty.mkdir()
        f = src / "app.py"
        f.write_text("pass")
        cfg = make_cfg(show_all_tree_directories=False)
        result = build_tree([f], cfg)
        assert "src/" in result
        assert "empty_dir" not in result

    def test_only_shows_paths_that_lead_to_included_files(self, tmp_path):
        a = tmp_path / "featureA" / "logic.py"
        a.parent.mkdir()
        a.write_text("pass")
        b_dir = tmp_path / "featureB"
        b_dir.mkdir()
        cfg = make_cfg(show_all_tree_directories=False)
        result = build_tree([a], cfg)
        assert "featureA/" in result
        assert "featureB" not in result


# ---------------------------------------------------------------------------
# Full mode (show_all_tree_directories=True)
# ---------------------------------------------------------------------------

class TestFullMode:
    def test_shows_empty_sibling_dir(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        empty = tmp_path / "empty_dir"
        empty.mkdir()
        f = src / "app.py"
        f.write_text("pass")
        cfg = make_cfg(
            show_all_tree_directories=True,
            exclude_directories=[],
            exclude_directories_containing=[],
        )
        # Must pass scan_root=tmp_path so the tree walks from the project root
        # and discovers empty_dir alongside src
        result = build_tree([f], cfg, scan_root=tmp_path)
        assert "src/" in result
        assert "empty_dir/" in result

    def test_excluded_dirs_not_shown_in_full_mode(self, tmp_path):
        src = tmp_path / "src"
        src.mkdir()
        excl = tmp_path / "node_modules"
        excl.mkdir()
        f = src / "app.py"
        f.write_text("pass")
        cfg = make_cfg(
            show_all_tree_directories=True,
            exclude_directories=["node_modules"],
        )
        result = build_tree([f], cfg)
        assert "node_modules" not in result


# ---------------------------------------------------------------------------
# Custom root override
# ---------------------------------------------------------------------------

class TestCustomRoot:
    def test_custom_root_overrides_common_prefix(self, tmp_path):
        project = tmp_path / "myproject"
        src = project / "src"
        src.mkdir(parents=True)
        f = src / "main.py"
        f.write_text("pass")
        cfg = make_cfg()
        result = build_tree([f], cfg, custom_root=project)
        # First line should be "myproject/"
        assert result.splitlines()[0] == "myproject/"
        assert "src/" in result
        assert "main.py" in result

    def test_custom_root_different_from_file_location(self, tmp_path):
        root = tmp_path / "root"
        deep = root / "a" / "b" / "c"
        deep.mkdir(parents=True)
        f = deep / "file.py"
        f.write_text("pass")
        cfg = make_cfg()
        result = build_tree([f], cfg, custom_root=root)
        assert "root/" in result.splitlines()[0]


# ---------------------------------------------------------------------------
# Sorting and ordering
# ---------------------------------------------------------------------------

class TestTreeOrdering:
    def test_entries_sorted_alphabetically(self, tmp_path):
        for name in ["z_file.py", "a_file.py", "m_file.py"]:
            (tmp_path / name).write_text("pass")
        result = build_tree([tmp_path / n for n in ["z_file.py", "a_file.py", "m_file.py"]])
        lines = result.splitlines()
        file_lines = [l for l in lines if "file.py" in l]
        names = [l.split("── ")[-1] for l in file_lines]
        assert names == sorted(names)

    def test_directories_before_files(self, tmp_path):
        sub = tmp_path / "alpha"
        sub.mkdir()
        f_sub = sub / "util.py"
        f_sub.write_text("pass")
        f_root = tmp_path / "beta.py"
        f_root.write_text("pass")
        result = build_tree([f_sub, f_root])
        lines = result.splitlines()
        entries = [l.split("── ")[-1] for l in lines if "── " in l]
        # "alpha/" should appear before "beta.py" due to sorted order ('a' < 'b')
        alpha_idx = next(i for i, e in enumerate(entries) if "alpha" in e)
        beta_idx = next(i for i, e in enumerate(entries) if "beta" in e)
        assert alpha_idx < beta_idx


# ---------------------------------------------------------------------------
# Depth and indentation
# ---------------------------------------------------------------------------

class TestTreeIndentation:
    def test_depth_indentation_uses_pipe_chars(self, tmp_path):
        deep = tmp_path / "level1" / "level2" / "level3"
        deep.mkdir(parents=True)
        f = deep / "file.py"
        f.write_text("pass")
        # Use scan_root=tmp_path so the tree starts from the top
        result = build_tree([f], scan_root=tmp_path)
        file_line = next(l for l in result.splitlines() if "file.py" in l)
        # file is 3 dirs deep → line should be indented with "│   " prefix
        assert "│   " in file_line

    def test_multiple_files_same_dir_all_appear(self, tmp_path):
        sub = tmp_path / "pkg"
        sub.mkdir()
        files = []
        for name in ["a.py", "b.py", "c.py"]:
            p = sub / name
            p.write_text("pass")
            files.append(p)
        result = build_tree(files)
        for name in ["a.py", "b.py", "c.py"]:
            assert name in result
