"""
Report registry — maps report keys to their output directories under reports/.

Usage:
    from config.package_analysis import report_dir

    output_dir = report_dir("packages")
    all_packages_csv = output_dir / "all_packages.csv"

To register a new report category, add an entry to REPORT_REGISTRY below.
The directory will be created automatically on first access.
"""

from pathlib import Path

from config.settings import settings

REPORT_REGISTRY: dict[str, str] = {
    # key          → subdirectory name under reports/
    "packages":    "packages",
}


def report_dir(key: str) -> Path:
    if key not in REPORT_REGISTRY:
        raise KeyError(
            f"Unknown report key '{key}'. "
            f"Register it in config/package_analysis/reports.py REPORT_REGISTRY first."
        )
    path = settings.reports_dir / REPORT_REGISTRY[key]
    path.mkdir(parents=True, exist_ok=True)
    return path
