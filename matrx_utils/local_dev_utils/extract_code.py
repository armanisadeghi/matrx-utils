"""
extract_code.py — Direct-run script for generating LLM-ready code context.

Run from the project root:
    python utils/local_dev_utils/extract_code.py

Or with CLI quick-overrides:
    python utils/local_dev_utils/extract_code.py [subdirectory] [mode]
    python utils/local_dev_utils/extract_code.py ai/tools signatures
    python utils/local_dev_utils/extract_code.py ai/tools tree_only

Output modes:
    tree_only   — directory tree only, no file content             (~1% tokens)
    signatures  — function/class/method signatures, no bodies    (~5-10% tokens)
    clean       — full content with comments stripped            (~70-80% tokens)
    original    — full content, completely unmodified              (100% tokens)
"""

import logging
import sys
from pathlib import Path

from matrx_utils import clear_terminal

from matrx_utils.code_context import CodeContextBuilder, OutputMode

# ── Project paths ─────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "tmp" / "code_context_output"

VALID_MODES: tuple[str, ...] = ("tree_only", "signatures", "clean", "original")

# =============================================================================
#  SETTINGS — edit everything between the dashed lines
# =============================================================================

if __name__ == "__main__":
    clear_terminal()
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

    # ── 1. WHAT to scan ───────────────────────────────────────────────────────
    #
    #   SUBDIRECTORY  — relative path inside PROJECT_ROOT to scan.
    #                   Set to None or "" to scan the entire project.
    #   ADDITIONAL    — absolute paths of individual files to always include,
    #                   regardless of exclusion filters.
    #
    SUBDIRECTORY: str | None = "utils/local_dev_utils"
    ADDITIONAL_FILES: list[str] = [
        # str(PROJECT_ROOT / "aidream/settings.py"),
    ]

    # ── 2. HOW MUCH detail ────────────────────────────────────────────────────
    #
    #   Choose ONE mode — this is the single most important setting.
    #
    #   "tree_only"  — orientation snapshot, near-zero token cost
    #   "signatures" — full API map, dependencies, ~5-10% of full cost
    #   "clean"      — everything, comments stripped,  ~70-80% cost
    #   "original"   — everything, nothing changed,     100% cost
    #
    OUTPUT_MODE: OutputMode = "signatures"

    # ── 3. NAMED PRESET (optional) ────────────────────────────────────────────
    #
    #   Presets are defined in utils/code_context/config.yaml under `presets:`.
    #   Built-in options:  "python_only" | "frontend" | "tree_overview"
    #   Set to None to use the base config directly.
    #
    PRESET: str | None = None

    # ── 4. FILTER OVERRIDES ───────────────────────────────────────────────────
    #
    #   All lists support {"add": [...], "remove": [...]} patch operations.
    #   Leave empty lists to use config.yaml defaults unchanged.
    #
    #   exclude_directories            — exact directory names to skip
    #   exclude_directories_containing — skip dirs whose name contains this word
    #   exclude_files                  — exact filenames to skip
    #   exclude_files_containing       — skip files whose name contains this word
    #   exclude_extensions             — file extensions to skip  (e.g. ".json")
    #   include_extensions             — WHITELIST: only keep these extensions
    #   include_directories            — ALLOWLIST: only traverse these dir names
    #   include_files                  — ALLOWLIST: only keep these filenames
    #
    OVERRIDES: dict = {
        "exclude_directories": {
            "add":    [],   # e.g. "armaniLocal", "scratch"
            "remove": [],   # e.g. "docs"  (re-include a default-excluded dir)
        },
        "exclude_extensions": {
            "add":    [],
            "remove": [],
        },
        # Uncomment to focus on Python files only:
        # "include_extensions": {"add": [".py"], "remove": []},
        #
        # Uncomment to restrict to specific directories:
        # "include_directories": {"add": ["implementations", "tests"], "remove": []},
    }

    # ── 5. TREE DISPLAY ───────────────────────────────────────────────────────
    #
    #   SHOW_ALL_DIRS  — True: show every directory (including those with no
    #                    included files). False: sparse tree (files-only dirs).
    #   PRUNE_EMPTY    — True: remove directory entries that contain no files
    #                    after filtering. Best combined with SHOW_ALL_DIRS=True.
    #   CUSTOM_ROOT    — Override the root label in the tree display.
    #                    Useful when scanning a subdirectory but you want the
    #                    tree to be rooted at the project root for readability.
    #                    Set to None to use auto-detected root.
    #
    SHOW_ALL_DIRS: bool = True
    PRUNE_EMPTY: bool = False
    CUSTOM_ROOT: str | None = None   # e.g. str(PROJECT_ROOT)

    # ── 6. LLM PROMPT WRAPPING (optional) ────────────────────────────────────
    #
    #   Text prepended / appended to the combined output.
    #   Leave as empty string "" to skip.
    #
    PROMPT_PREFIX: str = ""
    # Example:
    # PROMPT_PREFIX = """
    # Here is the code I want you to review.
    # A directory tree is shown first, followed by the source files.
    # """

    PROMPT_SUFFIX: str = ""
    # Example:
    # PROMPT_SUFFIX = """
    # Please review carefully. Point out any bugs, inconsistencies, or improvements.
    # """

    # ── 7. CALL GRAPH (optional, Python only) ─────────────────────────────────
    #
    #   CALL_GRAPH=True adds a section showing which functions call which,
    #   including line numbers. Useful for tracing logic flow.
    #   CALL_GRAPH_IGNORE   — builtins / noise to skip (e.g. "print", "len")
    #   CALL_GRAPH_HIGHLIGHT — function names to mark with "==>" in output
    #
    CALL_GRAPH: bool = False
    CALL_GRAPH_IGNORE: list[str] = ["print", "len", "str", "int", "list", "dict", "set"]
    CALL_GRAPH_HIGHLIGHT: list[str] = []

    # ── 8. OUTPUT FILES ───────────────────────────────────────────────────────
    #
    #   SAVE_INDIVIDUAL — also write one .txt file per source file
    #   EXPORT_DIR      — where output files are written
    #
    SAVE_INDIVIDUAL: bool = False
    EXPORT_DIRECTORY: str = str(EXPORT_DIR)

    # ── 9. PARALLEL WORKERS ───────────────────────────────────────────────────
    #
    #   Number of threads used for reading files. Increase for large trees on
    #   fast disks; decrease to 1 for debugging.
    #
    PARALLEL_WORKERS: int = 8

    # ==========================================================================
    #  CLI quick-overrides (optional — skip to just use the settings above)
    #  Usage: python extract_code.py [subdirectory] [mode]
    # ==========================================================================
    if len(sys.argv) > 1:
        SUBDIRECTORY = sys.argv[1]
    if len(sys.argv) > 2 and sys.argv[2] in VALID_MODES:
        OUTPUT_MODE = sys.argv[2]  # type: ignore[assignment]

    # ==========================================================================
    #  RUN — nothing to edit below this line
    # ==========================================================================
    builder = CodeContextBuilder(
        project_root=PROJECT_ROOT,
        subdirectory=SUBDIRECTORY or None,
        output_mode=OUTPUT_MODE,
        preset=PRESET,
        overrides=OVERRIDES,
        additional_files=ADDITIONAL_FILES or None,
        custom_root=CUSTOM_ROOT,
        show_all_tree_directories=SHOW_ALL_DIRS,
        prune_empty_directories=PRUNE_EMPTY,
        export_directory=EXPORT_DIRECTORY,
        prompt_prefix=PROMPT_PREFIX or None,
        prompt_suffix=PROMPT_SUFFIX or None,
        parallel_workers=PARALLEL_WORKERS,
        call_graph=CALL_GRAPH,
        call_graph_ignore=CALL_GRAPH_IGNORE or None,
        call_graph_highlight=CALL_GRAPH_HIGHLIGHT or None,
    )

    if SAVE_INDIVIDUAL:
        builder.cfg.save_individual = True

    result = builder.build()
    builder.print_summary(result)
    builder.save(result)
