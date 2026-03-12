"""
Import Checker
==============
Scans a directory for broken imports — modules that are referenced in code
but cannot be resolved. Run directly: python utils/local_dev_utils/import_checker.py

Ignore options:
  - Single line:  add  # noqa  anywhere on the import line
  - Whole file:   add  # noqa: import-checker  anywhere in the first 5 lines
"""

import ast
import sys
import warnings
from pathlib import Path

from matrx_utils import clear_terminal

# ── Configuration ────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Directories to scan (relative to project root). Edit as needed.
SCAN_DIRS =[
        # "ai",
        # "aidream",
        # "api_management",
        # "common",
        # "research",
        # "matrix",
        # "mcp_server",
        # "utils",
        # "workflows",
        # "workflows_v2",
        # "utils",
        # "config",
        "src",
    ]

# Top-level names to skip — stdlib, third-party, and known installed packages.
# Add any package name here to silence false positives.
IGNORE_PREFIXES = {
    # stdlib
    "os",
    "sys",
    "re",
    "json",
    "time",
    "math",
    "copy",
    "uuid",
    "enum",
    "abc",
    "io",
    "pathlib",
    "typing",
    "collections",
    "functools",
    "itertools",
    "dataclasses",
    "datetime",
    "logging",
    "hashlib",
    "base64",
    "struct",
    "asyncio",
    "concurrent",
    "threading",
    "multiprocessing",
    "subprocess",
    "inspect",
    "traceback",
    "warnings",
    "contextlib",
    "weakref",
    "gc",
    "importlib",
    "pkgutil",
    "types",
    "string",
    "textwrap",
    "pprint",
    "random",
    "secrets",
    "decimal",
    "fractions",
    "statistics",
    "heapq",
    "bisect",
    "array",
    "queue",
    "socket",
    "ssl",
    "email",
    "urllib",
    "http",
    "html",
    "xml",
    "csv",
    "configparser",
    "tomllib",
    "pickle",
    "shelve",
    "sqlite3",
    "zipfile",
    "tarfile",
    "gzip",
    "shutil",
    "tempfile",
    "glob",
    "fnmatch",
    "platform",
    "signal",
    "atexit",
    "builtins",
    # third-party (installed)
    "fastapi",
    "pydantic",
    "uvicorn",
    "httpx",
    "aiohttp",
    "requests",
    "anthropic",
    "openai",
    "google",
    "groq",
    "together",
    "cohere",
    "supabase",
    "asyncpg",
    "jwt",
    "dotenv",
    "decouple",
    "yaml",
    "rich",
    "tabulate",
    "ruff",
    "pytest",
    "pandas",
    "numpy",
    "PIL",
    "cv2",
    "torch",
    "sklearn",
    "scipy",
    "matplotlib",
    "seaborn",
    "bs4",
    "lxml",
    "scrapy",
    "playwright",
    "selenium",
    "celery",
    "redis",
    "boto3",
    "aioboto3",
    "stripe",
    "matrx_utils",
    "matrx_orm",
    "matrx_dream_service",
    "tiktoken",
    "tiktoken_ext",
    "tokenizers",
    "moviepy",
    "pydub",
    "speechrecognition",
    "pypdfium2",
    "docx",
    "pptx",
    "reportlab",
    "markdown",
    "markdownify",
    "pygments",
    "jsonschema",
    "json_repair",
    "tldextract",
    "selectolax",
    "readability",
    "faiss",
    "datasketch",
    "cerebras",
    "xai",
    "fireworks",
    "replicate",
    "pymongo",
    "qrcode",
    "regex",
    "parso",
    "astor",
    "mashumaro",
    "aioconsole",
    "aiofiles",
    "socketio",
    "daphne",
}


# ── Core logic ────────────────────────────────────────────────────────────────


def collect_python_files(directories: list[Path]) -> list[Path]:
    files = []
    for d in directories:
        if d.exists():
            files.extend(d.rglob("*.py"))
    return sorted(files)


FILE_IGNORE_MARKER = "# noqa: import-checker"
LINE_IGNORE_MARKER = "# noqa"


def extract_imports(filepath: Path) -> list[tuple[int, str]]:
    """Returns list of (line_number, full_module_path) from a file."""
    try:
        source = filepath.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    lines = source.splitlines()

    # File-level ignore: check BEFORE parsing so we never touch the file at all
    header = "\n".join(lines[:5])
    if FILE_IGNORE_MARKER in header:
        return []

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []

    imports = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        line_text = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
        if LINE_IGNORE_MARKER in line_text:
            continue
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif node.module and node.level == 0:  # absolute imports only
            imports.append((node.lineno, node.module))
    return imports


def is_ignored_prefix(module: str) -> bool:
    """Skip stdlib and known third-party top-level names."""
    return module.split(".")[0] in IGNORE_PREFIXES


def resolve_local(module: str, root: Path) -> bool:
    """
    Check if a dotted module path exists on disk under the project root.
    e.g. 'ai.usage_config' → root/ai/usage_config.py  or  root/ai/usage_config/__init__.py
    """
    parts = module.split(".")
    as_file = root.joinpath(*parts).with_suffix(".py")
    as_pkg = root.joinpath(*parts) / "__init__.py"
    # Also accept the top-level as a plain .py (e.g. 'run' → root/run.py)
    top_file = root / f"{parts[0]}.py"
    top_pkg = root / parts[0]
    if as_file.exists() or as_pkg.exists():
        return True
    # Top-level only (single segment) — dir or file
    if len(parts) == 1 and (top_file.exists() or top_pkg.is_dir()):
        return True
    return False


def can_be_imported(module: str) -> bool:
    """Try to import — catches installed third-party packages."""
    top = module.split(".")[0]
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            __import__(top)
        return True
    except ImportError:
        return False
    except Exception:
        return True  # something exists, don't flag it


def is_local_root_package(module: str, root: Path) -> bool:
    """True if the top-level name is a local project directory (not installed)."""
    top = module.split(".")[0]
    return (root / top).is_dir() and (root / top / "__init__.py").exists()


def check_imports(
    root: Path, scan_dirs: list[Path]
) -> dict[str, list[tuple[int, str]]]:
    """
    Returns a dict of {relative_file_path: [(line, module), ...]}
    for every file that has at least one unresolvable import.

    Logic per import:
      1. Ignored prefix (stdlib / known third-party) → skip
      2. Top-level is a local project package → must resolve fully on disk
      3. Otherwise → try __import__ for installed packages
    """
    broken: dict[str, list[tuple[int, str]]] = {}

    files = collect_python_files(scan_dirs)

    for filepath in files:
        file_broken = []
        for lineno, module in extract_imports(filepath):
            if is_ignored_prefix(module):
                continue
            if is_local_root_package(module, root):
                # It's a local package — only accept it if the full path resolves
                if not resolve_local(module, root):
                    file_broken.append((lineno, module))
            elif resolve_local(module, root):
                continue
            elif not can_be_imported(module):
                file_broken.append((lineno, module))

        if file_broken:
            rel = str(filepath.relative_to(root))
            broken[rel] = file_broken

    return broken


# ── Display ───────────────────────────────────────────────────────────────────


def print_results(broken: dict[str, list[tuple[int, str]]], scanned_count: int) -> None:
    total_issues = sum(len(v) for v in broken.values())

    print(f"Scanned {scanned_count} files across: {', '.join(SCAN_DIRS)}\n")

    if not broken:
        print("✓ No broken imports found.")
        return

    print(f"Found {total_issues} broken import(s) in {len(broken)} file(s):\n")
    print("-" * 60)

    for filepath, issues in sorted(broken.items()):
        print(f"\n  {filepath}")
        for lineno, module in sorted(issues):
            print(f"    line {lineno:>4}: {module}")

    print("\n" + "-" * 60)
    print(f"\nTotal: {total_issues} broken import(s) in {len(broken)} file(s)")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    clear_terminal()

    OVERRIDE_DIRS = [
        "src",
    ]

    # Allow passing a specific subdir as argument: python import_checker.py ai
    target_dirs = sys.argv[1:] if len(sys.argv) > 1 else SCAN_DIRS
    if OVERRIDE_DIRS:
        target_dirs = OVERRIDE_DIRS
    scan_paths = [PROJECT_ROOT / d for d in target_dirs]

    print("=" * 60)
    print("  Import Checker")
    print("=" * 60 + "\n")

    broken = check_imports(PROJECT_ROOT, scan_paths)
    total_files = sum(len(list(p.rglob("*.py"))) for p in scan_paths if p.exists())
    print_results(broken, total_files)
