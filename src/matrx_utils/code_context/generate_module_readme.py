"""
generate_module_readme.py
=========================
Generates or surgically updates a MODULE_README.md for any directory.

On first run: creates the file with all auto-managed sections plus a stub
Architecture section for human authoring.

On subsequent runs: replaces only the AUTO-tagged sections; all human-authored
content outside those blocks is left completely untouched.

AUTO section convention
-----------------------
Each auto-managed section is wrapped with sentinel comments:

    <!-- AUTO:section_id -->
    ...generated content...
    <!-- /AUTO:section_id -->

Anything outside these blocks belongs to the developer and is never modified.

Auto-managed sections (in order):
    meta        — document header, timestamp, regenerate command
    tree        — live directory tree (tree_only mode)
    signatures  — full API signatures (signatures mode)
    call_graph  — function call graph for scoped files (optional)

Sections that are NOT auto-managed (human-owned after first creation):
    architecture — call flow + layer map stub inserted once on first run,
                   then immediately removed from AUTO control so it can be
                   freely edited without being overwritten.

Usage
-----
    python utils/code_context/generate_module_readme.py <subdirectory> [options]

    # Examples:
    python utils/code_context/generate_module_readme.py ai/tools
    python utils/code_context/generate_module_readme.py ai/tools --mode signatures
    python utils/code_context/generate_module_readme.py ai/tools --output ai/tools/MODULE_README.md
    python utils/code_context/generate_module_readme.py ai/tools \\
        --call-graph-scope handle_tool_calls,executor,registry,guardrails

Options
-------
    --output PATH               Where to write the README (default: <subdirectory>/MODULE_README.md)
    --mode MODE                 Signature detail: signatures | tree_only  (default: signatures)
    --call-graph-scope CSV      Comma-separated file stems to include in call graph
    --project-noise CSV         Comma-separated names to suppress in call graph
    --no-call-graph             Skip call graph section entirely
    --cascade                   Auto-discover qualifying subdirectories, generate their
                                READMEs first, then generate the parent. Skips subdirs
                                that already have a MODULE_README.md.
    --cascade-min-files N       Minimum Python file count for cascade discovery (default: 5)
    --cascade-child-mode MODE   Signature mode for auto-generated children (default: signatures)
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from utils.code_context import CodeContextBuilder
from utils.code_context.code_context import OutputMode

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# AUTO sentinel regex
# ---------------------------------------------------------------------------
_AUTO_PATTERN = re.compile(
    r"<!-- AUTO:(\w+) -->(.*?)<!-- /AUTO:\1 -->",
    re.DOTALL,
)

# ---------------------------------------------------------------------------
# Section ordering — determines append order for new sections
# ---------------------------------------------------------------------------
_SECTION_ORDER = ["meta", "architecture", "tree", "signatures", "call_graph", "callers", "dependencies", "config"]

# ---------------------------------------------------------------------------
# Architecture stub (inserted once, then becomes human-owned)
# ---------------------------------------------------------------------------
_ARCHITECTURE_STUB = """\
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

"""

# ---------------------------------------------------------------------------
# Child README detection
# ---------------------------------------------------------------------------

def _find_child_readmes(subdirectory: str) -> list[Path]:
    """
    Return paths of MODULE_README.md files found in immediate *and* nested
    subdirectories of `subdirectory`, sorted for stable output.

    Only goes one logical level deep per branch — stops descending once a
    README is found in a directory, so deeply-nested modules don't double-count.
    For example:
        ai/tools/MODULE_README.md           → found
        ai/tools/implementations/MODULE_README.md  → NOT found (tools already has one)
    """
    target = PROJECT_ROOT / subdirectory
    found: list[Path] = []

    def _walk(directory: Path) -> None:
        readme = directory / "MODULE_README.md"
        if readme.exists() and directory != target:
            found.append(readme)
            return  # don't recurse into already-documented subtrees
        try:
            for child in sorted(directory.iterdir()):
                if child.is_dir() and not child.name.startswith((".", "_")):
                    _walk(child)
        except PermissionError:
            pass

    _walk(target)
    return sorted(found)


# ---------------------------------------------------------------------------
# Section generators
# ---------------------------------------------------------------------------

def _build_meta(
    subdirectory: str,
    output_path: Path,
    mode: str,
    scope: list[str] | None,
    child_readmes: list[Path] | None = None,
) -> str:
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    scope_arg = f" \\\n        --call-graph-scope {','.join(scope)}" if scope else ""
    cmd = (
        f"python utils/code_context/generate_module_readme.py {subdirectory}"
        f" --mode {mode}{scope_arg}"
    )
    rel_output = output_path.relative_to(PROJECT_ROOT) if output_path.is_relative_to(PROJECT_ROOT) else output_path

    child_readme_rows = ""
    if child_readmes:
        rows: list[str] = []
        for p in child_readmes:
            rel = p.relative_to(PROJECT_ROOT) if p.is_relative_to(PROJECT_ROOT) else p
            # Read its last-generated timestamp from inside the file if available
            child_ts = _read_child_timestamp(p)
            ts_note = f"last generated {child_ts}" if child_ts else ""
            rows.append(f"| [`{rel}`]({rel}) | {ts_note} |")
        child_readme_rows = (
            "\n\n**Child READMEs detected** (signatures collapsed — see links for detail):\n\n"
            "| README | |\n"
            "|--------|---|\n"
            + "\n".join(rows)
        )

    child_section = child_readme_rows if child_readme_rows else ""
    return f"""\
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `{subdirectory}` |
| Last generated | {ts} |
| Output file | `{rel_output}` |
| Signature mode | `{mode}` |
{child_section}
**To refresh auto-sections:**
```bash
{cmd}
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
"""


def _read_child_timestamp(readme_path: Path) -> str | None:
    """Extract the 'Last generated' timestamp from an existing MODULE_README.md."""
    try:
        text = readme_path.read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"\|\s*Last generated\s*\|\s*([^\|]+)\|", text)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return None


def _build_config_block(
    subdirectory: str,
    mode: OutputMode,
    scope: list[str] | None,
    project_noise: list[str] | None,
    include_call_graph: bool,
    entry_points: list[str] | None,
    call_graph_exclude: list[str] | None = None,
) -> str:
    """
    Build a machine-readable config block embedded at the bottom of every README.
    Stores the exact parameters used for this generation so any caller (parent
    cascade, CI, or a developer) can reproduce or re-trigger it without guessing.

    The block is auto-managed (overwritten on every run) and intentionally placed
    last so it stays out of the way of human-authored content.
    """
    cfg = {
        "subdirectory": subdirectory,
        "mode": mode,
        "scope": scope,
        "project_noise": project_noise,
        "include_call_graph": include_call_graph,
        "entry_points": entry_points,
        "call_graph_exclude": call_graph_exclude,
    }
    payload = json.dumps(cfg, indent=2)
    return f"""\
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{payload}
```
"""


def _read_child_config(readme_path: Path) -> dict | None:
    """
    Extract and parse the embedded generation config from a child MODULE_README.md.
    Returns the config dict, or None if the block is absent or malformed.
    """
    try:
        text = readme_path.read_text(encoding="utf-8", errors="ignore")
        # Find the AUTO:config block and extract the JSON fenced code block inside it
        block_match = re.search(
            r"<!-- AUTO:config -->(.*?)<!-- /AUTO:config -->",
            text,
            re.DOTALL,
        )
        if not block_match:
            return None
        json_match = re.search(r"```json\s*(\{.*?\})\s*```", block_match.group(1), re.DOTALL)
        if not json_match:
            return None
        return json.loads(json_match.group(1))
    except Exception:
        return None


def _check_child_staleness(child_readmes: list[Path]) -> list[tuple[Path, str]]:
    """
    For each child README, find the newest .py file modification time in that
    submodule and compare it against the README's embedded 'Last generated'
    timestamp.

    Returns a list of (readme_path, warning_message) tuples for any submodule
    whose source has been modified since the README was generated.
    Also checks the subdir's own mtime to catch file additions/deletions.
    """
    stale: list[tuple[Path, str]] = []
    for readme in child_readmes:
        subdir = readme.parent
        ts_str = _read_child_timestamp(readme)
        if not ts_str:
            continue
        try:
            readme_dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M")
        except ValueError:
            continue

        # Find the newest mtime across .py files AND the directory itself
        # (directory mtime changes on file addition/deletion)
        newest_mtime: float = subdir.stat().st_mtime
        newest_file: Path = subdir
        for py in subdir.rglob("*.py"):
            mt = py.stat().st_mtime
            if mt > newest_mtime:
                newest_mtime = mt
                newest_file = py

        # Compare at minute granularity — the embedded timestamp only has minute
        # precision, so sub-minute differences are noise (e.g. touch during the run).
        newest_dt = datetime.fromtimestamp(newest_mtime).replace(second=0, microsecond=0)
        if newest_dt > readme_dt:
            try:
                rel_readme = readme.relative_to(PROJECT_ROOT)
                rel_file = newest_file.relative_to(PROJECT_ROOT)
            except ValueError:
                rel_readme = readme
                rel_file = newest_file
            delta_minutes = int((newest_dt - readme_dt).total_seconds() / 60)
            age = f"{delta_minutes}m" if delta_minutes < 120 else f"{delta_minutes // 60}h"
            msg = (
                f"  ⚠  {rel_readme} is STALE — "
                f"{rel_file} modified {age} after last generation"
            )
            stale.append((readme, msg))

    return stale


def _build_tree(subdirectory: str, child_readmes: list[Path] | None = None) -> str:
    # Always include MODULE_README.md files as additional_files so they appear
    # in the tree even though .md is in the excluded extensions list.
    readme_paths = [str(p) for p in (child_readmes or [])]
    # Also include the target module's own README if it exists (for self-referential display)
    own_readme = PROJECT_ROOT / subdirectory / "MODULE_README.md"
    if own_readme.exists() and str(own_readme) not in readme_paths:
        readme_paths.append(str(own_readme))

    builder = CodeContextBuilder(
        project_root=PROJECT_ROOT,
        subdirectory=subdirectory,
        output_mode="tree_only",
        export_directory="/tmp/module_readme_gen",
        show_all_tree_directories=True,
        prune_empty_directories=False,
        additional_files=readme_paths if readme_paths else None,
    )
    result = builder.build()
    # Strip the header line ("Code Context [mode: ...]") — keep only the tree
    tree_lines: list[str] = []
    in_tree = False
    for ln in result.combined_text.splitlines():
        if not in_tree:
            if ln and not ln.startswith("Code Context") and not ln.startswith("Scanned:") and not ln.startswith("Files:"):
                in_tree = True
        if in_tree:
            tree_lines.append(ln)

    tree_text = "\n".join(tree_lines).strip()
    stats = result.stats
    file_count = stats.get("total_files", len(result.files))
    dir_count = stats.get("total_directories", len({f.parent for f in result.files}))

    # Excluded files footer — only show extensions with meaningful counts, skip noise-only
    excluded: dict[str, int] = stats.get("excluded_by_extension", {})
    excluded_note = ""
    if excluded:
        # Sort by count descending, skip extensions with 0 count (shouldn't happen but guard)
        parts = sorted(
            ((ext, cnt) for ext, cnt in excluded.items() if cnt > 0),
            key=lambda x: -x[1],
        )
        if parts:
            summary = ", ".join(f"{cnt} {ext}" for ext, cnt in parts)
            excluded_note = f"\n# excluded: {summary}"

    return f"""\
## Directory Tree

> Auto-generated. {file_count} files across {dir_count} directories.

```
{tree_text}{excluded_note}
```
"""


def _build_signatures(
    subdirectory: str,
    mode: OutputMode,
    child_readmes: list[Path] | None = None,
) -> str:
    builder = CodeContextBuilder(
        project_root=PROJECT_ROOT,
        subdirectory=subdirectory,
        output_mode=mode,
        export_directory="/tmp/module_readme_gen",
    )
    result = builder.build()
    # Strip the header block — extract just the per-file content
    text = result.combined_text
    sep_idx = text.find("\n---\n")
    if sep_idx >= 0:
        content = text[sep_idx + 1:].strip()
    else:
        lines = text.splitlines()
        content = "\n".join(lines[4:]).strip()

    # If child READMEs exist, collapse their file sections into a single stub line.
    # Each file section looks like:
    #   ---
    #   Filepath: ai/tools/models.py  [python]
    #   <content>
    # We group consecutive sections by their covered subdirectory prefix and replace
    # the whole group with a one-liner.
    if child_readmes:
        content = _collapse_covered_sections(content, subdirectory, child_readmes)

    label = "API Signatures" if mode == "signatures" else "File Contents"
    note = (
        "> Auto-generated via `output_mode=\"{mode}\"`. ~5-10% token cost vs full source.\n"
        "> For full source, open the individual files directly.\n"
        "> Submodules with their own `MODULE_README.md` are collapsed to a single stub line."
        if child_readmes else
        f"> Auto-generated via `output_mode=\"{mode}\"`. ~5-10% token cost vs full source.\n"
        "> For full source, open the individual files directly."
    )
    return f"""\
## {label}

{note}

```
{content}
```
"""


def _collapse_covered_sections(
    content: str,
    subdirectory: str,
    child_readmes: list[Path],
) -> str:
    """
    Replace all per-file signature sections that belong to a covered submodule
    with a single compact stub, e.g.:

        ---
        Submodule: ai/tools/  [43 files — full detail in ai/tools/MODULE_README.md]

    Works by splitting on the "---" separator that precedes each Filepath: block,
    then reassembling, substituting a stub for any filepath that falls under a
    covered subdirectory.
    """
    # Build a set of covered subdirectory prefixes (relative to project root, posix)
    covered: dict[str, Path] = {}  # prefix → readme path
    for readme in child_readmes:
        subdir_path = readme.parent
        try:
            rel = subdir_path.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = subdir_path
        prefix = rel.as_posix() + "/"  # e.g. "ai/tools/"
        covered[prefix] = readme

    # Split into blocks. Each block starts with "---\nFilepath: ..." or is a preamble.
    # The content looks like:
    #   ---\nFilepath: ai/tools/__init__.py  [python]\n\n\n---\nFilepath: ...
    blocks = re.split(r"(?=^---$)", content, flags=re.MULTILINE)

    output_blocks: list[str] = []
    emitted_stubs: set[str] = set()  # track which submodule stubs we've already emitted

    for block in blocks:
        if not block.strip():
            continue

        # Extract filepath from "Filepath: ai/tools/models.py  [python]"
        fp_match = re.search(r"^Filepath:\s*(\S+)", block, re.MULTILINE)
        if not fp_match:
            output_blocks.append(block)
            continue

        filepath = fp_match.group(1)  # e.g. "ai/tools/models.py"

        # Check if this filepath falls under any covered prefix
        matched_prefix: str | None = None
        for prefix in covered:
            if filepath.startswith(prefix):
                matched_prefix = prefix
                break

        if matched_prefix is None:
            output_blocks.append(block)
            continue

        # Already emitted stub for this submodule — skip
        if matched_prefix in emitted_stubs:
            continue

        # Emit a single stub for the whole submodule
        readme_path = covered[matched_prefix]
        try:
            readme_rel = readme_path.relative_to(PROJECT_ROOT).as_posix()
        except ValueError:
            readme_rel = str(readme_path)

        # Count files in this submodule (from the content, not filesystem, for accuracy)
        file_count = sum(
            1 for b in blocks
            if re.search(rf"^Filepath:\s*{re.escape(matched_prefix)}", b, re.MULTILINE)
        )
        stub = (
            f"---\n"
            f"Submodule: {matched_prefix}  "
            f"[{file_count} file{'s' if file_count != 1 else ''}"
            f" — full detail in {readme_rel}]\n"
        )
        output_blocks.append(stub)
        emitted_stubs.add(matched_prefix)

    return "\n".join(output_blocks)


def _covered_readme_for_module(module_dotted: str, child_readmes: list[Path]) -> Path | None:
    """
    Given a dotted module name (e.g. "ai.tools.executor") and a list of child README
    paths, return the README whose subdirectory prefix matches, or None.
    """
    for readme in child_readmes:
        try:
            rel = readme.parent.relative_to(PROJECT_ROOT)
        except ValueError:
            rel = readme.parent
        # Convert path to dotted prefix: "ai/tools" → "ai.tools"
        prefix = str(rel).replace("/", ".").replace("\\", ".")
        if module_dotted == prefix or module_dotted.startswith(prefix + "."):
            return readme
    return None


def _collapse_call_graph_block(header: str, entries: list[str], readme: Path) -> str:
    """
    Collapse a covered submodule's call graph block to a single stub line:

        ### Call graph: ai.tools.executor
        > Full detail in ai/tools/MODULE_README.md
        > `first_call` → ... → `last_call`
    """
    try:
        readme_rel = readme.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        readme_rel = str(readme)

    # Extract non-empty call lines
    call_lines = [ln.strip() for ln in entries if ln.strip()]

    if not call_lines:
        return f"### {header[2:]}\n\n> Full detail in [`{readme_rel}`]({readme_rel})\n"

    first = call_lines[0]
    last = call_lines[-1]

    # Pull out just the right-hand side (the callee) from "caller → callee (line N)"
    def _rhs(line: str) -> str:
        if " → " in line:
            return line.split(" → ", 1)[1]
        return line

    if first == last or len(call_lines) == 1:
        summary = f"`{first}`"
    else:
        summary = f"`{first}` → ... → `{_rhs(last)}`"

    return (
        f"### {header[2:]}\n\n"
        f"> Full detail in [`{readme_rel}`]({readme_rel})\n\n"
        f"```\n{summary}\n```"
    )


def _build_call_graph(
    subdirectory: str,
    scope: list[str] | None,
    project_noise: list[str] | None,
    child_readmes: list[Path] | None = None,
    call_graph_exclude: list[str] | None = None,
) -> str:
    """
    Build the call graph section.

    Files belonging to covered subdirectories (those with child READMEs) are
    rendered as collapsed one-liner stubs with a link to the child README.
    Uncovered files are rendered in full.

    call_graph_exclude: list of subdirectory paths (relative to project root,
    e.g. ["ai/tests", "ai/providers"]) whose modules are silently dropped from
    the call graph while still appearing in the directory tree.
    """
    # Build exclusion rules from call_graph_exclude entries.
    #
    # Each entry can be:
    #   "ai/tests"      — full path prefix: matches ai.tests and ai.tests.*
    #   "tests"         — bare name (no slash): matches any segment named "tests"
    #                     i.e. ai.tests, ai.agents.tests, ai.providers.tests, etc.
    #
    # Entries containing a "/" are treated as explicit dotted prefixes.
    # Entries without a "/" are treated as bare segment names to match anywhere.
    exclude_prefixes: set[str] = set()   # full dotted prefixes  (e.g. "ai.tests")
    exclude_segments: set[str] = set()   # bare segment names    (e.g. "tests")
    if call_graph_exclude:
        for excl in call_graph_exclude:
            cleaned = excl.strip("/\\")
            if "/" in cleaned or "\\" in cleaned:
                prefix = cleaned.replace("/", ".").replace("\\", ".")
                exclude_prefixes.add(prefix)
            else:
                exclude_segments.add(cleaned)

    builder = CodeContextBuilder(
        project_root=PROJECT_ROOT,
        subdirectory=subdirectory,
        output_mode="tree_only",
        call_graph=True,
        call_graph_scope=scope,
        call_graph_ignore=project_noise,
        call_graph_include_methods=True,
        call_graph_include_private=False,
        export_directory="/tmp/module_readme_gen",
    )
    result = builder.build()
    text = result.combined_text
    idx = text.find("Function Call Graphs")
    if idx < 0 or not result.call_graphs:
        return ""

    graph_text = text[idx:].strip()

    # Parse into (header_line, [entry_lines]) blocks
    raw_blocks: list[tuple[str, list[str]]] = []
    current_header: str = ""
    current_entries: list[str] = []

    for line in graph_text.splitlines():
        if line.startswith("# Call graph:"):
            if current_header:
                raw_blocks.append((current_header, current_entries))
            current_header = line
            current_entries = []
        elif line.strip() == "Function Call Graphs":
            continue
        else:
            current_entries.append(line)

    if current_header:
        raw_blocks.append((current_header, current_entries))

    if not raw_blocks:
        return ""

    # Drop explicitly excluded subdirectories (call_graph_exclude)
    if exclude_prefixes or exclude_segments:
        def _is_excluded(module_name: str) -> bool:
            # Full prefix match: "ai.tests" matches "ai.tests" and "ai.tests.foo"
            for p in exclude_prefixes:
                if module_name == p or module_name.startswith(p + "."):
                    return True
            # Bare segment match: "tests" matches any component named "tests"
            # e.g. ai.agents.tests, ai.providers.tests.foo
            if exclude_segments:
                parts = module_name.split(".")
                for seg in exclude_segments:
                    if seg in parts:
                        return True
            return False

        raw_blocks = [(h, e) for h, e in raw_blocks
                      if not _is_excluded(h[len("# Call graph: "):].strip())]

    if not raw_blocks:
        return ""

    # Render each block: collapsed stub for covered submodules, full detail otherwise
    blocks: list[str] = []
    for header, entries in raw_blocks:
        # module name is everything after "# Call graph: "
        module_name = header[len("# Call graph: "):].strip()
        covered_readme = _covered_readme_for_module(module_name, child_readmes or [])

        if covered_readme:
            blocks.append(_collapse_call_graph_block(header, entries, covered_readme))
        else:
            entry_text = "\n".join(entries).strip()
            if entry_text:
                blocks.append(f"### {header[2:]}\n\n```\n{entry_text}\n```")

    if not blocks:
        return ""

    scope_note = f"Scoped to: `{', '.join(scope)}`" if scope else "All Python files"
    if child_readmes:
        covered_names = sorted({readme.parent.name for readme in child_readmes})
        scope_note += (
            f"\n> Covered submodules shown as stubs — "
            f"see child READMEs for full detail: `{'`, `'.join(covered_names)}`"
        )
    if call_graph_exclude:
        scope_note += f"\n> Excluded from call graph: `{'`, `'.join(call_graph_exclude)}`"

    body = "\n\n".join(blocks)
    return f"""\
## Call Graph

> Auto-generated. {scope_note}.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

{body}
"""


def _build_dependencies(subdirectory: str) -> str:
    """
    Scan all Python files in the target module for import statements and produce
    two lists:
      - External packages: third-party packages (not stdlib, not this project)
      - Internal modules: cross-module project imports (outside the target directory)

    Uses the AST so it captures TYPE_CHECKING blocks and try/except imports too.
    Stdlib modules are filtered out using sys.stdlib_module_names (Python 3.10+)
    with a hardcoded fallback for older versions.
    """
    import ast as _ast
    import sys as _sys
    import warnings as _warnings

    # Python 3.10+ has sys.stdlib_module_names
    _STDLIB: frozenset[str] = getattr(_sys, "stdlib_module_names", frozenset({
        "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
        "asyncore", "atexit", "base64", "bdb", "binascii", "binhex",
        "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb", "chunk",
        "cmath", "cmd", "code", "codecs", "codeop", "colorsys", "compileall",
        "concurrent", "configparser", "contextlib", "contextvars", "copy",
        "copyreg", "cProfile", "csv", "ctypes", "curses", "dataclasses",
        "datetime", "dbm", "decimal", "difflib", "dis", "doctest", "email",
        "encodings", "enum", "errno", "faulthandler", "fcntl", "filecmp",
        "fileinput", "fnmatch", "fractions", "ftplib", "functools", "gc",
        "getopt", "getpass", "gettext", "glob", "grp", "gzip", "hashlib",
        "heapq", "hmac", "html", "http", "idlelib", "imaplib", "imghdr",
        "imp", "importlib", "inspect", "io", "ipaddress", "itertools", "json",
        "keyword", "lib2to3", "linecache", "locale", "logging", "lzma",
        "mailbox", "mailcap", "marshal", "math", "mimetypes", "mmap",
        "modulefinder", "multiprocessing", "netrc", "nis", "nntplib",
        "numbers", "operator", "optparse", "os", "pathlib", "pdb", "pickle",
        "pickletools", "pipes", "pkgutil", "platform", "plistlib", "poplib",
        "posix", "posixpath", "pprint", "profile", "pstats", "pty", "pwd",
        "py_compile", "pyclbr", "pydoc", "queue", "quopri", "random", "re",
        "readline", "reprlib", "resource", "rlcompleter", "runpy", "sched",
        "secrets", "select", "selectors", "shelve", "shlex", "shutil",
        "signal", "site", "smtpd", "smtplib", "sndhdr", "socket",
        "socketserver", "spwd", "sqlite3", "sre_compile", "sre_constants",
        "sre_parse", "ssl", "stat", "statistics", "string", "stringprep",
        "struct", "subprocess", "sunau", "symtable", "sys", "sysconfig",
        "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile", "termios",
        "test", "textwrap", "threading", "time", "timeit", "tkinter",
        "token", "tokenize", "tomllib", "trace", "traceback", "tracemalloc",
        "tty", "turtle", "turtledemo", "types", "typing", "unicodedata",
        "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave",
        "weakref", "webbrowser", "wsgiref", "xdrlib", "xml", "xmlrpc",
        "zipapp", "zipfile", "zipimport", "zlib", "zoneinfo", "_thread",
        "__future__",
    }))

    target_dir = PROJECT_ROOT / subdirectory
    # Derive the top-level package roots of this project from the project root
    # so we can distinguish "internal project" from "external package".
    # Include all non-hidden directories (with or without __init__.py) and
    # bare .py files at root so packages like seo/ and user_data/ are captured.
    _IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".cursor"}
    project_top_dirs: set[str] = set()
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name not in _IGNORE_DIRS and not item.name.startswith("."):
            project_top_dirs.add(item.name)
        elif item.is_file() and item.suffix == ".py":
            project_top_dirs.add(item.stem)

    # module prefix for the target directory itself (to exclude intra-module imports)
    target_module_prefix = subdirectory.replace("/", ".").replace("\\", ".")

    external: set[str] = set()
    internal: set[str] = set()

    for py_file in target_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                tree = _ast.parse(source, filename=str(py_file))
        except Exception:
            continue

        for node in _ast.walk(tree):
            names: list[str] = []

            if isinstance(node, _ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, _ast.ImportFrom):
                # Skip relative imports (from . import X, from .models import X)
                # They are always intra-module by definition.
                if node.level and node.level > 0:
                    continue
                if node.module:
                    names = [node.module]

            for name in names:
                root = name.split(".")[0]
                if root in _STDLIB or not root:
                    continue
                # Check if it's an intra-module import (within target directory)
                if name == target_module_prefix or name.startswith(target_module_prefix + "."):
                    continue
                # Check if it's another project-internal module
                if root in project_top_dirs:
                    # Collapse to two-segment path for readability (e.g. ai.execution_context)
                    parts = name.split(".")
                    label = ".".join(parts[:2]) if len(parts) > 1 else parts[0]
                    internal.add(label)
                else:
                    external.add(root)

    if not external and not internal:
        return ""

    lines: list[str] = ["## Dependencies", ""]
    if external:
        lines.append(f"**External packages:** {', '.join(sorted(external))}")
    if internal:
        lines.append(f"**Internal modules:** {', '.join(sorted(internal))}")
    lines.append("")

    return "\n".join(lines)


def _scan_external_imports(subdirectory: str) -> list[tuple[Path, set[str], set[str]]]:
    """
    Walk every .py file outside `subdirectory` and collect those that import
    from the target module.

    Returns a list of (py_file, imported_names, module_imports) where:
      - imported_names: specific names pulled via `from module import X`
      - module_imports: module-level names imported via `import module.X as Y`

    This is the shared scanning core used by both auto-discovery and
    the manual entry-points path.
    """
    import ast as _ast
    import warnings as _warnings

    module_path = subdirectory.replace("/", ".").replace("\\", ".")
    target_dir = PROJECT_ROOT / subdirectory

    # All .py files outside the target directory
    candidates: list[Path] = []
    for py_file in PROJECT_ROOT.rglob("*.py"):
        try:
            py_file.relative_to(target_dir)
            continue  # inside target module — skip
        except ValueError:
            pass
        parts = py_file.parts
        if any(p in parts for p in (".venv", "venv", "__pycache__", ".git", "node_modules")):
            continue
        candidates.append(py_file)

    results: list[tuple[Path, set[str], set[str]]] = []

    for py_file in candidates:
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # Quick pre-filter before full parse
        if module_path not in source and subdirectory.replace("/", ".") not in source:
            continue
        try:
            with _warnings.catch_warnings():
                _warnings.simplefilter("ignore")
                tree = _ast.parse(source, filename=str(py_file))
        except SyntaxError:
            continue

        imported_names: set[str] = set()   # from module import X  → X
        module_imports: set[str] = set()   # import module.sub as Y → Y

        for node in _ast.walk(tree):
            if isinstance(node, _ast.ImportFrom):
                mod = node.module or ""
                if mod == module_path or mod.startswith(module_path + "."):
                    for alias in node.names:
                        imported_names.add(alias.asname or alias.name)
            elif isinstance(node, _ast.Import):
                for alias in node.names:
                    n = alias.name
                    if n == module_path or n.startswith(module_path + "."):
                        module_imports.add(alias.asname or n.split(".")[-1])

        if imported_names or module_imports:
            results.append((py_file, imported_names, module_imports))

    return results


def _discover_entry_points(subdirectory: str) -> dict[str, list[str]]:
    """
    Auto-discover the public entry points of a module by inverting the import graph.

    For every external file that imports from `subdirectory`:
      1. Collect directly-imported names  (from ai.tools import handle_tool_calls_v2)
      2. Collect module-alias calls        (import ai.tools as t → t.handle_tool_calls_v2())
      3. Filter out non-callable noise: submodule names, class instances used as
         namespaces, and pure data names (lowercase single words that look like
         module-level variables rather than functions).

    Returns: dict mapping caller_path_str → [fn_name, ...] sorted.
    Only callers that reference at least one callable name are included.
    """
    import ast as _ast

    scan_results = _scan_external_imports(subdirectory)
    if not scan_results:
        return {}

    # Build the target module's own public callable names for cross-referencing.
    # This filters out submodule-name imports (e.g. `from ai import tools`).
    target_callables: set[str] = _get_module_callables(subdirectory)

    callers: dict[str, list[str]] = {}

    for py_file, imported_names, module_imports in scan_results:
        # For direct imports: if we know the module's callables, filter to those.
        # If we can't determine callables (empty set), trust all imported names.
        if target_callables:
            direct_hits = imported_names & target_callables
        else:
            # Heuristic: include names that look like functions/classes
            # (start with lowercase letter for functions, uppercase for classes)
            # Exclude single-word all-lowercase names that are likely submodules.
            direct_hits = {
                n for n in imported_names
                if not n.startswith("_") and (
                    len(n) > 3 or n[0].isupper()
                )
            }

        # For module-alias imports, scan the AST for attribute calls: alias.X()
        attr_hits: set[str] = set()
        if module_imports:
            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = _ast.parse(source)
            except Exception:
                tree = None
            if tree:
                for node in _ast.walk(tree):
                    if (
                        isinstance(node, _ast.Call)
                        and isinstance(node.func, _ast.Attribute)
                        and isinstance(node.func.value, _ast.Name)
                        and node.func.value.id in module_imports
                    ):
                        attr_name = node.func.attr
                        if not attr_name.startswith("_"):
                            if not target_callables or attr_name in target_callables:
                                attr_hits.add(attr_name)

        all_hits = direct_hits | attr_hits
        if all_hits:
            try:
                rel = py_file.relative_to(PROJECT_ROOT)
            except ValueError:
                rel = py_file
            callers[str(rel).replace("\\", "/")] = sorted(all_hits)

    return callers


def _get_module_callables(subdirectory: str) -> set[str]:
    """
    Return the set of public function and class names defined in `subdirectory`.
    Used to filter discovered imports down to actual callables, excluding
    submodule names and data variables.
    """
    import ast as _ast

    callables: set[str] = set()
    target_dir = PROJECT_ROOT / subdirectory

    for py_file in target_dir.rglob("*.py"):
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            tree = _ast.parse(source)
        except Exception:
            continue
        for node in tree.body:
            if isinstance(node, (_ast.FunctionDef, _ast.AsyncFunctionDef, _ast.ClassDef)):
                if not node.name.startswith("_"):
                    callables.add(node.name)

    return callables


def _build_callers(
    subdirectory: str,
    entry_points: list[str] | None,
) -> str:
    """
    Build the Upstream Callers table section.

    When entry_points is None: auto-discover by scanning all external files
    that import from the module and collecting what they actually call.

    When entry_points is a list: use only those specific names (original behaviour,
    now scoped to files that import from the module).

    Returns empty string if no callers are found.
    """
    import ast as _ast

    auto_mode = entry_points is None

    if auto_mode:
        # Auto-discovery path: invert the import graph
        callers_map = _discover_entry_points(subdirectory)
        if not callers_map:
            return ""
        rows: list[tuple[str, str]] = []
        for caller, fns in sorted(callers_map.items()):
            for fn in fns:
                rows.append((caller, fn))
        mode_note = (
            "> Auto-discovered by scanning all project files that import from this module.\n"
            "> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions."
        )
    else:
        # Manual path: original behaviour — scan for named entry points
        entry_set = set(entry_points)
        scan_results = _scan_external_imports(subdirectory)
        rows = []
        for py_file, imported_names, module_imports in scan_results:
            called: set[str] = set()
            # Direct imports of named entry points
            called |= imported_names & entry_set
            # Attribute calls on module aliases
            if module_imports:
                try:
                    source = py_file.read_text(encoding="utf-8", errors="ignore")
                    tree = _ast.parse(source)
                    for node in _ast.walk(tree):
                        if (
                            isinstance(node, _ast.Call)
                            and isinstance(node.func, _ast.Attribute)
                            and isinstance(node.func.value, _ast.Name)
                            and node.func.value.id in module_imports
                            and node.func.attr in entry_set
                        ):
                            called.add(node.func.attr)
                except Exception:
                    pass
            # Direct calls in the file body
            try:
                source = py_file.read_text(encoding="utf-8", errors="ignore")
                tree = _ast.parse(source)
                for node in _ast.walk(tree):
                    if isinstance(node, _ast.Call):
                        if isinstance(node.func, _ast.Name) and node.func.id in entry_set:
                            called.add(node.func.id)
                        elif isinstance(node.func, _ast.Attribute) and node.func.attr in entry_set:
                            called.add(node.func.attr)
            except Exception:
                pass
            if called:
                try:
                    rel = py_file.relative_to(PROJECT_ROOT)
                except ValueError:
                    rel = py_file
                for fn in sorted(called):
                    rows.append((str(rel).replace("\\", "/"), fn))

        if not rows:
            return ""
        mode_note = (
            "> Auto-generated. Shows which files import and call the listed entry points.\n"
            "> Update `ENTRY_POINTS` in `generate_readme.py` to control which functions are tracked."
        )

    rows.sort(key=lambda r: (r[1], r[0]))
    table_lines = ["| Caller | Calls |", "|--------|-------|"]
    table_lines += [f"| `{caller}` | `{fn}()` |" for caller, fn in rows]

    return f"""\
## Upstream Callers

{mode_note}

{chr(10).join(table_lines)}
"""


# ---------------------------------------------------------------------------
# AUTO block extraction and merging
# ---------------------------------------------------------------------------

def _extract_auto_blocks(content: str) -> dict[str, str]:
    """Return mapping of section_id → inner content for all AUTO blocks found."""
    return {m.group(1): m.group(2) for m in _AUTO_PATTERN.finditer(content)}


def _wrap_auto(section_id: str, content: str) -> str:
    return f"<!-- AUTO:{section_id} -->\n{content.strip()}\n<!-- /AUTO:{section_id} -->"


def _merge_sections(existing: str, sections: dict[str, str]) -> str:
    """
    Replace existing AUTO blocks in-place, then append any new sections
    at the end in _SECTION_ORDER order.
    """
    result = existing

    # Replace existing blocks
    def replacer(m: re.Match) -> str:
        sid = m.group(1)
        if sid in sections:
            return _wrap_auto(sid, sections[sid])
        return m.group(0)  # leave untouched if not in our sections dict

    result = _AUTO_PATTERN.sub(replacer, result)

    # Find which sections are already present (after replacement)
    present = set(_extract_auto_blocks(result).keys())

    # Append missing sections in canonical order
    for sid in _SECTION_ORDER:
        if sid == "architecture":
            continue  # architecture is never auto-appended after first creation
        if sid not in present and sid in sections:
            result = result.rstrip() + "\n\n" + _wrap_auto(sid, sections[sid]) + "\n"

    return result


def _build_initial_file(
    subdirectory: str,
    output_path: Path,
    mode: OutputMode,
    scope: list[str] | None,
    project_noise: list[str] | None,
    include_call_graph: bool,
    entry_points: list[str] | None = None,
    call_graph_exclude: list[str] | None = None,
) -> str:
    """Build the full file content for first-time creation."""
    module_name = subdirectory.replace("/", ".").replace("\\", ".")
    child_readmes = _find_child_readmes(subdirectory)
    parts: list[str] = []

    parts.append(f"# `{module_name}` — Module Overview\n")
    parts.append(
        "> This document is partially auto-generated. "
        "Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.\n"
        "> Everything else is yours to edit freely and will never be overwritten.\n"
    )

    # meta
    parts.append(_wrap_auto("meta", _build_meta(
        subdirectory, output_path, mode, scope, child_readmes or None,
    )))
    parts.append("")

    # architecture stub (human-owned from the start — no AUTO tag)
    parts.append(_ARCHITECTURE_STUB)

    # tree — MODULE_README.md files injected so they're visible
    parts.append(_wrap_auto("tree", _build_tree(subdirectory, child_readmes or None)))
    parts.append("")

    # signatures — covered subdirs collapsed to stubs
    parts.append(_wrap_auto("signatures", _build_signatures(
        subdirectory, mode, child_readmes or None,
    )))
    parts.append("")

    # call_graph (optional)
    if include_call_graph:
        cg = _build_call_graph(subdirectory, scope, project_noise, child_readmes or None, call_graph_exclude)
        if cg:
            parts.append(_wrap_auto("call_graph", cg))
            parts.append("")

    # callers — None means auto-discover, [] means explicitly disabled
    if entry_points != []:
        callers = _build_callers(subdirectory, entry_points)
        if callers:
            parts.append(_wrap_auto("callers", callers))
            parts.append("")

    # dependencies (always on — two compact lines, high signal)
    deps = _build_dependencies(subdirectory)
    if deps:
        parts.append(_wrap_auto("dependencies", deps))
        parts.append("")

    # config block — always last, machine-readable, enables auto-refresh of this README
    cfg_block = _build_config_block(
        subdirectory, mode, scope, project_noise, include_call_graph, entry_points, call_graph_exclude,
    )
    parts.append(_wrap_auto("config", cfg_block))
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(
    subdirectory: str,
    output_path: Path,
    mode: OutputMode,
    scope: list[str] | None,
    project_noise: list[str] | None,
    include_call_graph: bool,
    entry_points: list[str] | None = None,
    call_graph_exclude: list[str] | None = None,
    force_refresh_children: bool = False,
) -> None:
    is_new = not output_path.exists()

    if not is_new:
        existing = output_path.read_text(encoding="utf-8")
        # If the file exists but has no AUTO blocks yet (e.g. it was hand-written or
        # created before this system existed), treat it as a fresh generation so we
        # don't duplicate content by appending new AUTO sections after old prose.
        if not _AUTO_PATTERN.search(existing):
            logger.info("Existing file has no AUTO blocks — treating as new: %s", output_path)
            is_new = True

    # Detect child READMEs once — used in meta, tree, signatures, and staleness check
    child_readmes = _find_child_readmes(subdirectory)

    # Refresh children: stale ones always, all of them when force_refresh_children=True.
    # This ensures the parent always collapses up-to-date child data.
    auto_refreshed: list[str] = []
    no_config: list[str] = []
    if child_readmes:
        if force_refresh_children:
            children_to_refresh = [(p, "") for p in child_readmes]
        else:
            children_to_refresh = _check_child_staleness(child_readmes)
        for child_path, _warning in children_to_refresh:
            child_cfg = _read_child_config(child_path)
            if child_cfg is None:
                # Child exists but has no embedded config (generated before this feature)
                try:
                    rel = child_path.relative_to(PROJECT_ROOT)
                except ValueError:
                    rel = child_path
                no_config.append(str(rel))
                continue
            # Replay the child's stored generation parameters exactly
            child_subdir = child_cfg.get("subdirectory", "")
            child_mode: OutputMode = child_cfg.get("mode", "signatures")
            child_scope = child_cfg.get("scope")
            child_noise = child_cfg.get("project_noise")
            child_cg = child_cfg.get("include_call_graph", False)
            child_ep = child_cfg.get("entry_points")
            child_cg_exclude = child_cfg.get("call_graph_exclude")
            child_out = child_path
            logger.info(
                "%s child: %s",
                "Force-refreshing" if force_refresh_children else "Auto-refreshing stale",
                child_path,
            )
            run(
                subdirectory=child_subdir,
                output_path=child_out,
                mode=child_mode,
                scope=child_scope,
                project_noise=child_noise,
                include_call_graph=child_cg,
                entry_points=child_ep,
                call_graph_exclude=child_cg_exclude,
                force_refresh_children=force_refresh_children,
            )
            try:
                rel = child_path.relative_to(PROJECT_ROOT)
            except ValueError:
                rel = child_path
            auto_refreshed.append(str(rel))

        # Re-detect child READMEs after refresh so parent uses updated timestamps
        child_readmes = _find_child_readmes(subdirectory)

    if is_new:
        logger.info("Creating new README: %s", output_path)
        content = _build_initial_file(
            subdirectory, output_path, mode, scope, project_noise, include_call_graph,
            entry_points=entry_points, call_graph_exclude=call_graph_exclude,
        )
    else:
        logger.info("Updating existing README: %s", output_path)
        existing = output_path.read_text(encoding="utf-8")

        sections: dict[str, str] = {}
        sections["meta"] = _build_meta(
            subdirectory, output_path, mode, scope, child_readmes or None,
        )
        sections["tree"] = _build_tree(subdirectory, child_readmes or None)
        sections["signatures"] = _build_signatures(
            subdirectory, mode, child_readmes or None,
        )

        if include_call_graph:
            cg = _build_call_graph(subdirectory, scope, project_noise, child_readmes or None, call_graph_exclude)
            if cg:
                sections["call_graph"] = cg

        # callers — None means auto-discover, [] means explicitly disabled
        if entry_points != []:
            callers = _build_callers(subdirectory, entry_points)
            if callers:
                sections["callers"] = callers

        deps = _build_dependencies(subdirectory)
        if deps:
            sections["dependencies"] = deps

        # Config block — always written/updated, always last
        sections["config"] = _build_config_block(
            subdirectory, mode, scope, project_noise, include_call_graph, entry_points, call_graph_exclude,
        )

        content = _merge_sections(existing, sections)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    rel = output_path.relative_to(PROJECT_ROOT) if output_path.is_relative_to(PROJECT_ROOT) else output_path
    action = "Created" if is_new else "Updated"
    extra_sections = []
    if include_call_graph:
        extra_sections.append("call_graph")
    if entry_points != []:
        extra_sections.append("callers")
    extra_sections.append("dependencies")
    extra_sections.append("config")
    extra = ", " + ", ".join(extra_sections)
    print(f"{action}: {rel}")
    print(f"  Sections refreshed: meta, tree, signatures{extra}")
    print(f"  Architecture section: {'stub inserted (human-owned)' if is_new else 'preserved (human-owned)'}")

    # Report child README status
    if child_readmes:
        if auto_refreshed:
            print(f"  Child READMEs auto-refreshed ({len(auto_refreshed)}):")
            for r in auto_refreshed:
                print(f"    ↻  {r}")
        if no_config:
            print("  Child READMEs need manual refresh (no stored config — re-run each once):")
            for r in no_config:
                print(f"    ⚠  {r}")
        remaining_stale = _check_child_staleness(child_readmes)
        if not auto_refreshed and not no_config:
            print(f"  Child READMEs: {len(child_readmes)} found, all up-to-date ✓")
        elif remaining_stale:
            # Shouldn't normally happen, but guard against it
            print("  Still stale after refresh:")
            for _, w in remaining_stale:
                print(w)


def run_cascade(
    subdirectory: str,
    mode: OutputMode = "signatures",
    child_mode: OutputMode = "signatures",
    min_py_files: int = 5,
    scope: list[str] | None = None,
    project_noise: list[str] | None = None,
    include_call_graph: bool = False,
    entry_points: list[str] | None = None,
    call_graph_exclude: list[str] | None = None,
    force_refresh_children: bool = False,
    _depth: int = 0,
    _all_new: list[Path] | None = None,
) -> None:
    """
    Recursively auto-discover subdirectories that warrant their own MODULE_README.md,
    generate the deepest children first (depth-first), then generate the current level.

    Discovery rules:
    - All subdirectories at any depth are considered, not just immediate children.
    - Depth-first: deepest qualifying directories are generated before their parents,
      so every parent always finds its children already documented when it runs.
    - A subdirectory qualifies if it contains >= `min_py_files` Python files
      (counting recursively within that subdirectory).
    - Subdirectories that already have a MODULE_README.md are still recursed into
      (their children may still need READMEs), but the existing README is only
      regenerated if force_refresh_children=True or the subdir is stale.
    - The current level README is always generated last.

    Args:
        subdirectory:       Target directory (relative to project root).
        mode:               Signature mode for this level's README.
        child_mode:         Signature mode for all auto-generated child READMEs.
        min_py_files:       Minimum Python file count to qualify a subdir.
        scope:              Call graph scope for this level's README.
        project_noise:      Names to suppress in call graph output.
        include_call_graph: Whether to include a call graph in this level's README.
        entry_points:       Entry points for upstream callers section.
        call_graph_exclude: Subdirectory paths to exclude from call graph.
        force_refresh_children: Regenerate all children unconditionally.
    """
    if _all_new is None:
        _all_new = []

    target = PROJECT_ROOT / subdirectory
    indent = "  " * _depth

    # --- Discover immediate qualifying subdirectories -------------------------
    candidates: list[tuple[Path, int]] = []
    try:
        for child in sorted(target.iterdir()):
            if not child.is_dir():
                continue
            if child.name.startswith((".", "_")):
                continue
            py_count = sum(1 for _ in child.rglob("*.py"))
            if py_count >= min_py_files:
                candidates.append((child, py_count))
    except PermissionError:
        logger.warning("Permission denied reading %s", target)
        return

    if _depth == 0:
        if not candidates:
            print(f"Cascade: no subdirectories with >= {min_py_files} Python files found in {subdirectory}.")
            print("Generating parent README only.")
        else:
            print(f"Cascade: starting depth-first generation from {subdirectory}/")
            print(f"  (min_py_files={min_py_files}, child_mode={child_mode})")

    # --- Depth-first: recurse into each candidate before generating it --------
    for subdir_path, py_count in candidates:
        child_subdir = str(subdir_path.relative_to(PROJECT_ROOT))
        child_readme = subdir_path / "MODULE_README.md"
        already_has = child_readme.exists()

        # Always recurse deeper first, regardless of whether this level has a README.
        # This ensures grandchildren are documented before their parent is generated.
        run_cascade(
            subdirectory=child_subdir,
            mode=child_mode,
            child_mode=child_mode,
            min_py_files=min_py_files,
            scope=None,
            project_noise=project_noise,
            include_call_graph=False,
            entry_points=entry_points,
            call_graph_exclude=call_graph_exclude,
            force_refresh_children=force_refresh_children,
            _depth=_depth + 1,
            _all_new=_all_new,
        )

        # Now generate this level's README (after its children are ready)
        if not already_has:
            print(f"{indent}  → Generating: {child_subdir}/  [{py_count} .py files]")
            run(
                subdirectory=child_subdir,
                output_path=child_readme,
                mode=child_mode,
                scope=None,
                project_noise=project_noise,
                include_call_graph=False,
                entry_points=entry_points,
                call_graph_exclude=call_graph_exclude,
                force_refresh_children=force_refresh_children,
            )
            _all_new.append(child_readme)
        elif force_refresh_children:
            print(f"{indent}  ↻ Force-refreshing: {child_subdir}/")
            run(
                subdirectory=child_subdir,
                output_path=child_readme,
                mode=child_mode,
                scope=None,
                project_noise=project_noise,
                include_call_graph=False,
                entry_points=entry_points,
                call_graph_exclude=call_graph_exclude,
                force_refresh_children=force_refresh_children,
            )
        else:
            print(f"{indent}  ✓ Already documented: {child_subdir}/")

    # --- Generate (or update) this level's README last -----------------------
    parent_readme = PROJECT_ROOT / subdirectory / "MODULE_README.md"
    if _depth == 0:
        print(f"\nGenerating root: {subdirectory}/")
    run(
        subdirectory=subdirectory,
        output_path=parent_readme,
        mode=mode,
        scope=scope,
        project_noise=project_noise,
        include_call_graph=include_call_graph,
        entry_points=entry_points,
        call_graph_exclude=call_graph_exclude,
        force_refresh_children=force_refresh_children,
    )

    if _depth == 0:
        total_new = len(_all_new)
        print(f"\nCascade complete: {total_new} new child README{'s' if total_new != 1 else ''} created, root updated.")
        if _all_new:
            print("Next steps:")
            print("  1. Review each child README's Architecture stub and fill it in.")
            print("  2. Set INCLUDE_CALL_GRAPH=True for children that need call graphs, then re-run with FORCE_REFRESH_CHILDREN=True.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate or update a MODULE_README.md for a project subdirectory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("subdirectory", help="Path relative to project root (e.g. ai/tools)")
    parser.add_argument(
        "--output",
        metavar="PATH",
        help="Output path for the README (default: <subdirectory>/MODULE_README.md)",
    )
    parser.add_argument(
        "--mode",
        choices=["signatures", "tree_only", "clean"],
        default="signatures",
        help="Detail level for the API signatures section (default: signatures)",
    )
    parser.add_argument(
        "--call-graph-scope",
        metavar="FILE1,FILE2,...",
        help="Comma-separated file stems to include in call graph (e.g. executor,registry)",
    )
    parser.add_argument(
        "--project-noise",
        metavar="NAME1,NAME2,...",
        help="Additional names to suppress in call graph output",
    )
    parser.add_argument(
        "--no-call-graph",
        action="store_true",
        help="Skip the call graph section entirely",
    )
    parser.add_argument(
        "--cascade",
        action="store_true",
        help=(
            "Auto-discover subdirectories with >= --cascade-min-files Python files, "
            "generate their READMEs first, then generate the parent."
        ),
    )
    parser.add_argument(
        "--cascade-min-files",
        type=int,
        default=5,
        metavar="N",
        help="Minimum Python file count for a subdirectory to get its own README in cascade mode (default: 5)",
    )
    parser.add_argument(
        "--cascade-child-mode",
        choices=["signatures", "tree_only", "clean"],
        default="signatures",
        help="Signature mode for auto-generated child READMEs in cascade mode (default: signatures)",
    )

    args = parser.parse_args()

    subdirectory = args.subdirectory.strip("/\\")

    if args.output:
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
    else:
        output_path = PROJECT_ROOT / subdirectory / "MODULE_README.md"

    scope = [s.strip() for s in args.call_graph_scope.split(",")] if args.call_graph_scope else None
    project_noise = [s.strip() for s in args.project_noise.split(",")] if args.project_noise else None
    include_call_graph = not args.no_call_graph and (scope is not None or not args.no_call_graph)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.cascade:
        run_cascade(
            subdirectory=subdirectory,
            mode=args.mode,
            child_mode=args.cascade_child_mode,
            min_py_files=args.cascade_min_files,
            scope=scope,
            project_noise=project_noise,
            include_call_graph=include_call_graph,
        )
    else:
        run(
            subdirectory=subdirectory,
            output_path=output_path,
            mode=args.mode,
            scope=scope,
            project_noise=project_noise,
            include_call_graph=include_call_graph,
            entry_points=None,
        )


if __name__ == "__main__":
    main()
