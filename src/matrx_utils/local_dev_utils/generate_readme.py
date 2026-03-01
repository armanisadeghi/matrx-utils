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

from pathlib import Path

from matrx_utils import clear_terminal
from matrx_utils.code_context.code_context import OutputMode
from matrx_utils.code_context.generate_module_readme import readme_orchestrator

# =============================================================================
#  SETTINGS — edit everything between the dashed lines
# =============================================================================

if __name__ == "__main__":
    clear_terminal()

    # ── 1. TARGET MODULE ──────────────────────────────────────────────────────
    #
    #   PROJECT_ROOT — absolute path to the root of the project you are
    #   documenting.  Leave as None to auto-detect (walks up from cwd looking
    #   for pyproject.toml, setup.py, or .git — correct for most workflows).
    #   Set to an explicit path when documenting a different project:
    #       PROJECT_ROOT = Path("/home/arman/projects/matrx-ai")
    #
    #   SUBDIRECTORIES — list of paths relative to PROJECT_ROOT.
    #   The README is written to <PROJECT_ROOT>/<SUBDIRECTORIES>/MODULE_README.md
    #   by default.  Set OUTPUT_PATH to put it somewhere else.
    #
    PROJECT_ROOT: Path = Path("/home/arman/projects/flow-matrx")
    SUBDIRECTORIES: list[str] = ["backend", "frontend", ""]
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
    CASCADE: bool = False
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
    #   "clean"      — full source with comments stripped
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
    INCLUDE_CALL_GRAPH: bool = False
    CALL_GRAPH_SCOPE: list[str] | None = None  # None = all files

    # ── 6. EXCLUSIONS (optional) ──────────────────────────────────────────────
    #
    #   Directories or files to skip in the call graph / API signatures sections.
    #   Each section has its own list so you can exclude different things from each.
    #
    #   Matching rules (same for both lists):
    #     "tests"        — bare name: matches ANY directory named "tests" anywhere
    #     "ai/tests"     — path with /: matches only that directory name (last segment)
    #     "conftest.py"  — name ending in .py: matches that exact filename
    #
    CALL_GRAPH_EXCLUDE: list[str] | None = ["tests"]
    SIGNATURES_EXCLUDE: list[str] | None = ["tests"]  # e.g. ["tests", "migrations", "conftest.py"]

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
    #  RUN — nothing to edit below this line
    # ==========================================================================
    readme_orchestrator(
        subdirectories=SUBDIRECTORIES,
        project_root=PROJECT_ROOT,
        output=OUTPUT_PATH,
        mode=SIGNATURE_MODE,
        call_graph_scope=CALL_GRAPH_SCOPE,
        project_noise=EXTRA_NOISE,
        no_call_graph=not INCLUDE_CALL_GRAPH,
        cascade=CASCADE,
        cascade_min_files=CASCADE_MIN_FILES,
        cascade_child_mode=CASCADE_CHILD_MODE,
        entry_points=ENTRY_POINTS,
        call_graph_exclude=CALL_GRAPH_EXCLUDE,
        signatures_exclude=SIGNATURES_EXCLUDE,
        force_refresh_children=FORCE_REFRESH_CHILDREN,
    )