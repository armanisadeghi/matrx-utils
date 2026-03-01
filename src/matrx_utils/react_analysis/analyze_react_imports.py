import os
import re
from pathlib import Path

from utils.react_analysis.utils import (
    file_extension_supported,
    read_file_content,
    normalize_path,
    save_structure_to_json,
)
from utils.react_analysis.z_configs import get_default_configs_with_overrides


def analyze_imports(file_path, alias_map, config):
    """
    Parse all import statements in a file and classify them as packages,
    relative, or aliased imports.  Also detects duplicates.
    """
    results = {
        "packages": [],
        "relative_imports": [],
        "aliased_imports": [],
        "duplicates": [],
    }

    content = read_file_content(file_path, config, remove_comments=True)

    import_pattern = re.compile(
        r"import\s+(?:(?P<default>[a-zA-Z0-9_$]+)\s*,\s*)?(?:\{(?P<named>[^\}]+)\})?\s+"
        r"from\s+['\"](?P<source>[^'\"]+)['\"];?"
    )

    seen_imports: set[str] = set()

    for match in re.finditer(import_pattern, content):
        source = match.group("source")
        default = match.group("default")
        named = match.group("named")

        if source in seen_imports:
            results["duplicates"].append(source)
            continue
        seen_imports.add(source)

        import_details = {
            "source": source,
            "default": default,
            "named": [name.strip() for name in named.split(",")] if named else [],
        }

        if source.startswith("@/"):
            resolved_path = source.replace("@/", alias_map.get("@/", ""), 1)
            import_details["resolved_path"] = normalize_path(resolved_path)
            results["aliased_imports"].append(import_details)
        elif source.startswith("@"):
            results["packages"].append(import_details)
        elif not source.startswith(".") and not source.startswith("/"):
            results["packages"].append(import_details)
        else:
            resolved_path = os.path.normpath(os.path.join(os.path.dirname(str(file_path)), source))
            import_details["resolved_path"] = normalize_path(resolved_path)
            results["relative_imports"].append(import_details)

    return results


def analyze_imports_from_directory_structure(directory_structure, config):
    """
    Walk the _files-keyed directory structure and analyze imports for every supported file.

    Returns:
        dict[normalized_path, import_analysis_dict]
    """
    analysis_results = {}
    root_directory = config["root_directory"]
    alias_map = config.get("alias_map", {})

    def traverse_structure(structure, current_path):
        for file_name in structure.get("_files", []):
            if file_name.startswith("index."):
                continue
            file_path = Path(current_path) / file_name
            if file_extension_supported(file_path, config):
                try:
                    normalized_file_path = normalize_path(str(file_path))
                    imports = analyze_imports(normalized_file_path, alias_map, config)
                    analysis_results[normalized_file_path] = imports
                except Exception as e:
                    print(f"Error analyzing imports in {file_path}: {e}")

        for sub_dir, sub_structure in structure.items():
            if sub_dir in ("_files", "full_paths"):
                continue
            if not isinstance(sub_structure, dict):
                continue
            traverse_structure(sub_structure, Path(current_path) / sub_dir)

    traverse_structure(directory_structure, root_directory)
    return analysis_results
