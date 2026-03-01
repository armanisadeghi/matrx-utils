import os
import re
from pathlib import Path

from utils.react_analysis.utils import read_file_content


def preprocess_content(content):
    """Handle React.memo and other known export patterns before regex extraction."""
    content = re.sub(
        r"export\s+default\s+React\.memo\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)",
        r"export default \1",
        content,
    )
    return content


def analyze_react_exports(file_path, config):
    """
    Extracts all export declarations from a React/TS file.

    Returns:
        {"default_export": str | None, "named_exports": list[str]}
    """
    content = read_file_content(file_path, config, remove_comments=True)
    content = re.sub(r"//.*?|/\*[\s\S]*?\*/|<!--[\s\S]*?-->", "", content, flags=re.MULTILINE)
    content = preprocess_content(content)

    export_types = config.get("include_export_types", [])
    export_types_regex = "|".join(export_types)
    named_export_direct_pattern = rf"export\s+({export_types_regex})\s+([a-zA-Z_][a-zA-Z0-9_]*)"
    named_export_list_pattern = r"export\s+\{\s*([^}]*)\s*\}"
    default_export_pattern = r"export\s+default\s+(?:async\s+)?(?:function\s+)?(?:[a-zA-Z_][a-zA-Z0-9_]*\(|)([a-zA-Z_][a-zA-Z0-9_]*)(?:\)|)"

    default_export = None
    named_exports: set[str] = set()

    default_match = re.search(default_export_pattern, content)
    if default_match:
        default_export = default_match.group(1)

    for match in re.finditer(named_export_direct_pattern, content):
        named_exports.add(match.group(2))

    for match in re.finditer(named_export_list_pattern, content):
        export_list = match.group(1).split(",")
        named_exports.update(name.strip() for name in export_list if name.strip())

    ignore_export_list = set(config.get("ignore_export_list", []))
    named_exports.difference_update(ignore_export_list)

    if default_export in named_exports:
        named_exports.remove(default_export)

    return {
        "default_export": default_export if default_export not in ignore_export_list else None,
        "named_exports": list(named_exports),
    }
