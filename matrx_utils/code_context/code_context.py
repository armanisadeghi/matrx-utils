"""
Code Context Tool
=================
Produces LLM-ready code context from a directory at four levels of detail,
controlled by a single ``output_mode`` setting.

Output Modes
------------
"tree_only"   Directory tree + header only. No file content.
              ~1% of full token cost. Best for: orientation, "what files exist?"

"signatures"  Tree + code skeleton: function/class/method signatures with args, no bodies.
              ~5-10% of full token cost. Best for: full API map, understanding dependencies.
              Supports: Python (AST), TypeScript/JavaScript (regex), Go, Rust, Java, C/C++,
              Ruby, PHP, Swift, Kotlin, C#, Scala, Dart, Lua, and more via generic fallback.

"clean"       Tree + full file content with comments stripped.
              ~70-80% of full token cost. Best for: code review, editing tasks.

"original"    Tree + raw file content, nothing modified.
              100% of token cost. Best for: debugging, when comments matter.

Usage (programmatic)
--------------------
    builder = CodeContextBuilder(
        project_root="/path/to/project",
        subdirectory="src",
        output_mode="signatures",
        preset="my_preset",            # optional: named preset from config.yaml
        overrides={
            "exclude_directories": {"add": ["my_dir"], "remove": ["docs"]},
            "include_extensions":  {"add": [".py"]},   # whitelist mode
            "include_directories": {"add": ["src"]},   # allowlist: only these dirs
        },
        additional_files=["/abs/path/extra.py"],
        custom_root="/path/to/project/src",
        show_all_tree_directories=True,
        prune_empty_directories=True,
        prompt_prefix="Please review this code...",
        prompt_suffix="What do you think?",
    )
    result = builder.build()
    builder.save(result)
    print(result.combined_text)

Config defaults live in config.yaml next to this file.
Named presets in config.yaml let you store reusable exclusion profiles.
Runtime kwargs override config.yaml values.
"""

from __future__ import annotations

import ast
import logging
import os
import re
import sys
import warnings
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

try:
    import yaml
except ImportError:
    print("PyYAML is required: uv pip install pyyaml", file=sys.stderr)
    sys.exit(1)

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent / "config.yaml"

OutputMode = Literal["tree_only", "signatures", "clean", "original"]

_OUTPUT_MODE_LABELS: dict[str, str] = {
    "tree_only":  "tree only  — directory structure, no file content",
    "signatures": "signatures — code skeleton (functions/classes/methods, no bodies)",
    "clean":      "clean      — full content with comments stripped",
    "original":   "original   — full content, unmodified",
}

# ---------------------------------------------------------------------------
# Call graph — default noise filter (tier-1 builtins + stdlib)
# Callers can add project-specific noise via call_graph_ignore or config.yaml
# call_graph_project_noise key.
# ---------------------------------------------------------------------------
_DEFAULT_CALL_GRAPH_IGNORE: frozenset[str] = frozenset({
    # builtins
    "isinstance", "len", "str", "int", "float", "bool", "list", "dict",
    "set", "tuple", "type", "hasattr", "getattr", "setattr", "vars",
    "dir", "any", "all", "next", "iter", "zip", "enumerate", "range",
    "sorted", "reversed", "sum", "max", "min", "abs", "round",
    "super", "print", "repr", "hash",
    # exceptions
    "ValueError", "TypeError", "RuntimeError", "KeyError",
    "AttributeError", "IndexError", "StopIteration",
    "NotImplementedError", "Exception",
    # stdlib noise
    "defaultdict", "uuid4", "Field",
})


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

@dataclass
class CodeContextConfig:
    """
    Merged configuration: config.yaml base → named preset → runtime overrides.

    Exclusion/inclusion override format (used in CodeContextBuilder overrides kwarg):
        {
            "exclude_directories":            {"add": [...], "remove": [...]},
            "exclude_directories_containing": {"add": [...], "remove": [...]},
            "exclude_files":                  {"add": [...], "remove": [...]},
            "exclude_files_containing":       {"add": [...], "remove": [...]},
            "exclude_extensions":             {"add": [...], "remove": [...]},
            "include_extensions":             {"add": [...], "remove": [...]},
            "include_directories":            {"add": [...], "remove": [...]},
            "include_files":                  {"add": [...], "remove": [...]},
        }

    Allowlists (include_*):
        include_extensions  — if non-empty, ONLY files with these extensions are kept
        include_directories — if non-empty, ONLY directories with these names are traversed
        include_files       — if non-empty, ONLY files with these exact names are kept
    """

    # Exclusion lists
    exclude_directories: list[str] = field(default_factory=list)
    exclude_directories_containing: list[str] = field(default_factory=list)
    exclude_files: list[str] = field(default_factory=list)
    exclude_files_containing: list[str] = field(default_factory=list)
    exclude_extensions: list[str] = field(default_factory=list)

    # Allowlists (whitelist mode — empty means "allow all")
    include_extensions: list[str] = field(default_factory=list)
    include_directories: list[str] = field(default_factory=list)
    include_files: list[str] = field(default_factory=list)

    # Output settings
    save_combined: bool = True
    save_individual: bool = False
    export_directory: str = "./output"
    output_mode: OutputMode = "clean"
    show_all_tree_directories: bool = False
    prune_empty_directories: bool = False
    include_text_output: bool = True
    project_root_display: bool = True

    # Call graph settings
    call_graph_project_noise: list[str] = field(default_factory=list)

    # React / downstream analysis config
    extensions_for_analysis: list[str] = field(default_factory=lambda: [".js", ".jsx", ".ts", ".tsx", ".mjs"])
    remove_comments_for_extensions: list[str] = field(default_factory=lambda: [".js", ".jsx", ".ts", ".tsx"])
    alias_map: dict[str, str] = field(default_factory=dict)
    include_export_types: list[str] = field(default_factory=lambda: ["const", "function", "type", "interface"])
    ignore_export_list: list[str] = field(default_factory=list)

    @classmethod
    def from_yaml(
        cls,
        config_path: Path = _CONFIG_PATH,
        preset: str | None = None,
        overrides: dict | None = None,
    ) -> "CodeContextConfig":
        raw: dict = {}
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}
        else:
            logger.warning("config.yaml not found at %s; using built-in defaults", config_path)

        excl_dirs = raw.get("exclude_directories", {})
        excl_files = raw.get("exclude_files", {})
        out = raw.get("output", {})

        cfg = cls(
            exclude_directories=list(excl_dirs.get("exact", [])),
            exclude_directories_containing=list(excl_dirs.get("containing", [])),
            exclude_files=list(excl_files.get("exact", [])),
            exclude_files_containing=list(excl_files.get("containing", [])),
            exclude_extensions=list(raw.get("exclude_extensions", [])),
            include_extensions=list(raw.get("include_extensions", [])),
            include_directories=list(raw.get("include_directories", [])),
            include_files=list(raw.get("include_files", [])),
            save_combined=bool(out.get("save_combined", True)),
            save_individual=bool(out.get("save_individual", False)),
            export_directory=str(out.get("export_directory", "./output")),
            output_mode=out.get("output_mode", out.get("content_type", "clean")),
            show_all_tree_directories=bool(out.get("show_all_tree_directories", False)),
            prune_empty_directories=bool(out.get("prune_empty_directories", False)),
            include_text_output=bool(out.get("include_text_output", True)),
            project_root_display=bool(out.get("project_root_display", True)),
            call_graph_project_noise=list(raw.get("call_graph_project_noise", [])),
            extensions_for_analysis=list(raw.get("extensions_for_analysis", [".js", ".jsx", ".ts", ".tsx", ".mjs"])),
            remove_comments_for_extensions=list(raw.get("remove_comments_for_extensions", [".js", ".jsx", ".ts", ".tsx"])),
            alias_map=dict(raw.get("alias_map", {})),
            include_export_types=list(raw.get("include_export_types", ["const", "function", "type", "interface"])),
            ignore_export_list=list(raw.get("ignore_export_list", [])),
        )

        # Apply named preset on top of base config
        if preset:
            cfg._apply_preset(raw, preset)

        # Apply runtime overrides last (highest priority)
        if overrides:
            cfg._apply_overrides(overrides)

        return cfg

    def _apply_preset(self, raw: dict, preset_name: str) -> None:
        """
        Apply a named preset from config.yaml.

        Preset format in config.yaml:
            presets:
              my_preset:
                override: false   # if true, replaces lists; if false, merges them
                exclude_directories:
                  exact: [...]
                  containing: [...]
                include_extensions: [...]
                output:
                  output_mode: "signatures"
        """
        presets: dict = raw.get("presets", {})
        preset_data: dict = presets.get(preset_name, {})
        if not preset_data:
            logger.warning("Preset '%s' not found in config.yaml; ignoring.", preset_name)
            return

        do_override = preset_data.get("override", False)

        field_sources: list[tuple[str, str]] = [
            ("exclude_directories.exact",       "exclude_directories"),
            ("exclude_directories.containing",  "exclude_directories_containing"),
            ("exclude_files.exact",             "exclude_files"),
            ("exclude_files.containing",        "exclude_files_containing"),
            ("exclude_extensions",              "exclude_extensions"),
            ("include_extensions",              "include_extensions"),
            ("include_directories",             "include_directories"),
            ("include_files",                   "include_files"),
        ]

        for yaml_path, attr in field_sources:
            keys = yaml_path.split(".")
            value = preset_data
            for k in keys:
                if not isinstance(value, dict):
                    value = None
                    break
                value = value.get(k)
            if value is None:
                continue
            items = list(value) if isinstance(value, list) else [value]
            target: list = getattr(self, attr)
            if do_override:
                setattr(self, attr, items)
            else:
                for item in items:
                    if item and item not in target:
                        target.append(item)

        preset_out: dict = preset_data.get("output", {})
        for key in ("output_mode", "show_all_tree_directories", "prune_empty_directories",
                    "save_combined", "save_individual", "export_directory",
                    "include_text_output", "project_root_display"):
            if key in preset_out:
                setattr(self, key, preset_out[key])

    def _apply_overrides(self, overrides: dict) -> None:
        list_fields = {
            "exclude_directories":            "exclude_directories",
            "exclude_directories_containing": "exclude_directories_containing",
            "exclude_files":                  "exclude_files",
            "exclude_files_containing":       "exclude_files_containing",
            "exclude_extensions":             "exclude_extensions",
            "include_extensions":             "include_extensions",
            "include_directories":            "include_directories",
            "include_files":                  "include_files",
        }
        for key, attr in list_fields.items():
            if key not in overrides:
                continue
            ops = overrides[key]
            target: list = getattr(self, attr)
            for item in ops.get("add", []):
                if item and item not in target:
                    target.append(item)
            for item in ops.get("remove", []):
                if item in target:
                    target.remove(item)

        # Allow scalar overrides too
        scalar_fields = (
            "output_mode", "show_all_tree_directories", "prune_empty_directories",
            "save_combined", "save_individual", "export_directory",
            "include_text_output", "project_root_display",
        )
        for key in scalar_fields:
            if key in overrides:
                setattr(self, key, overrides[key])


# ---------------------------------------------------------------------------
# File Discovery
# ---------------------------------------------------------------------------

def _word_boundary_pattern(word: str) -> re.Pattern:
    return re.compile(r"(^|[_\- .])" + re.escape(word) + r"([_\- .]|$)", re.IGNORECASE)


class FileDiscovery:
    """
    Discovers files under a root directory using a layered filter system.

    Exclusion layers (applied in order):
      1. Exact directory name match (case-insensitive)
      2. Word-boundary substring match on directory names
      3. Allowlist: if include_directories is set, only those directories are traversed
      4. Exact filename match (case-insensitive)
      5. Word-boundary substring match on filenames
      6. Allowlist: if include_files is set, only those filenames are kept
      7. Extension: blacklist (exclude_extensions) OR whitelist (include_extensions)
    """

    def __init__(self, cfg: CodeContextConfig) -> None:
        self._cfg = cfg
        self._dir_exact: set[str] = {d.lower() for d in cfg.exclude_directories}
        self._dir_patterns: list[re.Pattern] = [_word_boundary_pattern(w) for w in cfg.exclude_directories_containing]
        self._dir_allowlist: set[str] = {d.lower() for d in cfg.include_directories}
        self._file_exact: set[str] = {f.lower() for f in cfg.exclude_files}
        self._file_patterns: list[re.Pattern] = [_word_boundary_pattern(w) for w in cfg.exclude_files_containing]
        self._file_allowlist: set[str] = {f.lower() for f in cfg.include_files}
        self._excl_ext: set[str] = {e.lower() for e in cfg.exclude_extensions}
        self._incl_ext: set[str] = {e.lower() for e in cfg.include_extensions}

    def should_exclude_directory(self, dirname: str) -> bool:
        low = dirname.lower()
        if low in self._dir_exact:
            return True
        for pat in self._dir_patterns:
            if pat.search(low):
                return True
        # Allowlist: if set, exclude anything not in it
        if self._dir_allowlist and low not in self._dir_allowlist:
            return True
        return False

    def should_exclude_file(self, filename: str) -> bool:
        low = filename.lower()
        if low in self._file_exact:
            return True
        for pat in self._file_patterns:
            if pat.search(low):
                return True
        # Allowlist: if set, exclude anything not in it
        if self._file_allowlist and low not in self._file_allowlist:
            return True
        ext = Path(filename).suffix.lower()
        if self._incl_ext:
            return ext not in self._incl_ext
        return ext in self._excl_ext

    def discover(
        self,
        root: str | Path,
        subdirectory: str | None = None,
        additional_files: list[str] | None = None,
    ) -> list[Path]:
        root = Path(root)
        if subdirectory:
            normalized = Path(os.path.normpath(subdirectory.lstrip("/\\")))
            target = root / normalized
        else:
            target = root

        if not target.exists():
            logger.warning("Discovery target does not exist: %s", target)
            return []

        found: list[Path] = []
        excluded_ext_counts: dict[str, int] = defaultdict(int)

        for dirpath, dirnames, filenames in os.walk(target):
            dirnames[:] = [d for d in dirnames if not self.should_exclude_directory(d)]
            for fname in filenames:
                fp = Path(dirpath) / fname
                if not fp.is_file():
                    continue
                if self.should_exclude_file(fname):
                    # Count by extension so the tree can show an excluded-files summary.
                    # Only count files that pass directory filters (i.e. "normal" files
                    # that were intentionally excluded by extension/name rules, not system
                    # noise from excluded directories).
                    ext = fp.suffix.lower() or "(no ext)"
                    excluded_ext_counts[ext] += 1
                else:
                    found.append(fp)

        # Expose excluded counts so callers (e.g. tree builder) can report them.
        self._last_excluded_counts: dict[str, int] = dict(excluded_ext_counts)

        if additional_files:
            seen = set(found)
            for af in additional_files:
                p = Path(af)
                if p.is_file() and p not in seen:
                    found.append(p)
                    seen.add(p)

        return found

    def analyze(self, files: list[Path]) -> dict:
        ext_counts: dict[str, int] = defaultdict(int)
        dirs: set[Path] = set()
        for f in files:
            dirs.add(f.parent)
            ext = f.suffix or "(no extension)"
            ext_counts[ext] += 1
        return {
            "total_files": len(files),
            "total_directories": len(dirs),
            "file_types": dict(sorted(ext_counts.items())),
        }


# ---------------------------------------------------------------------------
# Directory Tree
# ---------------------------------------------------------------------------

class DirectoryTree:
    """
    Generates a Unicode directory tree from a list of file paths.

    Modes:
    - sparse (default): only directories that contain included files
    - full (show_all_tree_directories=True): all directories under root,
      applying the same exclusion filters from FileDiscovery
    - prune (prune_empty_directories=True): removes any directory node that
      contains no files and no subdirectories with files (post-walk pruning)

    Root resolution priority:
    1. custom_root — explicit override
    2. scan_root   — the root used for file discovery (preserves full structure)
    3. common path of all included files
    """

    def __init__(
        self,
        files: list[Path],
        cfg: CodeContextConfig,
        custom_root: str | Path | None = None,
        scan_root: str | Path | None = None,
    ) -> None:
        self._files = files
        self._cfg = cfg
        self._custom_root = Path(custom_root) if custom_root else None
        self._scan_root = Path(scan_root) if scan_root else None
        self._discovery = FileDiscovery(cfg)

    def generate(self, project_root: Path | None = None) -> str:
        if not self._files:
            return "(no files included)\n"

        root = self._resolve_root()
        structure: dict = {}
        self._build_file_nodes(structure, root)

        if self._cfg.show_all_tree_directories:
            self._add_all_dirs(root, structure)

        if self._cfg.prune_empty_directories:
            self._prune(structure)

        # project_root_display: show relative path from project root rather than bare dirname
        if project_root and self._cfg.project_root_display:
            try:
                label = str(root.relative_to(project_root)).replace("\\", "/") + "/"
            except ValueError:
                label = root.name + "/"
        else:
            label = root.name + "/"

        lines = [label]
        self._render(structure, lines, depth=0)
        return "\n".join(lines)

    def _resolve_root(self) -> Path:
        if self._custom_root:
            return self._custom_root
        if self._scan_root:
            return self._scan_root
        common = Path(os.path.commonpath([str(f) for f in self._files]))
        return common if common.is_dir() else common.parent

    def _build_file_nodes(self, structure: dict, root: Path) -> None:
        for f in self._files:
            try:
                rel = f.relative_to(root)
            except ValueError:
                rel = Path(f.name)
            parts = rel.parts
            node = structure
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = None

    def _add_all_dirs(self, root: Path, structure: dict) -> None:
        for dirpath, dirnames, _ in os.walk(root):
            dirnames[:] = [d for d in dirnames if not self._discovery.should_exclude_directory(d)]
            rel = Path(dirpath).relative_to(root)
            if str(rel) == ".":
                continue
            node = structure
            for part in rel.parts:
                node = node.setdefault(part, {})

    def _prune(self, node: dict) -> bool:
        """
        Recursively removes directory entries that contain no files and no
        non-empty subdirectories. Returns True if the node has any content.
        """
        keys_to_delete = []
        for key, value in list(node.items()):
            if value is None:
                continue  # file node — keep
            if not self._prune(value):
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del node[key]
        return bool(node)

    def _render(self, node: dict, lines: list[str], depth: int) -> None:
        indent = "│   " * depth
        for name, children in sorted(node.items()):
            if children is None:
                lines.append(f"{indent}├── {name}")
            else:
                lines.append(f"{indent}├── {name}/")
                self._render(children, lines, depth + 1)


# ---------------------------------------------------------------------------
# Code Extractor
# ---------------------------------------------------------------------------

class CodeExtractor:
    """
    Reads a single file, strips comments/docstrings, and optionally holds
    modified content for programmatic injection.

    Comment stripping covers:
    - Python:      # line comments, triple-quoted strings (docstrings)
    - JS/TS/CSS/Go/C/C++/Java/Rust/Swift/Kotlin/C#/PHP: // and /* */
    - Lua:         -- single-line and --[[ block ]]
    - HTML/XML:    <!-- -->
    - Ruby/Shell:  # (already covered by Python rule)
    """

    def __init__(self, file_path: str | Path) -> None:
        self.path = Path(file_path)
        self.original: str | None = None
        self.clean: str | None = None
        self._original_chars: int = 0
        self._clean_chars: int = 0
        self._load()

    def _load(self) -> None:
        try:
            self.original = self.path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                self.original = self.path.read_text(encoding="latin-1")
            except Exception as exc:
                logger.error("Cannot read %s: %s", self.path, exc)
                self.original = None
        except Exception as exc:
            logger.error("Cannot read %s: %s", self.path, exc)
            self.original = None
        self._original_chars = len(self.original) if self.original else 0

    def strip_comments(self) -> str | None:
        if self.original is None:
            return None
        text = self.original

        # Python triple-quoted strings (docstrings) — must come before # removal
        text = re.sub(r"'''[\s\S]*?'''", "", text)
        text = re.sub(r'"""[\s\S]*?"""', "", text)
        # Python / Ruby / Shell single-line comments
        text = re.sub(r"#[^\n]*", "", text)

        # Block comments: JS/TS/CSS/Go/C/C++/Java/Rust/Swift/Kotlin/C#/PHP
        text = re.sub(r"/\*[\s\S]*?\*/", "", text)
        # Line comments: JS/TS/Go/C/C++/Java/Rust/Swift/Kotlin/C#/PHP
        text = re.sub(r"//[^\n]*", "", text)

        # Lua block comments
        text = re.sub(r"--\[\[[\s\S]*?\]\]", "", text)
        # Lua single-line comments
        text = re.sub(r"--[^\n]*", "", text)

        # HTML/XML comments
        text = re.sub(r"<!--[\s\S]*?-->", "", text)

        # Collapse 3+ blank lines to 2
        text = re.sub(r"\n[ \t]*\n[ \t]*\n+", "\n\n", text)

        self.clean = text
        self._clean_chars = len(text)
        return text

    def get_content(self, mode: OutputMode) -> str | None:
        if mode == "clean":
            return self.clean if self.clean is not None else self.original
        return self.original

    def update_contents(self, new_contents: str) -> None:
        """Replace original content in-memory (does not write to disk)."""
        self.original = new_contents
        self._original_chars = len(new_contents)
        self.clean = None
        self._clean_chars = 0

    def refresh_contents(self) -> None:
        """Re-read content from disk, discarding any in-memory edits."""
        self.clean = None
        self._clean_chars = 0
        self._load()

    @property
    def char_counts(self) -> dict[str, int]:
        return {"original": self._original_chars, "clean": self._clean_chars}

    def file_header(self, project_root: Path | None = None, language: str | None = None) -> str:
        display = self._relative_display(project_root)
        lang_tag = f"  [{language}]" if language else ""
        return f"\n\n---\nFilepath: {display}{lang_tag}\n\n"

    def _relative_display(self, project_root: Path | None) -> str:
        if project_root:
            try:
                return str(self.path.relative_to(project_root)).replace("\\", "/")
            except ValueError:
                pass
        return str(self.path)


# ---------------------------------------------------------------------------
# Signature Extractor — multi-language
# ---------------------------------------------------------------------------

@dataclass
class SignatureBlock:
    """One file's worth of extracted signatures."""
    file_path: Path
    language: str
    signatures: list[str] = field(default_factory=list)
    note: str | None = None

    def to_text(self, project_root: Path | None = None) -> str:
        if project_root:
            try:
                display = str(self.file_path.relative_to(project_root)).replace("\\", "/")
            except ValueError:
                display = str(self.file_path)
        else:
            display = str(self.file_path)

        lines = [f"\n\n---\nFilepath: {display}  [{self.language}]\n"]
        if self.note:
            lines.append(f"  # {self.note}")
        lines.extend(f"  {s}" for s in self.signatures)
        return "\n".join(lines)


_LANG_MAP: dict[str, str] = {
    ".py":    "python",
    ".ts":    "typescript",
    ".tsx":   "typescript",
    ".js":    "javascript",
    ".jsx":   "javascript",
    ".mjs":   "javascript",
    ".go":    "go",
    ".rs":    "rust",
    ".java":  "java",
    ".kt":    "kotlin",
    ".kts":   "kotlin",
    ".swift": "swift",
    ".c":     "c",
    ".h":     "c",
    ".cpp":   "cpp",
    ".cc":    "cpp",
    ".cxx":   "cpp",
    ".hpp":   "cpp",
    ".cs":    "csharp",
    ".rb":    "ruby",
    ".php":   "php",
    ".lua":   "lua",
    ".r":     "r",
    ".scala": "scala",
    ".ex":    "elixir",
    ".exs":   "elixir",
    ".hs":    "haskell",
    ".erl":   "erlang",
    ".dart":  "dart",
}

_SUPPORTED_LANGS = {
    "python", "typescript", "javascript", "go", "rust",
    "java", "kotlin", "swift", "c", "cpp", "csharp",
    "ruby", "php", "lua", "scala", "dart",
}

_SIG_PATTERNS: dict[str, list[re.Pattern]] = {

    "python": [
        re.compile(r"^(class\s+\w[\w\d]*(?:\s*\([^)]*\))?\s*:)", re.MULTILINE),
        re.compile(r"^(\s*(?:async\s+)?def\s+\w[\w\d]*\s*\([^)]*\)\s*(?:->\s*[^:]+)?:)", re.MULTILINE),
    ],

    "typescript": [
        re.compile(r"^(?:export\s+)?(?:abstract\s+)?(?:class|interface|enum|type)\s+\w[\w\d]*[^{;]*", re.MULTILINE),
        re.compile(r"^(?:export\s+)?(?:async\s+)?function\s*\*?\s*\w[\w\d]*\s*(?:<[^>]*>)?\s*\([^)]*\)[^{;]*", re.MULTILINE),
        re.compile(r"^\s+(?:(?:public|private|protected|static|async|readonly|abstract|override)\s+)*(?:readonly\s+)?(?:\w[\w\d]*)\s*(?:<[^>]*>)?\s*\([^)]*\)\s*(?::\s*[^{;]+)?(?=\s*\{|\s*;)", re.MULTILINE),
        re.compile(r"^(?:export\s+)?const\s+\w[\w\d]*\s*=\s*(?:async\s+)?\([^)]*\)\s*(?::\s*(?:Promise<[^>]+>|\w[\w\d<>|?,\s\[\]]+))?\s*=>", re.MULTILINE),
    ],

    "javascript": [
        re.compile(r"^(?:export\s+)?(?:class|extends)\s+\w[\w\d]*[^{;]*", re.MULTILINE),
        re.compile(r"^(?:export\s+)?(?:async\s+)?function\s*\*?\s*\w[\w\d]*\s*\([^)]*\)", re.MULTILINE),
        re.compile(r"^\s+(?:async\s+)?\w[\w\d]*\s*\([^)]*\)\s*(?=\{)", re.MULTILINE),
        re.compile(r"^(?:export\s+)?const\s+\w[\w\d]*\s*=\s*(?:async\s+)?\([^)]*\)\s*=>", re.MULTILINE),
    ],

    "go": [
        re.compile(r"^func\s+(?:\([^)]+\)\s+)?\w[\w\d]*\s*\([^)]*\)[^{]*", re.MULTILINE),
        re.compile(r"^type\s+\w[\w\d]*\s+(?:struct|interface)[^{]*", re.MULTILINE),
    ],

    "rust": [
        re.compile(r"^(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?fn\s+\w[\w\d]*[^{]*", re.MULTILINE),
        re.compile(r"^(?:pub\s+)?(?:struct|enum|trait|impl(?:\s+\w[\w\d]*)?)\s+\w[\w\d]*[^{]*", re.MULTILINE),
    ],

    "java": [
        re.compile(r"^(?:\s+)?(?:(?:public|private|protected|static|final|abstract|synchronized|native|strictfp)\s+)*(?:\w[\w\d<>,\[\] ]+)\s+\w[\w\d]*\s*\([^)]*\)(?:\s+throws\s+[^{]+)?(?=\s*\{)", re.MULTILINE),
        re.compile(r"^(?:public|private|protected)?\s*(?:abstract\s+)?(?:class|interface|enum|record)\s+\w[\w\d]*[^{]*", re.MULTILINE),
    ],

    "kotlin": [
        re.compile(r"^(?:(?:public|private|protected|internal|open|abstract|override|data|sealed|inline|suspend)\s+)*(?:fun|class|interface|object|enum\s+class|data\s+class|sealed\s+class)\s+\w[\w\d]*[^{=]*", re.MULTILINE),
    ],

    "swift": [
        re.compile(r"^(?:(?:public|private|internal|open|fileprivate|final|override|mutating|static|class)\s+)*(?:func|class|struct|protocol|enum|extension)\s+\w[\w\d]*[^{]*", re.MULTILINE),
    ],

    "c": [
        re.compile(r"^(?![\s#/])(?:(?:static|inline|extern|const|volatile|unsigned|signed)\s+)*\w[\w\d\s\*]+\s+\*?\w[\w\d]*\s*\([^;)]*\)(?=\s*[{;])", re.MULTILINE),
        re.compile(r"^(?:struct|union|enum|typedef)\s+\w[\w\d]*[^{;]*", re.MULTILINE),
    ],

    "cpp": [
        re.compile(r"^(?![\s#/])(?:(?:static|inline|virtual|explicit|constexpr|const|override|final|template[^>]*>\s*)\s+)*\w[\w\d:<>,\s\*&]+\s+\*?\w[\w\d]*\s*\([^;)]*\)(?:\s*const)?(?=\s*[{;])", re.MULTILINE),
        re.compile(r"^(?:class|struct|union|enum(?:\s+class)?|namespace)\s+\w[\w\d]*[^{;]*", re.MULTILINE),
    ],

    "csharp": [
        re.compile(r"^(?:\s+)?(?:(?:public|private|protected|internal|static|virtual|override|abstract|async|sealed|readonly|partial)\s+)*(?:\w[\w\d<>,\[\] ?]+)\s+\w[\w\d]*\s*\([^)]*\)(?=\s*[{;])", re.MULTILINE),
        re.compile(r"^(?:\s+)?(?:public|private|protected|internal)?\s*(?:abstract|static|partial)?\s*(?:class|interface|struct|enum|record)\s+\w[\w\d]*[^{;]*", re.MULTILINE),
    ],

    "ruby": [
        re.compile(r"^(?:\s+)?def\s+(?:self\.)?\w[\w\d?!]*(?:\([^)]*\))?", re.MULTILINE),
        re.compile(r"^(?:class|module)\s+\w[\w\d:]*[^;]*", re.MULTILINE),
    ],

    "php": [
        re.compile(r"^(?:\s+)?(?:(?:public|private|protected|static|abstract|final)\s+)*function\s+\w[\w\d]*\s*\([^)]*\)(?:\s*:\s*\??\w[\w\d\\|]+)?", re.MULTILINE),
        re.compile(r"^(?:abstract\s+)?(?:class|interface|trait|enum)\s+\w[\w\d]*[^{;]*", re.MULTILINE),
    ],

    "lua": [
        re.compile(r"^(?:local\s+)?function\s+[\w\d.:]+\s*\([^)]*\)", re.MULTILINE),
        re.compile(r"^[\w\d.:]+\s*=\s*function\s*\([^)]*\)", re.MULTILINE),
    ],

    "scala": [
        re.compile(r"^(?:\s+)?(?:(?:def|val|var|class|object|trait|case\s+class|sealed\s+(?:class|trait))\s+)\w[\w\d]*[^{=]*", re.MULTILINE),
    ],

    "dart": [
        re.compile(r"^(?:\s+)?(?:(?:static|final|const|abstract|override|late)\s+)*\w[\w\d?<>]+\s+\w[\w\d]*\s*\([^)]*\)(?=\s*[{;=>])", re.MULTILINE),
        re.compile(r"^(?:abstract\s+)?class\s+\w[\w\d]*[^{;]*", re.MULTILINE),
    ],
}


class SignatureExtractor:
    """
    Extracts code signatures (function/class/method declarations) from source files.

    Python: stdlib AST — precise extraction with full type annotations, defaults,
            return types, async/positional-only/keyword-only args.
    Other supported languages: curated regex patterns per language.
    Unsupported types: noted in output but not silently dropped.
    """

    def extract(self, path: Path, source: str | None = None) -> SignatureBlock:
        lang = _LANG_MAP.get(path.suffix.lower(), "unknown")

        if source is None:
            try:
                source = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                try:
                    source = path.read_text(encoding="latin-1")
                except Exception as exc:
                    return SignatureBlock(file_path=path, language=lang, note=f"read error: {exc}")
            except Exception as exc:
                return SignatureBlock(file_path=path, language=lang, note=f"read error: {exc}")

        if lang == "python":
            return self._extract_python(path, source)
        if lang in _SUPPORTED_LANGS:
            return self._extract_regex(path, lang, source)

        return SignatureBlock(
            file_path=path,
            language=lang if lang != "unknown" else f"unknown ({path.suffix})",
            note="signature extraction not supported for this language",
        )

    def _extract_python(self, path: Path, source: str) -> SignatureBlock:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            return SignatureBlock(file_path=path, language="python", note=f"SyntaxError: {exc}")

        sigs: list[str] = []
        method_names: set[str] = set()

        # Module-level constants, type aliases, and StrEnum/Literal declarations.
        # Only emits from the top-level module body (not inside classes or functions).
        # Private names (_prefixed) are always skipped.
        #
        # Large collection literals (list/dict/set/tuple with many items) are
        # summarised as "[N items]" / "{N keys}" to avoid multi-KB single-line dumps.
        _TYPE_ALIAS_HINTS = {"Literal", "TypeAlias", "Union", "Optional"}
        _MAX_RHS_CHARS = 120  # beyond this, collapse to a structural summary

        def _compact_rhs(node_value: ast.expr, full_rhs: str) -> str:
            """Return a compact representation if the full RHS is too long."""
            if len(full_rhs) <= _MAX_RHS_CHARS:
                return full_rhs
            # For collection literals, show type + element count instead of content.
            if isinstance(node_value, ast.List):
                return f"[{len(node_value.elts)} items]"
            if isinstance(node_value, ast.Dict):
                return "{" + f"{len(node_value.keys)} keys" + "}"
            if isinstance(node_value, (ast.Set, ast.Tuple)):
                n = len(node_value.elts)
                kind = "items"
                bracket = ("{", "}") if isinstance(node_value, ast.Set) else ("(", ")")
                return f"{bracket[0]}{n} {kind}{bracket[1]}"
            # For anything else (e.g. a long call expression), truncate with ellipsis.
            return full_rhs[:_MAX_RHS_CHARS].rstrip() + " ..."

        for stmt in tree.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if not isinstance(target, ast.Name):
                        continue
                    name = target.id
                    if name.startswith("_"):
                        continue
                    rhs = ast.unparse(stmt.value) if hasattr(ast, "unparse") else ""
                    is_caps = name.isupper() or (name[0].isupper() and "_" not in name and any(c.isupper() for c in name[1:]))
                    is_alias = any(hint in rhs for hint in _TYPE_ALIAS_HINTS)
                    is_enum = "StrEnum" in rhs or "IntEnum" in rhs or "Enum" in rhs
                    if is_alias or is_enum or (is_caps and len(name) > 2):
                        display_rhs = _compact_rhs(stmt.value, rhs)
                        sigs.append(f"{name} = {display_rhs}")
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                name = stmt.target.id
                if name.startswith("_"):
                    continue
                rhs = ast.unparse(stmt.value) if (hasattr(ast, "unparse") and stmt.value) else ""
                ann = ast.unparse(stmt.annotation) if (hasattr(ast, "unparse") and stmt.annotation) else ""
                is_alias = any(hint in ann for hint in _TYPE_ALIAS_HINTS) or any(hint in rhs for hint in _TYPE_ALIAS_HINTS)
                if is_alias:
                    sigs.append(f"{name}: {ann}" + (f" = {rhs}" if rhs else ""))

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                bases = ", ".join(
                    ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "?")
                    for b in node.bases
                )
                sigs.append(f"class {node.name}({bases}):" if bases else f"class {node.name}:")

                # Pydantic BaseModel: emit field list with types and defaults
                base_names = {
                    (ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", ""))
                    for b in node.bases
                }
                is_pydantic = any(
                    "BaseModel" in b or b in ("BaseModel",) for b in base_names
                )
                if is_pydantic:
                    field_parts: list[str] = []
                    for item in node.body:
                        if (
                            isinstance(item, ast.AnnAssign)
                            and isinstance(item.target, ast.Name)
                            and not item.target.id.startswith("_")
                        ):
                            fname = item.target.id
                            ftype = ast.unparse(item.annotation) if (hasattr(ast, "unparse") and item.annotation) else ""
                            # Extract the actual default value, handling Field(...) wrappers.
                            # Rules:
                            #   Field(default=X)          → show " = X"
                            #   Field(default_factory=X)  → show " = X()" (e.g. " = list()")
                            #   Field(description=...) only → no default shown
                            #   Field(...)                → no default shown (required field)
                            #   plain literal/value       → show as-is
                            fdefault = ""
                            if item.value and hasattr(ast, "unparse"):
                                raw_default = ast.unparse(item.value)
                                field_kw_default = re.search(r"\bdefault=([^,)]+)", raw_default)
                                field_kw_factory = re.search(r"\bdefault_factory=(\w+)", raw_default)
                                if raw_default.startswith("Field("):
                                    if field_kw_default:
                                        inner = field_kw_default.group(1).strip()
                                        if inner not in ("...", "PydanticUndefined"):
                                            fdefault = f" = {inner}"
                                    elif field_kw_factory:
                                        factory = field_kw_factory.group(1).strip()
                                        fdefault = f" = {factory}()"
                                    # else: required Field with only description= — no default
                                else:
                                    fdefault = f" = {raw_default}"
                            field_parts.append(f"{fname}: {ftype}{fdefault}" if ftype else fname)
                    if field_parts:
                        sigs.append(f"    # fields: {', '.join(field_parts)}")

                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        prefix = "async " if isinstance(item, ast.AsyncFunctionDef) else ""
                        args = _format_py_args(item.args)
                        ret = (f" -> {ast.unparse(item.returns)}"
                               if hasattr(ast, "unparse") and item.returns else "")
                        sigs.append(f"    {prefix}def {item.name}({args}){ret}")
                        method_names.add(item.name)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name not in method_names:
                    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
                    args = _format_py_args(node.args)
                    ret = (f" -> {ast.unparse(node.returns)}"
                           if hasattr(ast, "unparse") and node.returns else "")
                    sigs.append(f"{prefix}def {node.name}({args}){ret}")

        return SignatureBlock(file_path=path, language="python", signatures=sigs)

    def _extract_regex(self, path: Path, lang: str, source: str) -> SignatureBlock:
        patterns = _SIG_PATTERNS.get(lang, [])
        if not patterns:
            return SignatureBlock(file_path=path, language=lang, note="no regex patterns defined")

        seen: set[str] = set()
        sigs: list[str] = []
        for pat in patterns:
            for m in pat.finditer(source):
                line = re.sub(r"\s+", " ", m.group(0).strip())
                if line and line not in seen:
                    seen.add(line)
                    sigs.append(line)
        return SignatureBlock(file_path=path, language=lang, signatures=sigs)

    def extract_files(
        self,
        files: list[Path],
        extractors: dict[Path, CodeExtractor] | None = None,
    ) -> list[SignatureBlock]:
        results = []
        for f in files:
            source = extractors[f].original if (extractors and f in extractors) else None
            results.append(self.extract(f, source=source))
        return results


def _format_py_args(args: ast.arguments) -> str:
    """Format a Python AST arguments node into a readable signature string."""
    parts: list[str] = []

    for i, a in enumerate(args.posonlyargs):
        ann = f": {ast.unparse(a.annotation)}" if (hasattr(ast, "unparse") and a.annotation) else ""
        di = i - (len(args.posonlyargs) - len(args.defaults))
        dflt = f" = {ast.unparse(args.defaults[di])}" if (hasattr(ast, "unparse") and di >= 0) else ""
        parts.append(f"{a.arg}{ann}{dflt}")
    if args.posonlyargs:
        parts.append("/")

    offset = len(args.posonlyargs)
    for i, a in enumerate(args.args):
        ann = f": {ast.unparse(a.annotation)}" if (hasattr(ast, "unparse") and a.annotation) else ""
        di = (offset + i) - (len(args.posonlyargs) + len(args.args) - len(args.defaults))
        dflt = f" = {ast.unparse(args.defaults[di])}" if (hasattr(ast, "unparse") and di >= 0) else ""
        parts.append(f"{a.arg}{ann}{dflt}")

    if args.vararg:
        ann = f": {ast.unparse(args.vararg.annotation)}" if (hasattr(ast, "unparse") and args.vararg.annotation) else ""
        parts.append(f"*{args.vararg.arg}{ann}")
    elif args.kwonlyargs:
        parts.append("*")

    for i, a in enumerate(args.kwonlyargs):
        ann = f": {ast.unparse(a.annotation)}" if (hasattr(ast, "unparse") and a.annotation) else ""
        dflt = f" = {ast.unparse(args.kw_defaults[i])}" if (hasattr(ast, "unparse") and args.kw_defaults[i]) else ""
        parts.append(f"{a.arg}{ann}{dflt}")

    if args.kwarg:
        ann = f": {ast.unparse(args.kwarg.annotation)}" if (hasattr(ast, "unparse") and args.kwarg.annotation) else ""
        parts.append(f"**{args.kwarg.arg}{ann}")

    return ", ".join(parts)


# ---------------------------------------------------------------------------
# AST Analyzer — Python function-call graph (from code_analyzer/_ast_analysis)
# ---------------------------------------------------------------------------

@dataclass
class FunctionCallInfo:
    caller: str | None
    callee: str
    arguments: list[str]
    line: int
    is_async: bool = False


@dataclass
class FunctionCallGraph:
    file_path: Path
    module_name: str
    calls: list[FunctionCallInfo] = field(default_factory=list)
    error: str | None = None

    def to_text(self, highlight: set[str] | None = None, concise: bool = False) -> str:
        if self.error:
            return f"# {self.module_name}: parse error — {self.error}\n"
        lines: list[str] = [f"# Call graph: {self.module_name}"]
        for call in self.calls:
            callee_name = call.callee.split(".")[-1]
            marker = "==> " if (highlight and callee_name in highlight) else ""
            async_prefix = "async " if call.is_async else ""
            if concise:
                caller_name = call.caller.split(".")[-1] if call.caller else "Global"
                lines.append(f"  {marker}{async_prefix}{caller_name} → {callee_name} (line {call.line})")
            else:
                caller = f"{async_prefix}{call.caller}" if call.caller else "Global Scope"
                args = ", ".join(call.arguments) if call.arguments else ""
                lines.append(f"  {marker}{caller} → {call.callee}({args}) (line {call.line})")
        return "\n".join(lines)


class FunctionCallAnalyzer:
    """
    Builds a function-call graph for Python source files using the stdlib AST.
    Useful for understanding inter-function dependencies within a module or directory.

    Args:
        ignore:                  Function/method names to skip. Merged with _DEFAULT_CALL_GRAPH_IGNORE.
        highlight:               Function names to mark in text output.
        include_method_calls:    If True (default), include method calls (obj.method()).
        include_private_methods: If True, include _prefixed method calls. Default False.
    """

    def __init__(
        self,
        ignore: list[str] | None = None,
        highlight: list[str] | None = None,
        include_method_calls: bool = True,
        include_private_methods: bool = False,
    ) -> None:
        self._ignore: set[str] = set(ignore or [])
        self._highlight: set[str] = set(highlight or [])
        self._include_method_calls = include_method_calls
        self._include_private_methods = include_private_methods

    def analyze_file(self, path: Path, project_root: Path | None = None) -> FunctionCallGraph:
        if path.suffix.lower() != ".py":
            return FunctionCallGraph(file_path=path, module_name=str(path), error="not a Python file")

        module_name = self._module_name(path, project_root)
        try:
            source = path.read_text(encoding="utf-8")
        except Exception as exc:
            return FunctionCallGraph(file_path=path, module_name=module_name, error=str(exc))

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            return FunctionCallGraph(file_path=path, module_name=module_name, error=f"SyntaxError: {exc}")

        visitor = _CallVisitor(
            module_name,
            self._ignore,
            include_method_calls=self._include_method_calls,
            include_private_methods=self._include_private_methods,
        )
        visitor.visit(tree)
        return FunctionCallGraph(file_path=path, module_name=module_name, calls=visitor.calls)

    def analyze_files(
        self,
        files: list[Path],
        project_root: Path | None = None,
        scope: list[str] | None = None,
    ) -> list[FunctionCallGraph]:
        candidates = [f for f in files if f.suffix.lower() == ".py"]
        if scope:
            scope_set = set(scope)
            candidates = [f for f in candidates if f.stem in scope_set]
        return [self.analyze_file(f, project_root) for f in candidates]

    def _module_name(self, path: Path, project_root: Path | None) -> str:
        if project_root:
            try:
                rel = path.relative_to(project_root)
                return str(rel.with_suffix("")).replace(os.sep, ".")
            except ValueError:
                pass
        return path.stem


class _CallVisitor(ast.NodeVisitor):
    def __init__(
        self,
        module_name: str,
        ignore: set[str],
        include_method_calls: bool = True,
        include_private_methods: bool = False,
    ) -> None:
        self.module_name = module_name
        self._ignore = ignore
        self._include_method_calls = include_method_calls
        self._include_private_methods = include_private_methods
        self.current_function: str | None = None
        self.current_is_async: bool = False
        self.calls: list[FunctionCallInfo] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        prev_func = self.current_function
        prev_async = self.current_is_async
        self.current_function = f"{self.module_name}.{node.name}"
        self.current_is_async = isinstance(node, ast.AsyncFunctionDef)
        self.generic_visit(node)
        self.current_function = prev_func
        self.current_is_async = prev_async

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_Call(self, node: ast.Call) -> None:
        args: list[str] = []
        if hasattr(ast, "unparse"):
            args = [ast.unparse(a) for a in node.args]

        if isinstance(node.func, ast.Name):
            name = node.func.id
            if name not in self._ignore:
                self.calls.append(FunctionCallInfo(
                    caller=self.current_function,
                    callee=f"{self.module_name}.{name}",
                    arguments=args,
                    line=node.lineno,
                    is_async=self.current_is_async,
                ))

        elif self._include_method_calls and isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr not in self._ignore:
                if not self._include_private_methods and attr.startswith("_"):
                    pass  # skip private method calls
                else:
                    if isinstance(node.func.value, ast.Name):
                        callee = f"{node.func.value.id}.{attr}"
                    elif isinstance(node.func.value, ast.Attribute):
                        callee = f"...{attr}"
                    else:
                        callee = attr
                    self.calls.append(FunctionCallInfo(
                        caller=self.current_function,
                        callee=callee,
                        arguments=args,
                        line=node.lineno,
                        is_async=self.current_is_async,
                    ))

        self.generic_visit(node)


# ---------------------------------------------------------------------------
# AST Analyzer — Python class/method/function structure (legacy, kept for compat)
# ---------------------------------------------------------------------------

@dataclass
class FunctionInfo:
    name: str
    args: list[str]
    is_method: bool = False


@dataclass
class ClassInfo:
    name: str
    methods: list[FunctionInfo] = field(default_factory=list)


@dataclass
class ModuleAST:
    file_path: Path
    functions: list[FunctionInfo] = field(default_factory=list)
    classes: list[ClassInfo] = field(default_factory=list)
    error: str | None = None

    def to_text(self, project_root: Path | None = None) -> str:
        if self.error:
            return f"# Module: {self.file_path}\n(parse error: {self.error})\n"
        if project_root:
            try:
                display = str(self.file_path.relative_to(project_root)).replace("\\", "/")
            except ValueError:
                display = str(self.file_path)
        else:
            display = str(self.file_path)

        parts = [f"# Module: {display}\n"]
        if self.functions:
            parts.append("## Functions:")
            for fn in self.functions:
                parts.append(f"  Function: {fn.name} — Args: {fn.args}")
            parts.append("")
        if self.classes:
            parts.append("## Classes:")
            for cls in self.classes:
                parts.append(f"  Class: {cls.name}")
                for m in cls.methods:
                    parts.append(f"    Method: {m.name} — Args: {m.args}")
            parts.append("")
        return "\n".join(parts).strip() + "\n"


class ASTAnalyzer:
    """Python-only structural analysis: extracts class/method/function names and args."""

    @staticmethod
    def analyze_file(path: Path, source: str | None = None) -> ModuleAST:
        if path.suffix.lower() != ".py":
            return ModuleAST(file_path=path, error="not a Python file")
        if source is None:
            try:
                source = path.read_text(encoding="utf-8")
            except Exception as exc:
                return ModuleAST(file_path=path, error=str(exc))
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            return ModuleAST(file_path=path, error=f"SyntaxError: {exc}")

        classes: list[ClassInfo] = []
        method_names: set[str] = set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods: list[FunctionInfo] = []
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        args = [a.arg for a in item.args.args]
                        methods.append(FunctionInfo(name=item.name, args=args, is_method=True))
                        method_names.add(item.name)
                classes.append(ClassInfo(name=node.name, methods=methods))

        functions: list[FunctionInfo] = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name not in method_names:
                    args = [a.arg for a in node.args.args]
                    functions.append(FunctionInfo(name=node.name, args=args))

        return ModuleAST(file_path=path, functions=functions, classes=classes)

    @staticmethod
    def analyze_files(
        files: list[Path],
        extractors: dict[Path, CodeExtractor] | None = None,
    ) -> list[ModuleAST]:
        results = []
        for f in files:
            source = extractors[f].original if (extractors and f in extractors) else None
            results.append(ASTAnalyzer.analyze_file(f, source=source))
        return results


# ---------------------------------------------------------------------------
# Builder result
# ---------------------------------------------------------------------------

@dataclass
class FileNode:
    """
    Per-file metadata populated by the builder.
    Downstream consumers (e.g. React analysis) may attach exports/imports.
    """
    path: Path
    language: str | None
    original_chars: int
    clean_chars: int
    signatures: list[str] = field(default_factory=list)
    exports: dict | None = None    # attached by react_analysis consumers
    imports: dict | None = None    # attached by react_analysis consumers


@dataclass
class CodeContextResult:
    combined_text: str
    files: list[Path]
    output_mode: OutputMode
    stats: dict
    extractors: dict[Path, CodeExtractor] = field(default_factory=dict)
    file_nodes: dict[Path, FileNode] = field(default_factory=dict)
    signature_blocks: list[SignatureBlock] = field(default_factory=list)
    ast_modules: list[ModuleAST] = field(default_factory=list)
    call_graphs: list[FunctionCallGraph] = field(default_factory=list)
    export_path: Path | None = None

    def to_files_json(self, root: Path | None = None) -> dict:
        """
        Canonical _files-keyed JSON — the single source of truth for downstream consumers.

        Shape:
            {
                "dir": {
                    "_files":      ["a.py", "b.py"],
                    "full_paths":  ["/abs/dir/a.py", "/abs/dir/b.py"],
                    "subdir": {
                        "_files":     ["c.py"],
                        "full_paths": ["/abs/dir/subdir/c.py"],
                    }
                }
            }

        Each directory node carries:
        - "_files"      — list of bare filenames in that directory
        - "full_paths"  — parallel list of absolute paths (as strings)

        If a FileNode has exports/imports attached, they are embedded per file:
            "a.py": {"exports": {...}, "imports": {...}}
        """
        structure: dict = {}

        for f in self.files:
            # Determine path relative to root for tree placement
            if root:
                try:
                    rel = f.relative_to(root)
                except ValueError:
                    rel = Path(f.name)
            else:
                rel = Path(f.name)

            parts = rel.parts
            node = structure
            for part in parts[:-1]:
                node = node.setdefault(part, {})

            filename = parts[-1]
            node.setdefault("_files", []).append(filename)
            node.setdefault("full_paths", []).append(str(f))

            # Embed per-file analysis data if available
            fn = self.file_nodes.get(f)
            if fn and (fn.exports is not None or fn.imports is not None):
                entry: dict = {}
                if fn.exports is not None:
                    entry["exports"] = fn.exports
                if fn.imports is not None:
                    entry["imports"] = fn.imports
                node[filename] = entry

        return structure

    def to_simple_json(self) -> dict:
        """
        Flat file→None mapping for lightweight use (tree shape, no _files convention).
        """
        structure: dict = {}
        for f in self.files:
            parts = f.parts
            node = structure
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            node[parts[-1]] = None
        return structure


# ---------------------------------------------------------------------------
# Code Context Builder (orchestrator)
# ---------------------------------------------------------------------------

class CodeContextBuilder:
    """
    Main entry point. Orchestrates:
      discovery → extraction (parallel) → tree → signatures/content → assembly → save

    Args:
        project_root:                Root directory to scan.
        subdirectory:                Optional subdirectory within project_root to restrict scan.
        output_mode:                 "tree_only" | "signatures" | "clean" | "original".
        preset:                      Named preset from config.yaml presets section.
        config_path:                 Path to config.yaml. Defaults to the one next to this file.
        overrides:                   Runtime exclusion/inclusion tweaks.
        additional_files:            Extra file paths always included regardless of filters.
        custom_root:                 Override the tree root label.
        show_all_tree_directories:   Show all dirs in tree, not just those with included files.
        prune_empty_directories:     Remove empty directory entries from the tree.
        export_directory:            Where to write output files. Overrides config.yaml.
        prompt_prefix:               Text prepended to the combined output.
        prompt_suffix:               Text appended to the combined output.
        parallel_workers:            Number of threads for parallel file reading. Default: 8.
        call_graph:                  If True, build function-call graphs for Python files.
        call_graph_ignore:           Additional function names to skip (merged with defaults).
        call_graph_highlight:        Function names to mark in call graph output.
        call_graph_scope:            If set, only analyze files whose stem is in this list.
        call_graph_include_methods:  If True (default), include method calls (ast.Attribute).
        call_graph_include_private:  If True, include private (_prefixed) method calls.
    """

    def __init__(
        self,
        project_root: str | Path,
        subdirectory: str | None = None,
        output_mode: OutputMode | None = None,
        preset: str | None = None,
        config_path: Path = _CONFIG_PATH,
        overrides: dict | None = None,
        additional_files: list[str] | None = None,
        custom_root: str | Path | None = None,
        show_all_tree_directories: bool | None = None,
        prune_empty_directories: bool | None = None,
        export_directory: str | None = None,
        prompt_prefix: str | None = None,
        prompt_suffix: str | None = None,
        parallel_workers: int = 8,
        call_graph: bool = False,
        call_graph_ignore: list[str] | None = None,
        call_graph_highlight: list[str] | None = None,
        call_graph_scope: list[str] | None = None,
        call_graph_include_methods: bool = True,
        call_graph_include_private: bool = False,
    ) -> None:
        self.project_root = Path(project_root)
        self.subdirectory = subdirectory
        self.additional_files = additional_files
        self.custom_root = Path(custom_root) if custom_root else None
        self.prompt_prefix = prompt_prefix
        self.prompt_suffix = prompt_suffix
        self.parallel_workers = max(1, parallel_workers)
        self.call_graph_enabled = call_graph
        self.call_graph_ignore = call_graph_ignore
        self.call_graph_highlight = call_graph_highlight
        self.call_graph_scope = call_graph_scope
        self.call_graph_include_methods = call_graph_include_methods
        self.call_graph_include_private = call_graph_include_private

        self.cfg = CodeContextConfig.from_yaml(config_path, preset=preset, overrides=overrides)

        if output_mode is not None:
            self.cfg.output_mode = output_mode
        if show_all_tree_directories is not None:
            self.cfg.show_all_tree_directories = show_all_tree_directories
        if prune_empty_directories is not None:
            self.cfg.prune_empty_directories = prune_empty_directories
        if export_directory is not None:
            self.cfg.export_directory = export_directory

    def build(self) -> CodeContextResult:
        discovery = FileDiscovery(self.cfg)
        files = discovery.discover(
            self.project_root,
            subdirectory=self.subdirectory,
            additional_files=self.additional_files,
        )
        stats = discovery.analyze(files)
        # Attach excluded file counts so tree builder can show a summary footer.
        stats["excluded_by_extension"] = getattr(discovery, "_last_excluded_counts", {})

        scan_root = self.project_root
        if self.subdirectory:
            normalized = Path(os.path.normpath(self.subdirectory.lstrip("/\\")))
            scan_root = self.project_root / normalized

        tree = DirectoryTree(files, self.cfg, self.custom_root, scan_root=scan_root).generate(
            project_root=self.project_root
        )
        mode = self.cfg.output_mode

        extractors: dict[Path, CodeExtractor] = {}
        signature_blocks: list[SignatureBlock] = []
        ast_modules: list[ModuleAST] = []
        call_graphs: list[FunctionCallGraph] = []

        if mode in ("clean", "original", "signatures"):
            extractors = self._load_files_parallel(files)

        if mode == "clean":
            for ex in extractors.values():
                ex.strip_comments()

        elif mode == "signatures":
            sig_extractor = SignatureExtractor()
            signature_blocks = sig_extractor.extract_files(files, extractors)

        if self.call_graph_enabled:
            # Merge: defaults + project noise from config + caller-supplied ignore
            merged_ignore = list(_DEFAULT_CALL_GRAPH_IGNORE)
            merged_ignore.extend(self.cfg.call_graph_project_noise)
            if self.call_graph_ignore:
                merged_ignore.extend(self.call_graph_ignore)
            analyzer = FunctionCallAnalyzer(
                ignore=merged_ignore,
                highlight=self.call_graph_highlight,
                include_method_calls=self.call_graph_include_methods,
                include_private_methods=self.call_graph_include_private,
            )
            call_graphs = analyzer.analyze_files(
                files, self.project_root, scope=self.call_graph_scope
            )

        combined = self._assemble(files, extractors, tree, signature_blocks, call_graphs, mode)

        # Build file_nodes from extractors
        sig_map = {sb.file_path: sb for sb in signature_blocks}
        file_nodes: dict[Path, FileNode] = {}
        for f in files:
            ex = extractors.get(f)
            lang = _LANG_MAP.get(f.suffix.lower())
            original_chars = ex.char_counts.get("original", 0) if ex else 0
            clean_chars = ex.char_counts.get("clean", 0) if ex else 0
            sigs: list[str] = []
            if mode == "signatures":
                sb = sig_map.get(f)
                if sb:
                    sigs = list(sb.signatures)
            file_nodes[f] = FileNode(
                path=f,
                language=lang,
                original_chars=original_chars,
                clean_chars=clean_chars,
                signatures=sigs,
            )

        return CodeContextResult(
            combined_text=combined,
            files=files,
            output_mode=mode,
            stats=stats,
            extractors=extractors,
            file_nodes=file_nodes,
            signature_blocks=signature_blocks,
            ast_modules=ast_modules,
            call_graphs=call_graphs,
        )

    def _load_files_parallel(self, files: list[Path]) -> dict[Path, CodeExtractor]:
        """Load all files in parallel using a thread pool."""
        extractors: dict[Path, CodeExtractor] = {}
        if not files:
            return extractors

        def _load(path: Path) -> tuple[Path, CodeExtractor]:
            return path, CodeExtractor(path)

        with ThreadPoolExecutor(max_workers=self.parallel_workers) as executor:
            futures = {executor.submit(_load, f): f for f in files}
            for future in as_completed(futures):
                path, ex = future.result()
                extractors[path] = ex

        return extractors

    def _assemble(
        self,
        files: list[Path],
        extractors: dict[Path, CodeExtractor],
        tree: str,
        signature_blocks: list[SignatureBlock],
        call_graphs: list[FunctionCallGraph],
        mode: OutputMode,
    ) -> str:
        parts: list[str] = []

        scanned = self.subdirectory or str(self.project_root)
        dirs = len({f.parent for f in files})
        stats_line = f"Files: {len(files)}  |  Directories: {dirs}" if files else ""
        parts.append(
            f"Code Context  [mode: {mode}  —  {_OUTPUT_MODE_LABELS[mode]}]\n"
            f"Scanned: {scanned}\n"
            + (f"{stats_line}\n" if stats_line else "")
        )

        if self.prompt_prefix:
            parts.append(self.prompt_prefix.strip())
            parts.append("")

        parts.append(tree)
        parts.append("")

        if mode == "tree_only":
            pass

        elif mode == "signatures":
            sig_map = {sb.file_path: sb for sb in signature_blocks}
            for f in files:
                sb = sig_map.get(f)
                if sb:
                    lang = _LANG_MAP.get(f.suffix.lower())
                    parts.append(sb.to_text(self.project_root))

        else:  # "clean" or "original"
            for f in files:
                ex = extractors.get(f)
                if not ex:
                    continue
                content = ex.get_content(mode)
                if not content:
                    continue
                lang = _LANG_MAP.get(f.suffix.lower())
                parts.append(ex.file_header(self.project_root, language=lang))
                parts.append(content)

        if call_graphs:
            parts.append("\n\n---\nFunction Call Graphs\n")
            highlight = set(self.call_graph_highlight) if self.call_graph_highlight else None
            for cg in call_graphs:
                if cg.calls or cg.error:
                    parts.append(cg.to_text(highlight=highlight, concise=False))

        if self.prompt_suffix:
            parts.append("")
            parts.append(self.prompt_suffix.strip())

        return "\n".join(parts)

    def save(self, result: CodeContextResult, export_directory: str | None = None) -> Path | None:
        export_dir = Path(export_directory or self.cfg.export_directory)
        export_dir.mkdir(parents=True, exist_ok=True)

        saved_path: Path | None = None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if self.cfg.save_combined:
            out_path = export_dir / f"{result.output_mode}_{timestamp}.txt"
            out_path.write_text(result.combined_text, encoding="utf-8")
            result.export_path = out_path
            saved_path = out_path
            logger.info("Saved: %s", out_path)
            print(f"Saved: {out_path}")

        if self.cfg.save_individual and result.output_mode in ("clean", "original"):
            for f in result.files:
                ex = result.extractors.get(f)
                if ex is None:
                    ex = CodeExtractor(f)
                    if result.output_mode == "clean":
                        ex.strip_comments()
                content = ex.get_content(result.output_mode)
                if content:
                    fn = result.file_nodes.get(f)
                    lang = fn.language if fn else _LANG_MAP.get(f.suffix.lower())
                    ind_path = export_dir / f"{f.stem}_{timestamp}.txt"
                    ind_path.write_text(
                        ex.file_header(self.project_root, language=lang) + content,
                        encoding="utf-8",
                    )

        if self.cfg.save_combined:
            import json as _json
            json_path = export_dir / f"{result.output_mode}_{timestamp}_structure.json"
            json_path.write_text(
                _json.dumps(result.to_files_json(root=self.project_root), indent=2),
                encoding="utf-8",
            )
            logger.info("Saved structure JSON: %s", json_path)

        return saved_path

    def print_summary(self, result: CodeContextResult) -> None:
        stats = result.stats
        mode_label = _OUTPUT_MODE_LABELS.get(result.output_mode, result.output_mode)
        sep = "=" * 60
        print(f"\n{sep}")
        print(f"Mode:          {mode_label}")
        print(f"Files:         {stats['total_files']}")
        print(f"Directories:   {stats['total_directories']}")
        print(f"File types:    {stats['file_types']}")
        total_original = sum(fn.original_chars for fn in result.file_nodes.values())
        total_clean = sum(fn.clean_chars for fn in result.file_nodes.values())
        if total_original:
            print(f"Chars (raw):   {total_original:,}")
        if total_clean:
            print(f"Chars (clean): {total_clean:,}")
        print(f"Output chars:  {len(result.combined_text):,}")
        if result.export_path:
            print(f"Saved to:      {result.export_path}")
        print(f"{sep}\n")


# ---------------------------------------------------------------------------
# CLI / __main__ usage
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # -------------------------------------------------------------------------
    # Set OUTPUT_MODE to control what the tool produces.
    #
    # "tree_only"   — directory tree only, no file content             (~1% tokens)
    # "signatures"  — function/class/method signatures, no bodies    (~5-10% tokens)
    # "clean"       — full content with comments stripped            (~70-80% tokens)
    # "original"    — full content, completely unmodified              (100% tokens)
    # -------------------------------------------------------------------------
    OUTPUT_MODE: OutputMode = "signatures"

    PROJECT_ROOT = Path("/home/arman/projects/aidream")
    SUBDIRECTORY = "ai/tools"      # set to None to scan the whole root
    CUSTOM_ROOT: Path | None = None
    EXPORT_DIRECTORY = Path("/tmp/code_context_output")

    # Named preset from config.yaml (optional)
    PRESET: str | None = None

    OVERRIDES = {
        "exclude_directories": {"add": [], "remove": []},
        "exclude_extensions":  {"add": [], "remove": []},
        # "include_extensions":  {"add": [".py"]},  # uncomment to whitelist
        # "include_directories": {"add": ["src"]},  # uncomment to allowlist dirs
    }

    ADDITIONAL_FILES: list[str] = []

    PROMPT_PREFIX = """\
Here is the code for the module I want you to review.
A directory tree is shown first, followed by the code.
"""

    PROMPT_SUFFIX = """\
Please review carefully and let me know if anything needs to be improved.
"""

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    builder = CodeContextBuilder(
        project_root=PROJECT_ROOT,
        subdirectory=SUBDIRECTORY,
        output_mode=OUTPUT_MODE,
        preset=PRESET,
        overrides=OVERRIDES,
        additional_files=ADDITIONAL_FILES or None,
        custom_root=CUSTOM_ROOT,
        show_all_tree_directories=False,
        prune_empty_directories=False,
        export_directory=str(EXPORT_DIRECTORY),
        prompt_prefix=PROMPT_PREFIX,
        prompt_suffix=PROMPT_SUFFIX,
        parallel_workers=8,
        call_graph=False,
    )

    result = builder.build()
    builder.print_summary(result)
    builder.save(result)
