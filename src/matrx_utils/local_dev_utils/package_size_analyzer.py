import importlib.metadata
import os
import re
import tomllib
from pathlib import Path

import pandas as pd
from matrx_utils import clear_terminal

from config.package_analysis import report_dir
from config.settings import settings

TOP_N = 20
OUTPUT_DIR = report_dir("packages")

ALL_PACKAGES_CSV = OUTPUT_DIR / "all_packages.csv"
ALL_PACKAGES_JSON = OUTPUT_DIR / "all_packages.json"
TOP_PACKAGES_CSV = OUTPUT_DIR / "top_packages.csv"
TOP_PACKAGES_JSON = OUTPUT_DIR / "top_packages.json"

COL_WIDTH = 40


def _load_direct_deps() -> set[str]:
    """
    Returns the set of normalised package names that are direct dependencies
    of this project (listed in pyproject.toml [project.dependencies]).

    Only direct deps are relevant for the usage scanner — transitive deps are
    managed by uv/pip and cannot be removed independently, so flagging them
    as "unused" is meaningless noise.
    """
    pyproject = settings.base_dir / "pyproject.toml"
    if not pyproject.exists():
        return set()
    with pyproject.open("rb") as f:
        data = tomllib.load(f)
    deps = data.get("project", {}).get("dependencies", [])
    return {
        re.split(r"[>=<!;\s\[]", dep)[0].strip().lower().replace("-", "_")
        for dep in deps
        if dep.strip()
    }


def _print_size_table(df: pd.DataFrame, title: str) -> None:
    divider = "-" * (COL_WIDTH + 12)
    print(f"\n{title}")
    print(f"{'Name':<{COL_WIDTH}}  Size (MB)")
    print(divider)
    for _, row in df.iterrows():
        print(f"{row['Package']:<{COL_WIDTH}}  {row['Size_MB']}")
    print(divider)


def get_package_sizes(direct_only: bool = True, verbose: bool = True) -> pd.DataFrame:
    """
    Measures the installed size of packages.

    Args:
        direct_only: When True (default), only includes packages that are
                     direct dependencies in pyproject.toml.  Transitive deps
                     are excluded because they cannot be removed independently.
        verbose:     When True (default), prints the per-package size table
                     to the terminal.  Set to False when called programmatically
                     to suppress the noise.
    """
    direct_deps = _load_direct_deps() if direct_only else set()

    rows: list[dict] = []
    skipped_transitive = 0

    if verbose:
        divider = "-" * (COL_WIDTH + 12)
        print(f"\n{'Name':<{COL_WIDTH}}  Size (MB)")
        print(divider)

    for pkg in importlib.metadata.distributions():
        name = pkg.metadata.get("Name", "unknown")
        norm = name.lower().replace("-", "_")

        if direct_only and norm not in direct_deps:
            skipped_transitive += 1
            continue

        try:
            files = pkg.files
            if not files:
                continue

            size = 0
            for f in files:
                file_path = f.locate()
                if os.path.exists(file_path):
                    size += os.path.getsize(file_path)

            size_mb = size / (1024 * 1024)
            size_display = round(size_mb) if size_mb >= 1 else round(size_mb, 1)

            if verbose:
                print(f"{name:<{COL_WIDTH}}  {size_display}")
            rows.append({"Package": name, "Size_MB": size_display})
        except Exception as e:
            if verbose:
                print(f"  [skip] {name}: {e}")
            continue

    if verbose:
        divider = "-" * (COL_WIDTH + 12)
        print(divider)
        if direct_only:
            print(f"  (skipped {skipped_transitive} transitive dependencies)")

    df = pd.DataFrame(rows).sort_values(by="Size_MB", ascending=False).reset_index(drop=True)
    return df


def run_package_size_report(verbose: bool = True) -> pd.DataFrame:
    df = get_package_sizes(verbose=verbose)

    df.to_csv(ALL_PACKAGES_CSV, index=False)
    df.to_json(ALL_PACKAGES_JSON, orient="records", indent=2)

    top_df = df.head(TOP_N)
    top_df.to_csv(TOP_PACKAGES_CSV, index=False)
    top_df.to_json(TOP_PACKAGES_JSON, orient="records", indent=2)

    if verbose:
        _print_size_table(top_df, f"Top {TOP_N} Direct Dependencies by Size")
        print(f"\nSaved files:")
        print(f"  {ALL_PACKAGES_CSV}")
        print(f"  {ALL_PACKAGES_JSON}")
        print(f"  {TOP_PACKAGES_CSV}")
        print(f"  {TOP_PACKAGES_JSON}")

    return df


if __name__ == "__main__":
    clear_terminal()
    run_package_size_report()
