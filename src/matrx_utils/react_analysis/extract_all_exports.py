import os
from pathlib import Path

from utils.react_analysis.extract_exports import analyze_react_exports
from utils.react_analysis.utils import file_extension_supported, normalize_path


def extract_and_analyze_all_exports(directory_structure, config):
    """
    Walk the _files-keyed directory structure and extract exports from every supported file.

    Returns:
        dict[normalized_path, {"default_export": ..., "named_exports": [...]}]
    """
    analysis_results = {}
    root_directory = config["root_directory"]

    def traverse_structure(structure, current_path):
        for file_name in structure.get("_files", []):
            if file_name.startswith("index."):
                continue
            file_path = Path(current_path) / file_name
            if file_extension_supported(file_path, config):
                try:
                    normalized_file_path = normalize_path(str(file_path))
                    exports = analyze_react_exports(file_path, config)
                    analysis_results[normalized_file_path] = exports
                except Exception as e:
                    print(f"Error analyzing {file_path}: {e}")

        for sub_dir, sub_structure in structure.items():
            if sub_dir in ("_files", "full_paths"):
                continue
            if not isinstance(sub_structure, dict):
                continue
            traverse_structure(sub_structure, Path(current_path) / sub_dir)

    traverse_structure(directory_structure, root_directory)
    return analysis_results
