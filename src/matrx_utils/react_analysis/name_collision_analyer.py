import os
from collections import defaultdict

from utils.react_analysis.utils import save_structure_to_json, load_json, normalize_path


def find_name_collisions(combined_structure):
    """
    Traverse the combined structure and find export names declared in more than one file.

    Returns:
        dict[export_name, list[file_path]]  — only names that appear in 2+ files.
    """
    collisions: dict = defaultdict(list)

    def traverse_structure(sub_structure):
        _files = sub_structure.get("_files", [])
        full_paths = sub_structure.get("full_paths", [])

        for file, full_path in zip(_files, full_paths):
            file_details = sub_structure.get(file, {})
            exports = file_details.get("exports", {})
            if not exports:
                continue

            named_exports = exports.get("named_exports", [])
            default_export = exports.get("default_export")
            combined_exports = named_exports + ([default_export] if default_export else [])

            for name in combined_exports:
                collisions[name].append(normalize_path(full_path))

        for key, value in sub_structure.items():
            if isinstance(value, dict) and key not in ("_files", "full_paths"):
                traverse_structure(value)

    traverse_structure(combined_structure)
    return {name: paths for name, paths in collisions.items() if len(paths) > 1}


def analyze_file_collisions(combined_structure, name_collisions):
    """
    For each file, identify which of its exports/imports appear in `name_collisions`.

    Returns:
        dict[file_path, {"exports": list[str], "imports": list[str]}]
    """
    page_analysis: dict = defaultdict(lambda: {"exports": set(), "imports": set()})

    def traverse_structure(sub_structure):
        _files = sub_structure.get("_files", [])
        full_paths = sub_structure.get("full_paths", [])

        for file, full_path in zip(_files, full_paths):
            file_details = sub_structure.get(file, {})
            if not file_details:
                continue

            exports = file_details.get("exports", {})
            imports = file_details.get("imports", {})

            default_export = exports.get("default_export")
            if default_export and default_export in name_collisions:
                page_analysis[full_path]["exports"].add(default_export)

            for name in exports.get("named_exports", []):
                if name in name_collisions:
                    page_analysis[full_path]["exports"].add(name)

            def check_imports(import_list):
                for imp in import_list:
                    default_import = imp.get("default")
                    if default_import and default_import in name_collisions:
                        page_analysis[full_path]["imports"].add(default_import)
                    for named in imp.get("named", []):
                        if named in name_collisions:
                            page_analysis[full_path]["imports"].add(named)

            for import_type in ("packages", "aliased_imports", "relative_imports"):
                check_imports(imports.get(import_type, []))

        for key, value in sub_structure.items():
            if isinstance(value, dict) and key not in ("_files", "full_paths"):
                traverse_structure(value)

    traverse_structure(combined_structure)

    return {
        page: {"exports": list(data["exports"]), "imports": list(data["imports"])}
        for page, data in page_analysis.items()
        if data["exports"] or data["imports"]
    }
