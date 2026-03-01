"""
Deep-dive inspector for a single package.

Tells you everything the scanner knows about one package:
  - What import names it installs (resolved from metadata)
  - Whether it is a CLI-only tool or a proper library
  - Every file in the codebase that imports it (with exact line numbers)
  - Every mention of the package name in code comments, strings, and text files

Usage (run directly):

    python -m utils.local_dev_utils.package_inspector selenium
    python -m utils.local_dev_utils.package_inspector pandas
    python -m utils.local_dev_utils.package_inspector opencv-python-headless

The package name is matched case-insensitively and with hyphen/underscore
normalisation, so all of these are equivalent:
    opencv-python-headless
    opencv_python_headless
    OpenCV-Python-Headless
"""

import ast
import importlib.metadata as importlib_meta
import io
import re
import sys
import tokenize
import warnings
from pathlib import Path

from matrx_utils.package_analysis.scan_excludes import MENTION_SCAN_EXCLUDE_DIRS, MENTION_SCAN_EXCLUDE_FILES
from matrx_utils.conf import settings

# ── Skip dirs (same as scanner) ───────────────────────────────────────────────
SKIP_DIRS = {
    ".venv", "venv", ".git", "__pycache__", ".mypy_cache",
    ".pytest_cache", "node_modules", "reports", "temp",
    "staticfiles", "migrations",
}

TEXT_EXTENSIONS: frozenset[str] = frozenset({
    ".md", ".rst", ".txt", ".toml", ".cfg", ".ini", ".yaml", ".yml",
})

_THIS_FILE = Path(__file__).resolve()
_ROOT      = _THIS_FILE.parent.parent.parent

# Hard-coded self-exclusions (scanner infrastructure files that mention package
# names as data).  Merged with user-supplied MENTION_SCAN_EXCLUDE_FILES.
_EXCLUDE_FILES: frozenset[Path] = frozenset({
    _THIS_FILE,
    _ROOT / "utils" / "local_dev_utils" / "package_usage_scanner.py",
    _ROOT / "utils" / "local_dev_utils" / "package_size_analyzer.py",
    _ROOT / "config" / "package_analysis" / "packages.py",
    _ROOT / "config" / "package_analysis" / "scan_excludes.py",
    _ROOT / "config" / "package_analysis" / "__init__.py",
    _ROOT / "config" / "settings.py",
    _ROOT / "requirements.txt",
    _ROOT / "pyproject.toml",
}) | frozenset((_ROOT / p).resolve() for p in MENTION_SCAN_EXCLUDE_FILES)

# Context labels
_CTX_CODE    = "code"
_CTX_COMMENT = "comment/docstring"
_CTX_STRING  = "string"
_CTX_TEXT    = "text/markdown"
_CTX_LABELS  = {_CTX_CODE: "real code", _CTX_COMMENT: "comment/docstring",
                _CTX_STRING: "string literal", _CTX_TEXT: "text/markdown"}
_CTX_ORDER   = {_CTX_CODE: 0, _CTX_STRING: 1, _CTX_COMMENT: 2, _CTX_TEXT: 3}

COL = 60
DIV = "─" * (COL + 20)
FAT = "═" * (COL + 20)


# ── Metadata helpers ──────────────────────────────────────────────────────────

def _normalize(name: str) -> str:
    return name.replace("-", "_").lower()


def _resolve_import_names(package_name: str) -> list[str]:
    try:
        dist = importlib_meta.distribution(package_name)
    except importlib_meta.PackageNotFoundError:
        return [_normalize(package_name)]

    top_txt = dist.read_text("top_level.txt")
    if top_txt:
        names = [n.strip() for n in top_txt.strip().splitlines() if n.strip()]
        if names:
            return names

    record = dist.read_text("RECORD") or ""
    mods: set[str] = set()
    for line in record.splitlines():
        path_part = line.split(",")[0]
        parts = path_part.replace("\\", "/").split("/")
        top = parts[0] if len(parts) >= 2 else (path_part[:-3] if path_part.endswith(".py") else "")
        if (top and re.match(r"^[A-Za-z][A-Za-z0-9_]*$", top)
                and "dist-info" not in top and ".data" not in top
                and top != "__pycache__"):
            mods.add(top)
    return sorted(mods) if mods else [_normalize(package_name)]


def _is_cli_only(package_name: str) -> bool:
    try:
        dist = importlib_meta.distribution(package_name)
    except importlib_meta.PackageNotFoundError:
        return False

    record = dist.read_text("RECORD") or ""
    non_meta = [
        line.split(",")[0] for line in record.splitlines()
        if ".dist-info/" not in line and not line.startswith("../")
    ]
    if not non_meta:
        return True

    dist_info_path = Path(str(dist._path))  # type: ignore[attr-defined]
    site_packages  = dist_info_path.parent
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


def _get_package_metadata(package_name: str) -> dict:
    try:
        dist  = importlib_meta.distribution(package_name)
        meta  = dist.metadata
        return {
            "name":        meta.get("Name", package_name),
            "version":     meta.get("Version", "unknown"),
            "summary":     meta.get("Summary", ""),
            "home_page":   meta.get("Home-page") or meta.get("Project-URL", ""),
            "requires":    dist.metadata.get_all("Requires-Dist") or [],
        }
    except importlib_meta.PackageNotFoundError:
        return {"name": package_name, "version": "NOT INSTALLED", "summary": "", "home_page": "", "requires": []}


# ── File collection ───────────────────────────────────────────────────────────

def _collect_python_files(base: Path) -> list[Path]:
    return [p for p in base.rglob("*.py")
            if not any(s in p.parts for s in SKIP_DIRS)]


def _collect_text_files(base: Path) -> list[Path]:
    all_skip = SKIP_DIRS | MENTION_SCAN_EXCLUDE_DIRS
    return [p for p in base.rglob("*")
            if not any(s in p.parts for s in all_skip)
            and p.suffix.lower() in TEXT_EXTENSIONS and p.is_file()]


# ── Import scan ───────────────────────────────────────────────────────────────

def _extract_imports(path: Path) -> set[str]:
    try:
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


def _find_import_lines(path: Path, import_names: set[str]) -> list[int]:
    """Returns line numbers where any of `import_names` are imported."""
    try:
        source = path.read_text(encoding="utf-8", errors="ignore")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return []
    lines: list[int] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0].lower() in import_names:
                    lines.append(node.lineno)
        elif isinstance(node, ast.ImportFrom):
            if node.module and node.module.split(".")[0].lower() in import_names:
                lines.append(node.lineno)
    return sorted(set(lines))


# ── Mention scan ──────────────────────────────────────────────────────────────

def _classify_line_ctx(line_ctx: dict[int, str], lineno: int) -> str:
    return line_ctx.get(lineno, _CTX_CODE)


def _build_line_ctx(source: str) -> dict[int, str]:
    ctx: dict[int, str] = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            kind, s_ln, e_ln = tok.type, tok.start[0], tok.end[0]
            if kind in (tokenize.COMMENT, tokenize.STRING):
                for ln in range(s_ln, e_ln + 1):
                    ctx.setdefault(ln, _CTX_COMMENT)
    except tokenize.TokenError:
        pass
    return ctx


def _find_mentions(
    package_name: str,
    py_files: list[Path],
    text_files: list[Path],
    base: Path,
) -> list[dict]:
    """
    Searches for the package name (and its normalised form) in all files.
    Returns list of {file, context, lines} dicts sorted by context severity.
    """
    terms   = list({package_name, _normalize(package_name)})
    pattern = re.compile(r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b", re.IGNORECASE)
    results: list[dict] = []

    for py_file in py_files:
        if py_file.resolve() in _EXCLUDE_FILES:
            continue
        if any(part in MENTION_SCAN_EXCLUDE_DIRS for part in py_file.parts):
            continue
        try:
            source = py_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not pattern.search(source):
            continue
        line_ctx = _build_line_ctx(source)
        hits = [(i, _classify_line_ctx(line_ctx, i))
                for i, line in enumerate(source.splitlines(), 1)
                if pattern.search(line)]
        if hits:
            dominant = min(hits, key=lambda x: _CTX_ORDER.get(x[1], 9))[1]
            results.append({
                "file":    str(py_file.relative_to(base)),
                "context": dominant,
                "lines":   [ln for ln, _ in hits],
                "details": hits,
            })

    for txt_file in text_files:
        if txt_file.resolve() in _EXCLUDE_FILES:
            continue
        try:
            text = txt_file.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not pattern.search(text):
            continue
        matched = [(i + 1, _CTX_TEXT)
                   for i, line in enumerate(text.splitlines())
                   if pattern.search(line)]
        if matched:
            results.append({
                "file":    str(txt_file.relative_to(base)),
                "context": _CTX_TEXT,
                "lines":   [ln for ln, _ in matched],
                "details": matched,
            })

    results.sort(key=lambda h: _CTX_ORDER.get(h["context"], 9))
    return results


# ── Display ───────────────────────────────────────────────────────────────────

def _print_section(title: str) -> None:
    print(f"\n{DIV}")
    print(f"  {title}")
    print(DIV)


def inspect_package(package_name: str) -> None:
    base       = settings.base_dir
    py_files   = _collect_python_files(base)
    text_files = _collect_text_files(base)

    # ── Resolve ───────────────────────────────────────────────────────────────
    import_names = {n.lower() for n in _resolve_import_names(package_name)}
    is_cli       = _is_cli_only(package_name)
    meta         = _get_package_metadata(package_name)

    print(f"\n{FAT}")
    print(f"  PACKAGE INSPECTOR  —  {meta['name']}  v{meta['version']}")
    print(FAT)
    if meta["summary"]:
        print(f"  {meta['summary']}")
    if meta["home_page"]:
        print(f"  {meta['home_page']}")

    # ── Metadata ──────────────────────────────────────────────────────────────
    _print_section("METADATA")
    print(f"  Import names  : {', '.join(sorted(import_names))}")
    print(f"  CLI-only tool : {'yes — no importable Python API' if is_cli else 'no'}")
    direct_reqs = [r for r in meta["requires"] if "extra ==" not in r]
    if direct_reqs:
        print(f"  Requires ({len(direct_reqs)})  : " + ", ".join(direct_reqs[:6]))
        if len(direct_reqs) > 6:
            print(f"  {'':14}  ... and {len(direct_reqs) - 6} more")

    # ── Import scan ───────────────────────────────────────────────────────────
    _print_section("IMPORT USAGE — files that directly import this package")
    import_hits: list[dict] = []
    for py_file in py_files:
        file_imports = _extract_imports(py_file)
        matched = import_names & file_imports
        if matched:
            lines = _find_import_lines(py_file, matched)
            import_hits.append({
                "file":         str(py_file.relative_to(base)),
                "import_names": sorted(matched),
                "lines":        lines,
            })

    if not import_hits:
        print(f"  No direct imports found across {len(py_files)} Python files.")
    else:
        print(f"  Found in {len(import_hits)} file(s):\n")
        for hit in sorted(import_hits, key=lambda h: h["file"]):
            lines_str = ", ".join(str(ln) for ln in hit["lines"])
            print(f"  {hit['file']}")
            print(f"    imported as : {', '.join(hit['import_names'])}")
            print(f"    line(s)     : {lines_str}")

    # ── Mention scan ──────────────────────────────────────────────────────────
    _print_section("MENTIONS — name found in comments, strings, or text files")
    mentions = _find_mentions(package_name, py_files, text_files, base)

    # Exclude files already shown in import hits (those are real usage, not mentions)
    import_hit_files = {h["file"] for h in import_hits}
    extra_mentions   = [m for m in mentions if m["file"] not in import_hit_files]

    if not extra_mentions:
        print("  No additional mentions found outside import-usage files.")
    else:
        # Group by context for summary
        by_ctx: dict[str, list[dict]] = {}
        for m in extra_mentions:
            by_ctx.setdefault(m["context"], []).append(m)

        for ctx in sorted(by_ctx, key=lambda c: _CTX_ORDER.get(c, 9)):
            label = _CTX_LABELS.get(ctx, ctx)
            group = by_ctx[ctx]
            print(f"\n  [{label}]  {len(group)} file(s):")
            for m in group:
                lines_str = ", ".join(str(ln) for ln in m["lines"][:5])
                if len(m["lines"]) > 5:
                    lines_str += f" (+{len(m['lines']) - 5})"
                print(f"    {m['file']}  (line {lines_str})")

    # ── Summary ───────────────────────────────────────────────────────────────
    _print_section("SUMMARY")
    verdict = (
        "CLI / non-importable tool — not expected to appear as an import"
        if is_cli
        else f"Imported in {len(import_hits)} file(s)"
    )
    print(f"  Import usage  : {verdict}")
    print(f"  Extra mentions: {len(extra_mentions)} file(s) outside import-usage files")

    if not is_cli and not import_hits and not extra_mentions:
        print("\n  ✗  No usage found anywhere — safe candidate for removal")
    elif not is_cli and not import_hits:
        print("\n  ?  No imports found — review mentions above before removing")
    else:
        print("\n  ✓  Package appears to be in use")

    print(f"\n{FAT}\n")


# ── Entry point ───────────────────────────────────────────────────────────────

def _load_top_packages() -> list[str]:
    """Return the top-N package names from the size report, or an empty list if unavailable."""
    try:
        from matrx_utils.local_dev_utils.package_size_analyzer import get_package_sizes, TOP_N
        df = get_package_sizes(direct_only=True, verbose=False)
        return df.head(TOP_N)["Package"].tolist()
    except Exception:
        return []


def _print_top_packages(packages: list[str]) -> None:
    print()
    print("  Top packages by installed size:")
    print()
    col = max(len(p) for p in packages) + 2
    for i, name in enumerate(packages, 1):
        print(f"  {i:>2}.  {name:<{col}}")
    print()
    print("  Enter a number (1–{n}), a custom package name, or Ctrl+C to quit.".format(n=len(packages)))
    print()


def main() -> None:
    if len(sys.argv) >= 2:
        inspect_package(sys.argv[1])
        return

    top_packages = _load_top_packages()

    if top_packages:
        _print_top_packages(top_packages)
    else:
        print()
        print("  (Could not load top packages — enter a package name directly.)")
        print()

    while True:
        try:
            raw = input("  Package (number or name, Ctrl+C to quit): ").strip()
        except KeyboardInterrupt:
            print("\n  Done.")
            return

        if not raw:
            continue

        if top_packages and raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(top_packages):
                target = top_packages[idx - 1]
            else:
                print(f"  Please enter a number between 1 and {len(top_packages)}.")
                continue
        else:
            target = raw

        inspect_package(target)

        try:
            input("  Inspect another? (Enter to continue, Ctrl+C to quit): ")
        except KeyboardInterrupt:
            print("\n  Done.")
            return


if __name__ == "__main__":
    from matrx_utils import clear_terminal
    clear_terminal()
    main()
