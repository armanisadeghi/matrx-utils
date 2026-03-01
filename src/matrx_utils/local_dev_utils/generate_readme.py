"""
generate_readme.py — Direct-run script for creating or updating a MODULE_README.md.

Run from the project root:
    python utils/local_dev_utils/generate_readme.py

What it does
------------
First run:  Creates MODULE_README.md in the target directory with all auto-sections
            plus a human-editable Architecture stub.

Subsequent runs:  Refreshes only the AUTO-tagged sections. Everything else —
            including any notes, architecture details, or custom sections you've
            written — is left completely untouched.

AUTO sections refreshed on every run:
    meta        — timestamp, module path, regenerate command
    tree        — live directory tree
    signatures  — full function/class/method signatures with Pydantic field lists
    call_graph  — function call graph (optional, scope-filtered)
    callers     — upstream callers table (auto-discovered or manually pinned)

Human-owned sections (never overwritten):
    ## Architecture  — inserted as a stub on first run, then yours forever
    Anything else you write outside AUTO blocks
"""

import logging
import sys
from pathlib import Path

from matrx_utils import clear_terminal

import matrx_utils.code_context.generate_module_readme as _readme_mod
from matrx_utils.code_context.code_context import OutputMode
from matrx_utils.code_context.generate_module_readme import run as generate_readme
from matrx_utils.code_context.generate_module_readme import run_cascade

# ── Project paths ─────────────────────────────────────────────────────────────

_DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[2]

# =============================================================================
#  SETTINGS — edit everything between the dashed lines
# =============================================================================

if __name__ == "__main__":
    clear_terminal()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # ── 1. TARGET MODULE ──────────────────────────────────────────────────────
    #
    #   PROJECT_ROOT_OVERRIDE — set to a path string to run against another project.
    #   Leave as None to use this project's root (default).
    #
    #   SUBDIRECTORY — path relative to the project root.
    #   The README will be written to <SUBDIRECTORY>/MODULE_README.md by default.
    #   Set OUTPUT_PATH to override where the file lands.
    #
    PROJECT_ROOT_OVERRIDE: str | None = None  # e.g. "/home/arman/projects/matrx-ai"

    SUBDIRECTORY: str = "utils"
    OUTPUT_PATH: str | None = None  # e.g. "ai/tools/MODULE_README.md"

    # ── 2. CASCADE MODE ───────────────────────────────────────────────────────
    #
    #   CASCADE — when True, auto-discovers subdirectories with enough Python
    #             files and generates their READMEs first, then generates the
    #             parent. Use this when running on a large module for the first
    #             time, or any time you see the output README is 1,000+ lines.
    #
    #   CASCADE_MIN_FILES — minimum Python file count (recursive) for a
    #                       subdirectory to get its own child README.
    #                       Default 5. Lower to split more aggressively.
    #
    #   CASCADE_CHILD_MODE — signature detail level for auto-generated children.
    #                        Same choices as SIGNATURE_MODE below.
    #
    CASCADE: bool = True
    CASCADE_MIN_FILES: int = 5
    CASCADE_CHILD_MODE: OutputMode = "signatures"

    # ── 3. FORCE REFRESH CHILDREN ─────────────────────────────────────────────
    #
    #   False (default) — only auto-refresh child READMEs whose source files
    #                     have changed since the child was last generated.
    #
    #   True            — re-generate ALL child READMEs unconditionally, even
    #                     if their source files haven't changed. Use this when
    #                     you've updated generator settings (call graph scope,
    #                     exclude rules, entry points, etc.) and want every
    #                     child to pick up the changes immediately.
    #
    FORCE_REFRESH_CHILDREN: bool = False

    # ── 4. SIGNATURE DETAIL ───────────────────────────────────────────────────
    #
    #   "signatures" — function/class/method signatures + Pydantic field lists
    #   "tree_only"  — directory tree only, no signatures
    #
    SIGNATURE_MODE: OutputMode = "signatures"

    # ── 5. CALL GRAPH (optional, Python only) ─────────────────────────────────
    #
    #   INCLUDE_CALL_GRAPH — set to True to enable the call graph section.
    #                        False skips it entirely.
    #
    #   CALL_GRAPH_SCOPE — file STEMS (no extension) to limit the graph to.
    #                      None = analyze ALL Python files (good for first run).
    #                      Narrow to 3-6 core files once you know the module.
    #
    #   Per-module reference (after first unscoped run, narrow to these):
    #     ai/tools       → ["handle_tool_calls", "executor", "registry", "guardrails"]
    #     ai/prompts     → ["session", "prompt_runner", "context"]
    #     research/      → ["pipeline", "search", "synthesizer"]
    #     aidream/api/   → ["streaming", "emitter", "context"]
    #     utils/code_context → ["code_context", "generate_module_readme"]
    #
    INCLUDE_CALL_GRAPH: bool = True
    CALL_GRAPH_SCOPE: list[str] | None = None  # None = all files

    # ── 6. CALL GRAPH DIRECTORY EXCLUSIONS (optional) ─────────────────────────
    #
    #   Subdirectory paths to skip in the call graph. These dirs still appear
    #   in the tree and signatures — only the call graph ignores them.
    #
    #   "tests"        — bare name: matches ANY segment named "tests" anywhere
    #                    in the module tree (ai.tests, ai.agents.tests, etc.)
    #   "ai/tests"     — full path: matches only that exact subtree.
    #
    CALL_GRAPH_EXCLUDE: list[str] | None = ["tests"]

    # ── 7. UPSTREAM CALLERS ───────────────────────────────────────────────────
    #
    #   None  (default) → AUTO-DISCOVER: scans the project for files that import
    #                      from this module and extracts what they call.
    #
    #   ["fn1", "fn2"]  → MANUAL: pin to specific public entry points after
    #                      reviewing the auto-discovered output (3-6 names ideal).
    #
    #   []              → DISABLED: skip the callers section entirely.
    #
    ENTRY_POINTS: list[str] | None = None

    # ── 8. EXTRA CALL GRAPH NOISE SUPPRESSION (optional) ─────────────────────
    #
    #   Function names to suppress in the call graph beyond the built-in
    #   defaults (builtins, stdlib, and config.yaml project noise).
    #   Only add names that appear as noise specific to THIS module.
    #
    EXTRA_NOISE: list[str] | None = None  # e.g. ["my_util_fn", "debug_helper"]

    # ==========================================================================
    #  CLI quick-override — pass a subdirectory as the first positional arg:
    #  python generate_readme.py ai/tools
    # ==========================================================================
    args = sys.argv[1:]
    PROJECT_ROOT = (
        Path(PROJECT_ROOT_OVERRIDE).resolve()
        if PROJECT_ROOT_OVERRIDE
        else _DEFAULT_PROJECT_ROOT
    )

    if "--root" in args:
        idx = args.index("--root")
        if idx + 1 >= len(args):
            logging.error("--root requires a path argument")
            sys.exit(1)
        PROJECT_ROOT = Path(args[idx + 1]).resolve()
        args = args[:idx] + args[idx + 2:]

    if args:
        SUBDIRECTORY = args[0].strip("/\\")

    # ==========================================================================
    #  RUN — nothing to edit below this line
    # ==========================================================================
    output_path = (
        PROJECT_ROOT / OUTPUT_PATH
        if OUTPUT_PATH
        else PROJECT_ROOT / SUBDIRECTORY / "MODULE_README.md"
    )

    # Patch the generator's module-level root so all internal helpers resolve
    # paths correctly when PROJECT_ROOT_OVERRIDE or --root is used.
    _readme_mod.PROJECT_ROOT = PROJECT_ROOT

    if CASCADE:
        run_cascade(
            subdirectory=SUBDIRECTORY,
            mode=SIGNATURE_MODE,
            child_mode=CASCADE_CHILD_MODE,
            min_py_files=CASCADE_MIN_FILES,
            scope=CALL_GRAPH_SCOPE or None,
            project_noise=EXTRA_NOISE,
            include_call_graph=INCLUDE_CALL_GRAPH,
            entry_points=ENTRY_POINTS,
            call_graph_exclude=CALL_GRAPH_EXCLUDE or None,
            force_refresh_children=FORCE_REFRESH_CHILDREN,
        )
    else:
        generate_readme(
            subdirectory=SUBDIRECTORY,
            output_path=output_path,
            mode=SIGNATURE_MODE,
            scope=CALL_GRAPH_SCOPE or None,
            project_noise=EXTRA_NOISE,
            include_call_graph=INCLUDE_CALL_GRAPH,
            entry_points=ENTRY_POINTS,
            call_graph_exclude=CALL_GRAPH_EXCLUDE or None,
            force_refresh_children=FORCE_REFRESH_CHILDREN,
        )
