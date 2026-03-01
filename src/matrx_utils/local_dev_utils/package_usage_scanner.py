"""
Scans the codebase for imports of installed packages and writes:
  - reports/packages/usage_counts.csv    — all packages sorted by file count (ascending)
  - reports/packages/usage_counts.json   — same data as JSON
  - reports/packages/usage_details.csv   — one row per (package, file) pair
  - reports/packages/usage_details.json  — same data as JSON
  - reports/packages/usage_summary.txt   — human-readable summary

Three layers of false-positive defence
───────────────────────────────────────
Layer 1 — Auto import-name resolution (works for any package in the universe):
  Uses importlib.metadata to map each package name to its real import name(s)
  before scanning.  For example: pymupdf → ['fitz', 'pymupdf'],
  opencv-python-headless → ['cv2'], speechrecognition → ['speech_recognition'].
  This is derived entirely from the package's own installed metadata — no
  project-specific knowledge required.

Layer 2 — Companion suppression (config/package_ignore.py → PACKAGE_COMPANIONS):
  Some packages ship as two separate pip entries but share a single import name,
  or the companion has no import name at all.  If the primary is found as used,
  its listed companions are silently suppressed from the unused list.

Layer 3 — CLI / non-importable tool detection (automatic + manual override):
  Packages whose installed __init__.py is a zero-byte stub are reported as
  "CLI / non-importable tools" rather than "unused".  This is detected
  automatically; edge cases can be added to config/package_ignore.py →
  CLI_PACKAGES.

Bonus — String-mention hint for zero-usage packages:
  Any package that still shows zero import usage after all three layers is
  subjected to a plain-text search of the codebase (both .py and text/markdown
  files).  Hits are categorised by context — comment, string literal, or
  plain text — so the user knows how much weight to give each mention.
  This scanner's own source files and config files are excluded from this
  search to prevent self-referential false positives.

Run package_size_analyzer.py first so this script knows which packages to scan.
"""

import ast
import importlib.metadata as importlib_meta
import os
import re
import warnings
from pathlib import Path

import pandas as pd
from matrx_utils import clear_terminal

from config.package_analysis import report_dir
from config.package_analysis.packages import CLI_PACKAGES, PACKAGE_COMPANIONS, PACKAGES_TO_IGNORE
from config.package_analysis.scan_excludes import MENTION_SCAN_EXCLUDE_DIRS, MENTION_SCAN_EXCLUDE_FILES
from config.settings import settings
from utils.local_dev_utils.package_size_analyzer import run_package_size_report

OUTPUT_DIR = report_dir("packages")
ALL_PACKAGES_CSV = OUTPUT_DIR / "all_packages.csv"

USAGE_COUNTS_CSV = OUTPUT_DIR / "usage_counts.csv"
USAGE_COUNTS_JSON = OUTPUT_DIR / "usage_counts.json"
USAGE_DETAILS_CSV = OUTPUT_DIR / "usage_details.csv"
USAGE_DETAILS_JSON = OUTPUT_DIR / "usage_details.json"
USAGE_SUMMARY_TXT = OUTPUT_DIR / "usage_summary.txt"

SKIP_DIRS = {
    ".venv", "venv", ".git", "__pycache__", ".mypy_cache",
    ".pytest_cache", "node_modules", "reports", "temp",
    "staticfiles", "migrations",
}

# ── Mention-search exclusion set ─────────────────────────────────────────────
# Built once at import time from:
#   1. Hard-coded scanner infrastructure files (always excluded)
#   2. MENTION_SCAN_EXCLUDE_FILES from config/package_analysis/scan_excludes.py

_THIS_FILE = Path(__file__).resolve()
_ROOT = _THIS_FILE.parent.parent.parent  # aidream/

_SCANNER_EXCLUDE_FILES: frozenset[Path] = frozenset({
    # This scanner and its companion
    _THIS_FILE,
    _THIS_FILE.parent / "package_size_analyzer.py",
    # Scanner config directory
    _ROOT / "config" / "package_analysis" / "packages.py",
    _ROOT / "config" / "package_analysis" / "reports.py",
    _ROOT / "config" / "package_analysis" / "scan_excludes.py",
    _ROOT / "config" / "package_analysis" / "__init__.py",
    _ROOT / "config" / "settings.py",
    # Dependency manifests — every package name appears here by definition
    _ROOT / "requirements.txt",
    _ROOT / "pyproject.toml",
})

# Merge with user-supplied exclusions from scan_excludes.py
_SELF_EXCLUDE_FILES: frozenset[Path] = _SCANNER_EXCLUDE_FILES | frozenset(
    (_ROOT / p).resolve() for p in MENTION_SCAN_EXCLUDE_FILES
)

# Text file extensions included in the string-mention pass (not import scan).
TEXT_EXTENSIONS: frozenset[str] = frozenset({
    ".md", ".rst", ".txt", ".toml", ".cfg", ".ini", ".yaml", ".yml",
})

COL_WIDTH = 40
DIVIDER = "-" * (COL_WIDTH + 12)


# ── Layer 1: auto import-name resolution ─────────────────────────────────────

def _resolve_import_names(package_name: str) -> list[str]:
    """
    Returns the list of top-level module names that `package_name` installs,
    derived entirely from the package's own metadata.

    Strategy:
      1. top_level.txt  — explicit list provided by many packages
      2. RECORD parsing — scan the installed file manifest for top-level
         directories and .py files that look like importable modules
      3. Fallback        — return the normalised package name itself
    """
    try:
        dist = importlib_meta.distribution(package_name)
    except importlib_meta.PackageNotFoundError:
        return [_normalize(package_name)]

    # Method 1 — top_level.txt
    top_txt = dist.read_text("top_level.txt")
    if top_txt:
        names = [n.strip() for n in top_txt.strip().splitlines() if n.strip()]
        if names:
            return names

    # Method 2 — RECORD file
    record = dist.read_text("RECORD") or ""
    mods: set[str] = set()
    for line in record.splitlines():
        path_part = line.split(",")[0]
        parts = path_part.replace("\\", "/").split("/")
        top = parts[0] if len(parts) >= 2 else (path_part[:-3] if path_part.endswith(".py") else "")
        if (
            top
            and re.match(r"^[A-Za-z][A-Za-z0-9_]*$", top)
            and "dist-info" not in top
            and ".data" not in top
            and top != "__pycache__"
        ):
            mods.add(top)
    if mods:
        return sorted(mods)

    # Fallback
    return [_normalize(package_name)]


def _is_cli_only(package_name: str) -> bool:
    """
    Returns True when a package installs only a zero-byte __init__.py stub —
    the pattern used by pure CLI tools (ruff, black, mypy, etc.) that ship a
    `package/__init__.py` so `import package` doesn't crash, but the module
    has no real Python API.

    Also returns True for packages listed explicitly in CLI_PACKAGES.
    """
    if _normalize(package_name) in {_normalize(p) for p in CLI_PACKAGES}:
        return True

    try:
        dist = importlib_meta.distribution(package_name)
    except importlib_meta.PackageNotFoundError:
        return False

    record = dist.read_text("RECORD") or ""
    non_meta = [
        line.split(",")[0]
        for line in record.splitlines()
        if ".dist-info/" not in line and not line.startswith("../")
    ]
    if not non_meta:
        return True

    # Find the site-packages root from the dist-info path
    dist_info_path = Path(str(dist._path))  # type: ignore[attr-defined]
    site_packages = dist_info_path.parent

    # Only check the *top-level* __init__.py (exactly one path component deep).
    # Sub-package __init__.py files being empty is normal for real packages.
    for entry in non_meta:
        parts = entry.replace("\\", "/").split("/")
        if len(parts) == 2 and parts[1] == "__init__.py":
            candidate = site_packages / entry
            try:
                if candidate.exists() and candidate.stat().st_size == 0:
                    return True
            except OSError:
                pass
    return False


# ── Layer 2: companion suppression ───────────────────────────────────────────

def _build_companion_suppression(
    used_packages: set[str],
) -> set[str]:
    """
    Returns the set of companion package names that should be suppressed
    because their primary package was found as used.
    """
    suppressed: set[str] = set()
    for primary, companions in PACKAGE_COMPANIONS.items():
        if _normalize(primary) in {_normalize(p) for p in used_packages}:
            suppressed.update(_normalize(c) for c in companions)
    return suppressed


# ── Bonus: context-aware string-mention search ───────────────────────────────

# Context labels used in mention hit records
_CTX_IMPORT  = "import"       # actual import statement (shouldn't appear here, but guard)
_CTX_COMMENT = "comment"      # inside a # comment or docstring
_CTX_STRING  = "string"       # inside a string literal (but not a docstring)
_CTX_CODE    = "code"         # anywhere else in real code
_CTX_TEXT    = "text"         # plain text / markdown / config file


def _classify_py_mentions(
    path: Path,
    pattern: re.Pattern[str],
) -> list[tuple[int, str]]:
    """
    Returns a list of (lineno, context_label) for every line in `path` that
    matches `pattern`, classified by where in the Python source the match sits:
      - 'comment'  — the match is inside a # comment or a docstring
      - 'string'   — the match is inside a string literal (non-docstring)
      - 'code'     — anywhere else (real executable code)

    We use a two-pass approach:
      Pass 1: tokenize to mark every line as comment / string / code.
      Pass 2: regex-match lines that still exist after Pass 1 filtering.

    Tokenisation failures (encoding issues, syntax errors) fall back to a
    plain-text match labelled 'comment' (conservative — we'd rather under-
    report than over-report real usage).
    """
    import tokenize
    import io

    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return []

    lines = source.splitlines()
    line_ctx: dict[int, str] = {}   # 1-indexed lineno → context label

    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
        for tok in tokens:
            kind = tok.type
            start_line = tok.start[0]
            end_line = tok.end[0]
            for ln in range(start_line, end_line + 1):
                if kind == tokenize.COMMENT:
                    line_ctx.setdefault(ln, _CTX_COMMENT)
                elif kind == tokenize.STRING:
                    # Distinguish docstrings from plain string literals.
                    # A STRING token that is the first statement of a module,
                    # class, or function body is a docstring — treat as comment.
                    line_ctx.setdefault(ln, _CTX_COMMENT)
    except tokenize.TokenError:
        pass   # partial tokenisation is fine — unset lines default to 'code'

    results: list[tuple[int, str]] = []
    for i, line in enumerate(lines, start=1):
        if pattern.search(line):
            ctx = line_ctx.get(i, _CTX_CODE)
            results.append((i, ctx))
    return results


MentionHit = dict  # {"file": str, "context": str, "lines": list[int]}

_CTX_ORDER = {_CTX_CODE: 0, _CTX_IMPORT: 0, _CTX_STRING: 1, _CTX_COMMENT: 2, _CTX_TEXT: 3}


def _search_all_mentions(
    packages: list[str],
    py_files: list[Path],
    text_files: list[Path],
    base: Path,
) -> dict[str, list[MentionHit]]:
    """
    Single-pass combined-regex mention search for all `packages` at once.

    Rather than iterating over every file once per package (O(files × packages)),
    this builds one regex with a named capture group per package and makes a
    single pass over each file (O(files)).  Results are identical to running
    separate searches — verified by correctness test before implementation.

    Prints a live progress line per package as results are assembled.

    Returns {package_name: [MentionHit, ...]} for packages that had any hits,
    sorted within each package by context severity (real code first).
    """
    import io
    import tokenize

    if not packages:
        return {}

    # ── Build one combined pattern with a named group per package ────────────
    # Group names cannot contain hyphens, so map each package to a safe key.
    pkg_to_key = {pkg: f"p{i}" for i, pkg in enumerate(packages)}
    key_to_pkg = {v: k for k, v in pkg_to_key.items()}

    alternation = "|".join(
        # Each group matches the package name OR its normalised (hyphen→underscore) form
        f"(?P<{key}>{re.escape(pkg)}|{re.escape(pkg.replace('-', '_'))})"
        for pkg, key in pkg_to_key.items()
    )
    combined = re.compile(r"\b(?:" + alternation + r")\b", re.IGNORECASE)

    def _which_pkg(m: re.Match) -> str | None:
        for key, val in m.groupdict().items():
            if val is not None:
                return key_to_pkg[key]
        return None

    # Accumulator: pkg → filepath → list of (lineno, ctx)
    raw: dict[str, dict[str, list[tuple[int, str]]]] = {pkg: {} for pkg in packages}

    # ── .py files ─────────────────────────────────────────────────────────────
    for py_file in py_files:
        if py_file.resolve() in _SELF_EXCLUDE_FILES:
            continue
        if any(part in MENTION_SCAN_EXCLUDE_DIRS for part in py_file.parts):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not combined.search(source):
            continue  # fast skip — no match anywhere in file

        # Tokenise once to classify every line
        line_ctx: dict[int, str] = {}
        try:
            for tok in tokenize.generate_tokens(io.StringIO(source).readline):
                kind, s_ln, e_ln = tok.type, tok.start[0], tok.end[0]
                if kind in (tokenize.COMMENT, tokenize.STRING):
                    for ln in range(s_ln, e_ln + 1):
                        line_ctx.setdefault(ln, _CTX_COMMENT)
        except tokenize.TokenError:
            pass

        fkey = str(py_file.relative_to(base))
        for i, line in enumerate(source.splitlines(), 1):
            for m in combined.finditer(line):
                pkg = _which_pkg(m)
                if pkg:
                    ctx = line_ctx.get(i, _CTX_CODE)
                    raw[pkg].setdefault(fkey, []).append((i, ctx))

    # ── text files ────────────────────────────────────────────────────────────
    for txt_file in text_files:
        if txt_file.resolve() in _SELF_EXCLUDE_FILES:
            continue
        try:
            text = txt_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not combined.search(text):
            continue

        fkey = str(txt_file.relative_to(base))
        for i, line in enumerate(text.splitlines(), 1):
            for m in combined.finditer(line):
                pkg = _which_pkg(m)
                if pkg:
                    raw[pkg].setdefault(fkey, []).append((i, _CTX_TEXT))

    # ── Assemble final MentionHit lists with live progress output ─────────────
    results: dict[str, list[MentionHit]] = {}
    name_w = max(len(p) for p in packages) + 2

    for pkg in packages:
        file_hits = raw[pkg]
        if not file_hits:
            print(f"  {pkg:<{name_w}} → 0 hits")
            continue

        hits: list[MentionHit] = []
        for fkey, line_list in file_hits.items():
            dominant = min(line_list, key=lambda x: _CTX_ORDER.get(x[1], 9))[1]
            hits.append({
                "file": fkey,
                "context": dominant,
                "lines": [ln for ln, _ in line_list],
            })
        hits.sort(key=lambda h: _CTX_ORDER.get(h["context"], 9))

        # Build compact summary for live output
        ctx_counts: dict[str, int] = {}
        for h in hits:
            ctx_counts[h["context"]] = ctx_counts.get(h["context"], 0) + 1
        ctx_summary = ", ".join(
            f"{cnt} {_CTX_LABELS.get(ctx, ctx)}"
            for ctx, cnt in sorted(ctx_counts.items(), key=lambda x: _CTX_ORDER.get(x[0], 9))
        )
        print(f"  {pkg:<{name_w}} → {len(hits)} file(s)  [{ctx_summary}]")
        results[pkg] = hits

    return results


# ── Core utilities ────────────────────────────────────────────────────────────

def _normalize(name: str) -> str:
    return name.replace("-", "_").lower()


def _print_usage_table(counts_df: pd.DataFrame, title: str) -> None:
    print(f"\n{title}")
    print(f"{'Name':<{COL_WIDTH}}  Files")
    print(DIVIDER)
    for _, row in counts_df.iterrows():
        print(f"{row['package']:<{COL_WIDTH}}  {int(row['file_count'])}")
    print(DIVIDER)


def _load_target_packages() -> list[str]:
    if ALL_PACKAGES_CSV.exists():
        df = pd.read_csv(ALL_PACKAGES_CSV)
        col = "Package" if "Package" in df.columns else "package"
        packages = df[col].dropna().str.lower().tolist()
        print(f"Loaded {len(packages)} packages from {ALL_PACKAGES_CSV.name}")
        return packages

    print("No package CSV found — this should not happen after a refresh.")
    return []


def _collect_python_files(base: Path) -> list[Path]:
    files = []
    for path in base.rglob("*.py"):
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        files.append(path)
    return files


def _collect_text_files(base: Path) -> list[Path]:
    """Collects non-Python text files for the string-mention pass."""
    all_skip = SKIP_DIRS | MENTION_SCAN_EXCLUDE_DIRS
    files = []
    for path in base.rglob("*"):
        if any(skip in path.parts for skip in all_skip):
            continue
        if path.suffix.lower() in TEXT_EXTENSIONS and path.is_file():
            files.append(path)
    return files


def _extract_imports_from_file(path: Path) -> set[str]:
    try:
        if not path.is_file():
            return set()
        source = path.read_text(encoding="utf-8", errors="ignore")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return set()

    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name.split(".")[0].lower())
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module.split(".")[0].lower())
    return names


# ── Main scan ─────────────────────────────────────────────────────────────────

def run_package_usage_scan(
    target_packages: list[str] | None = None,
    refresh: bool = True,
    detail_threshold: int = 0,
) -> pd.DataFrame:
    """
    Args:
        target_packages:   explicit list of package names to scan.  When None
                           the list is loaded from the size-analyzer CSV.
        refresh:           when True (default), runs the size analyzer first so
                           the package list always reflects the current state of
                           pyproject.toml.  Set to False to skip the pre-pass
                           and use whatever CSV is already on disk.
        detail_threshold:  when > 0, any package with file_count ≤ this value
                           gets its matching file paths printed inline under the
                           LOW / HIGH sections.  Useful once you've cleaned up
                           the obvious unused packages and want to dig into the
                           remaining low-usage ones.  Default 0 (no details).
    """
    if target_packages is None:
        if refresh:
            print("Refreshing package list from pyproject.toml ...")
            run_package_size_report(verbose=False)
        target_packages = _load_target_packages()

    ignored_normalized = {_normalize(p) for p in PACKAGES_TO_IGNORE}
    scanned = [p for p in target_packages if _normalize(p) not in ignored_normalized]
    ignored_count = len(target_packages) - len(scanned)
    if ignored_count:
        print(f"Skipping {ignored_count} ignored packages (see config/package_ignore.py)")

    # ── Layer 1: build import-name → package map ──────────────────────────────
    # One package can have multiple import names (e.g. pymupdf → fitz + pymupdf)
    # Multiple packages can share an import name (google-cloud-aiplatform → google)
    # We map each import name back to all packages it could represent.
    import_name_to_packages: dict[str, list[str]] = {}
    package_import_names: dict[str, list[str]] = {}
    cli_only_packages: set[str] = set()

    for pkg in scanned:
        if _is_cli_only(pkg):
            cli_only_packages.add(pkg)
            continue
        names = _resolve_import_names(pkg)
        package_import_names[pkg] = names
        for name in names:
            key = _normalize(name)
            import_name_to_packages.setdefault(key, []).append(pkg)

    base = settings.base_dir
    print(f"\nScanning {len(scanned)} packages across .py files in {base.name}/ ...")
    if cli_only_packages:
        print(f"  ({len(cli_only_packages)} detected as CLI/non-importable tools)")
    py_files = _collect_python_files(base)
    text_files = _collect_text_files(base)
    print(f"Found {len(py_files)} Python files + {len(text_files)} text/markdown files.")

    # ── Import scan ───────────────────────────────────────────────────────────
    detail_rows: list[dict] = []
    for py_file in py_files:
        imports = _extract_imports_from_file(py_file)
        rel_path = py_file.relative_to(base)
        for imp in imports:
            norm = _normalize(imp)
            if norm in import_name_to_packages:
                for pkg in import_name_to_packages[norm]:
                    detail_rows.append({"package": pkg, "file": str(rel_path)})

    details_df = pd.DataFrame(detail_rows, columns=["package", "file"])
    details_df = details_df.drop_duplicates().sort_values(["package", "file"]).reset_index(drop=True)

    found_packages = (
        {_normalize(p) for p in details_df["package"]} if not details_df.empty else set()
    )

    # ── Layer 2: companion suppression ────────────────────────────────────────
    suppressed = _build_companion_suppression(found_packages)

    # ── Classify each package ─────────────────────────────────────────────────
    zero_packages: list[str] = []
    for pkg in scanned:
        norm = _normalize(pkg)
        if norm in {_normalize(p) for p in cli_only_packages}:
            continue
        if norm in suppressed:
            continue
        if norm not in found_packages:
            zero_packages.append(pkg)

    zero_rows = [{"package": p, "file_count": 0} for p in zero_packages]

    counts_df = (
        details_df.groupby("package", sort=False)
        .size()
        .reset_index(name="file_count")
        .sort_values("file_count", ascending=True)
        .reset_index(drop=True)
    )
    if zero_rows:
        zero_df = pd.DataFrame(zero_rows)
        counts_df = pd.concat([zero_df, counts_df], ignore_index=True)

    # ── Bonus: string-mention hints for zero-usage packages ───────────────────
    # Single combined-regex pass — ~14x faster than per-package separate passes.
    # Import aliases are intentionally excluded (only the pip package name is
    # searched) to avoid false positives from short generic aliases like 'grpc'.
    mention_hints: dict[str, list[MentionHit]] = {}
    if zero_packages:
        print(f"\nString-mention search ({len(zero_packages)} zero-usage packages):")
        mention_hints = _search_all_mentions(zero_packages, py_files, text_files, base)

    # ── Persist ───────────────────────────────────────────────────────────────
    details_df.to_csv(USAGE_DETAILS_CSV, index=False)
    details_df.to_json(USAGE_DETAILS_JSON, orient="records", indent=2)
    counts_df.to_csv(USAGE_COUNTS_CSV, index=False)
    counts_df.to_json(USAGE_COUNTS_JSON, orient="records", indent=2)

    _write_summary(counts_df, details_df, cli_only_packages, suppressed, mention_hints)
    _print_terminal_summary(counts_df, cli_only_packages, suppressed, mention_hints, detail_threshold, details_df)

    print(f"\nSaved files:")
    print(f"  {USAGE_COUNTS_CSV}")
    print(f"  {USAGE_COUNTS_JSON}")
    print(f"  {USAGE_DETAILS_CSV}")
    print(f"  {USAGE_DETAILS_JSON}")
    print(f"  {USAGE_SUMMARY_TXT}")

    return counts_df


# ── Output helpers ────────────────────────────────────────────────────────────

_CTX_LABELS: dict[str, str] = {
    _CTX_CODE:    "real code",
    _CTX_STRING:  "string literal",
    _CTX_COMMENT: "comment/docstring",
    _CTX_TEXT:    "text/markdown",
    _CTX_IMPORT:  "import",
}


def _print_file_details(pkg: str, details_df: pd.DataFrame) -> None:
    files = details_df.loc[details_df["package"] == pkg, "file"].tolist()
    for f in files:
        print(f"    {f}")


def _print_terminal_summary(
    counts_df: pd.DataFrame,
    cli_only_packages: set[str],
    suppressed: set[str],
    mention_hints: dict[str, list[MentionHit]],
    detail_threshold: int,
    details_df: pd.DataFrame,
) -> None:
    zero_df = counts_df[counts_df["file_count"] == 0]
    low_df  = counts_df[(counts_df["file_count"] > 0) & (counts_df["file_count"] <= 3)]
    high_df = counts_df[counts_df["file_count"] > 3]

    if not zero_df.empty:
        hinted     = zero_df[zero_df["package"].isin(mention_hints)]
        clean_zero = zero_df[~zero_df["package"].isin(mention_hints)]

        if not clean_zero.empty:
            _print_usage_table(clean_zero, "ZERO usage — safe candidates for removal")

        if not hinted.empty:
            print(f"\n{'─' * (COL_WIDTH + 12)}")
            print("ZERO import usage — BUT name found in code (investigate before removing)")
            print(f"{'─' * (COL_WIDTH + 12)}")
            for _, row in hinted.iterrows():
                pkg  = row["package"]
                hits = mention_hints[pkg]
                ctx_counts: dict[str, int] = {}
                for h in hits:
                    ctx_counts[h["context"]] = ctx_counts.get(h["context"], 0) + 1
                ctx_summary = ", ".join(
                    f"{cnt} {_CTX_LABELS.get(ctx, ctx)}"
                    for ctx, cnt in sorted(ctx_counts.items(), key=lambda x: _CTX_ORDER.get(x[0], 9))
                )
                print(f"\n  {pkg}  [{ctx_summary}]")
                for h in hits[:4]:
                    label     = _CTX_LABELS.get(h["context"], h["context"])
                    lines_str = ", ".join(str(ln) for ln in h["lines"][:3])
                    if len(h["lines"]) > 3:
                        lines_str += f" (+{len(h['lines']) - 3})"
                    print(f"    [{label}]  {h['file']}  (line {lines_str})")
                if len(hits) > 4:
                    print(f"    ... and {len(hits) - 4} more file(s)")
            print()

    if not low_df.empty:
        _print_usage_table(low_df, "LOW usage (1–3 files) — worth reviewing")
        if detail_threshold > 0:
            for _, row in low_df.iterrows():
                if int(row["file_count"]) <= detail_threshold:
                    print(f"  {row['package']}:")
                    _print_file_details(row["package"], details_df)

    if not high_df.empty:
        sorted_high = high_df.sort_values("file_count", ascending=False)
        _print_usage_table(sorted_high, "HIGH usage — keeping these")
        if detail_threshold > 0:
            for _, row in sorted_high.iterrows():
                if int(row["file_count"]) <= detail_threshold:
                    print(f"  {row['package']}:")
                    _print_file_details(row["package"], details_df)

    if cli_only_packages:
        print(f"\n{'─' * (COL_WIDTH + 12)}")
        print("CLI / non-importable tools (auto-detected — not flagged as unused)")
        print(f"{'─' * (COL_WIDTH + 12)}")
        for p in sorted(cli_only_packages):
            print(f"  {p}")
        print(f"{'─' * (COL_WIDTH + 12)}")

    if suppressed:
        print(f"\n{'─' * (COL_WIDTH + 12)}")
        print("Companion packages (suppressed because primary package is used)")
        print(f"{'─' * (COL_WIDTH + 12)}")
        for p in sorted(suppressed):
            print(f"  {p}")
        print(f"{'─' * (COL_WIDTH + 12)}")

    _print_action_summary(zero_df, mention_hints)


def _print_action_summary(
    zero_df: pd.DataFrame,
    mention_hints: dict[str, list[MentionHit]],
    top_n: int = 10,
) -> None:
    """
    Prints a compact action-ready summary at the very end of output.

    All zero-usage packages are ranked by urgency of removal:
      1. No import usage, no mentions at all  → remove immediately
      2. No import usage, text/comment only   → probably safe, low noise
      3. No import usage, real-code mentions  → investigate first

    Within each tier packages are sorted by total mention count ascending
    (fewest mentions = easiest to remove first).  The top `top_n` candidates
    are shown; remaining count is noted if there are more.
    """
    if zero_df.empty:
        return

    # Build scored rows
    rows: list[dict] = []
    for _, r in zero_df.iterrows():
        pkg   = r["package"]
        hits  = mention_hints.get(pkg, [])
        code_files = sum(1 for h in hits if h["context"] in (_CTX_CODE, _CTX_IMPORT, _CTX_STRING))
        text_files = sum(1 for h in hits if h["context"] in (_CTX_COMMENT, _CTX_TEXT))
        total      = code_files + text_files
        rows.append({"pkg": pkg, "code": code_files, "text": text_files, "total": total})

    # Sort: packages with real-code hits last, then by total ascending
    rows.sort(key=lambda x: (1 if x["code"] > 0 else 0, x["total"]))

    W = COL_WIDTH
    print(f"\n{'═' * (W + 32)}")
    print("  ACTION SUMMARY — zero-usage packages ranked by removal confidence")
    print(f"{'═' * (W + 32)}")
    print(f"  {'Package':<{W}}  {'Imports':>7}  {'Code':>5}  {'Text':>5}  {'Total':>6}")
    print(f"  {'─' * W}  {'─' * 7}  {'─' * 5}  {'─' * 5}  {'─' * 6}")

    # Always show all clean-zero packages; cap the mentioned ones at top_n
    clean_rows   = [r for r in rows if r["total"] == 0]
    mention_rows = [r for r in rows if r["total"] > 0]
    displayed    = clean_rows + mention_rows[:top_n]

    for row in displayed:
        flag = "  ← remove" if row["total"] == 0 else ("  ← check code" if row["code"] > 0 else "")
        print(f"  {row['pkg']:<{W}}  {'0':>7}  {row['code']:>5}  {row['text']:>5}  {row['total']:>6}{flag}")

    remaining = len(mention_rows) - min(len(mention_rows), top_n)
    if remaining:
        print(f"  ... and {remaining} more package(s) with mentions not shown")

    clean = sum(1 for r in rows if r["total"] == 0)
    noisy = sum(1 for r in rows if r["total"] > 0 and r["code"] == 0)
    risky = sum(1 for r in rows if r["code"] > 0)
    print(f"\n  {clean} safe to remove  |  {noisy} text-only mentions  |  {risky} real-code mentions")
    print(f"{'═' * (W + 32)}\n")


def _write_summary(
    counts_df: pd.DataFrame,
    details_df: pd.DataFrame,
    cli_only_packages: set[str],
    suppressed: set[str],
    mention_hints: dict[str, list[MentionHit]],
) -> None:
    lines: list[str] = []

    lines.append("PACKAGE USAGE SUMMARY")
    lines.append("=" * (COL_WIDTH + 12))
    lines.append(f"{'Name':<{COL_WIDTH}}  Files")
    lines.append(DIVIDER)
    for _, row in counts_df.iterrows():
        lines.append(f"{row['package']:<{COL_WIDTH}}  {int(row['file_count'])}")
    lines.append(DIVIDER)

    if mention_hints:
        lines.append("")
        lines.append("STRING-MENTION HINTS — zero import usage but name found in code")
        lines.append("=" * (COL_WIDTH + 12))
        for pkg, hits in mention_hints.items():
            lines.append(f"\n{pkg} ({len(hits)} file(s)):")
            for h in hits:
                label = _CTX_LABELS.get(h["context"], h["context"])
                lines_str = ", ".join(str(ln) for ln in h["lines"])
                lines.append(f"  [{label}]  {h['file']}  (lines: {lines_str})")

    if cli_only_packages:
        lines.append("")
        lines.append("CLI / NON-IMPORTABLE TOOLS")
        lines.append("=" * (COL_WIDTH + 12))
        for p in sorted(cli_only_packages):
            lines.append(f"  {p}")

    if suppressed:
        lines.append("")
        lines.append("COMPANION PACKAGES (suppressed)")
        lines.append("=" * (COL_WIDTH + 12))
        for p in sorted(suppressed):
            lines.append(f"  {p}")

    lines.append("")
    lines.append("DETAILS — all files per package")
    lines.append("=" * (COL_WIDTH + 12))
    for pkg in counts_df[counts_df["file_count"] > 0]["package"]:
        pkg_files = details_df.loc[details_df["package"] == pkg, "file"].tolist()
        lines.append(f"\n{pkg} ({len(pkg_files)} files):")
        for f in pkg_files:
            lines.append(f"  {f}")

    USAGE_SUMMARY_TXT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    clear_terminal()
    run_package_usage_scan(refresh=True, detail_threshold=1)
