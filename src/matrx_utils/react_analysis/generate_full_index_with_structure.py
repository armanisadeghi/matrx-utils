import os
from pathlib import Path

from utils.react_analysis.analyze_react_imports import analyze_imports_from_directory_structure
from utils.react_analysis.extract_all_exports import extract_and_analyze_all_exports
from utils.react_analysis.utils import (
    save_combined_structure_to_txt,
    save_structure_to_json,
    normalize_path,
)


def create_combined_structure(config, directory_structure, export_analysis, import_analysis):
    """
    Merge export and import analysis into the _files-keyed directory structure.
    Each file entry gains {"exports": {...}, "imports": {...}}.
    """
    def add_structure_recursive(current_dir, path):
        full_structure = {"_files": [], "full_paths": []}

        for file in current_dir.get("_files", []):
            file_path = Path(path) / file
            file_str_path = normalize_path(str(file_path))

            exports = export_analysis.get(file_str_path, {})
            imports = import_analysis.get(file_str_path, {})

            full_structure["_files"].append(file)
            full_structure["full_paths"].append(file_str_path)

            if exports or imports:
                full_structure[file] = {"exports": exports, "imports": imports}

        for dir_name, sub_dir in current_dir.items():
            if dir_name in ("_files", "full_paths"):
                continue
            if not isinstance(sub_dir, dict):
                continue
            _, full_sub_structure = add_structure_recursive(sub_dir, Path(path) / dir_name)
            full_structure[dir_name] = full_sub_structure

        return {}, full_structure

    _, combined_structure = add_structure_recursive(
        directory_structure, Path(config["root_directory"])
    )
    return combined_structure
