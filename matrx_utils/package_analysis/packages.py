"""
Package scanning configuration.

Edit this file to control how the package scanner classifies packages.
There are four independent mechanisms — each covers a different case.

────────────────────────────────────────────────────────────────────────────────
PACKAGES_TO_IGNORE
────────────────────────────────────────────────────────────────────────────────
Packages excluded entirely from the scan — they will never appear in any output.

Only add a package here if BOTH conditions are true:
  1. We intentionally install and want it.
  2. It will never appear as a direct import in our code AND the auto-resolver
     (importlib.metadata) cannot detect its import name either.

The scanner already auto-resolves import-name mismatches (e.g. pymupdf → fitz,
opencv-python-headless → cv2) so most packages do NOT need to be listed here.

────────────────────────────────────────────────────────────────────────────────
PACKAGE_COMPANIONS
────────────────────────────────────────────────────────────────────────────────
Companion/satellite packages that must be installed alongside a primary package
but are never imported directly.  The primary package is the key; its companions
are suppressed from the "unused" list whenever the primary is detected as used.

Format:
    "primary-package": {"companion-a", "companion-b"}

When to add something here:
  - The companion resolves to the SAME import name as the primary (e.g. pymupdfb
    also maps to `pymupdf` in metadata, so the scanner can't tell them apart).
  - The companion is a pure binary/data sidecar with no importable module.

────────────────────────────────────────────────────────────────────────────────
CLI_PACKAGES  (auto-detected — override here only if needed)
────────────────────────────────────────────────────────────────────────────────
The scanner detects CLI-only packages automatically by checking whether the
package's top-level __init__.py is a zero-byte stub (the ruff/black/mypy
pattern).  Only add a package here if auto-detection fails for that specific
package (i.e. it has a non-empty __init__.py but still has no useful Python API).

────────────────────────────────────────────────────────────────────────────────
"""

PACKAGES_TO_IGNORE: set[str] = {
    # --- PACKAGING: Python/pip toolchain, never imported by app code ---
    "pip",
    "setuptools",
    "wheel",
    "uv",
}


PACKAGE_COMPANIONS: dict[str, set[str]] = {
    # pymupdf ships as two separate pip packages; pymupdfb is the binary
    # companion — it maps to the same `pymupdf` import name so the scanner
    # can never distinguish it.  Suppress pymupdfb whenever pymupdf is used.
    "pymupdf": {"pymupdfb"},
}


CLI_PACKAGES: set[str] = {
    # Add packages here only if auto-detection (empty __init__.py check) fails.
    # "black",   # example — already auto-detected
    # "mypy",    # example — already auto-detected
}
