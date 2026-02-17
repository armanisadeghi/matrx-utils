"""
print_link cross-platform test.

Run this BEFORE and AFTER the fix to compare terminal output.
Check that every file path line is clickable in your terminal.
"""
import os
import sys
import platform

from matrx_utils import print_link
from matrx_utils.fancy_prints.fancy_prints import plt


def print_header(text: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}")


def test_print_link() -> None:
    print_header("ENVIRONMENT INFO")
    print(f"  platform.system()  = {platform.system()}")
    print(f"  sys.platform       = {sys.platform}")
    print(f"  os.name            = {os.name}")
    print(f"  TERM_PROGRAM       = {os.environ.get('TERM_PROGRAM', 'N/A')}")
    print(f"  WSL_DISTRO_NAME    = {os.environ.get('WSL_DISTRO_NAME', 'N/A')}")
    print(f"  VSCODE_*           = {bool(os.environ.get('TERM_PROGRAM') == 'vscode')}")

    # --- URLs (should just print as-is) ---
    print_header("URLs (should print as-is, always clickable)")
    print_link("https://www.google.com")
    print_link("https://github.com/user/repo")
    print_link("http://localhost:3000")

    # --- Relative file path ---
    print_header("RELATIVE PATH (should resolve to absolute and be clickable)")
    relative_path = "src/matrx_utils/data_handling/utils.py"
    print(f"  raw input: {relative_path}")
    print_link(relative_path)

    # --- Absolute file path (current OS) ---
    print_header("ABSOLUTE PATH (should be clickable)")
    abs_path = os.path.abspath("src/matrx_utils/fancy_prints/fancy_prints.py")
    print(f"  raw input: {abs_path}")
    print_link(abs_path)

    # --- Directory path ---
    print_header("DIRECTORY PATH (should be clickable)")
    dir_path = os.path.abspath("src/matrx_utils/fancy_prints")
    print(f"  raw input: {dir_path}")
    print_link(dir_path)

    # --- plt (print link with title) ---
    print_header("PLT (title + link)")
    plt(abs_path, "Fancy Prints Source")

    # --- Plain print for comparison ---
    print_header("PLAIN PRINT FOR COMPARISON (no print_link)")
    print(abs_path)
    print(relative_path)

    print_header("TEST COMPLETE")


if __name__ == "__main__":
    test_print_link()
