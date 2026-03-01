"""
Files and directories excluded from the string-mention search.

The string-mention search is the second pass that runs only on zero-usage
packages, looking for their names anywhere in the codebase — in comments,
strings, markdown files, etc.  The goal is to surface hints about packages
that the import scanner could not detect.

This file lets you exclude paths that would produce noisy or misleading hits
because they contain package names as data rather than as evidence of usage.

────────────────────────────────────────────────────────────────────────────────
MENTION_SCAN_EXCLUDE_FILES
────────────────────────────────────────────────────────────────────────────────
Individual files to exclude.  Use paths relative to the project root.

Already excluded automatically (do not need to be listed here):
  - requirements.txt / pyproject.toml      — list every package by definition
  - config/package_analysis/packages.py    — this config references package names
  - config/package_analysis/reports.py     — scanner infrastructure
  - config/package_analysis/scan_excludes.py (this file)
  - config/settings.py
  - utils/local_dev_utils/package_usage_scanner.py
  - utils/local_dev_utils/package_size_analyzer.py

Add any file here that lists package names as notes/analysis rather than code.
Examples: audit docs, migration notes, architecture decision records.

────────────────────────────────────────────────────────────────────────────────
MENTION_SCAN_EXCLUDE_DIRS
────────────────────────────────────────────────────────────────────────────────
Directory names (not full paths) to skip entirely during the mention search.
These are matched against each path component, the same way SKIP_DIRS works
in the main import scan.

The main import scan already skips:
  .venv, venv, .git, __pycache__, .mypy_cache, .pytest_cache,
  node_modules, reports, temp, staticfiles, migrations

Add directory names here to also skip them in the mention search only.
Use this for folders that contain notes/analysis/docs about packages.

────────────────────────────────────────────────────────────────────────────────
"""

# Individual files to exclude from the string-mention search.
# Paths are relative to the project root (aidream/).
MENTION_SCAN_EXCLUDE_FILES: list[str] = [
    # --- Analysis notes that list packages by name as documentation ---
    ".arman/analysis/packages/not-used.md",
    ".arman/junk/PACKAGE_SIZE_ANALYSIS.md",

    # Add your own below:
    # "docs/package-audit-2025.md",
    # "notes/migration-plan.txt",
]


# Directory names to skip entirely during the mention search.
# Matched against path components (not full paths).
MENTION_SCAN_EXCLUDE_DIRS: set[str] = set()
# Uncomment and add directory names to skip them entirely:
# MENTION_SCAN_EXCLUDE_DIRS = {
#     ".arman",   # skip all .arman analysis notes
# }
