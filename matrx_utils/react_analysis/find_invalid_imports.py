import os
from collections import defaultdict

from matrx_utils.react_analysis.utils import save_structure_to_json, load_json, resolve_alias


def find_invalid_imports(combined_structure, config):
    """
    Identify imports that resolve to paths not present in the combined structure.

    Returns:
        dict[file_path, list[{"type": str, "import": str, "reason": str}]]
    """
    invalid_imports: dict = defaultdict(list)
    all_valid_paths: set[str] = set()

    def _normalize(path):
        return os.path.normpath(path).lower()

    def collect_valid_paths(sub_structure):
        full_paths = sub_structure.get("full_paths", [])
        all_valid_paths.update(_normalize(p) for p in full_paths)
        for key, value in sub_structure.items():
            if isinstance(value, dict) and key not in ("_files", "full_paths"):
                collect_valid_paths(value)

    collect_valid_paths(combined_structure)

    def check_imports(sub_structure):
        _files = sub_structure.get("_files", [])
        full_paths = sub_structure.get("full_paths", [])

        for file, full_path in zip(_files, full_paths):
            file_details = sub_structure.get(file, {})
            if not file_details:
                continue

            imports = file_details.get("imports", {})

            def validate_imports(import_list, import_type):
                for imp in import_list:
                    resolved_path = imp.get("resolved_path")
                    source = imp.get("source", "")

                    if import_type == "aliased_imports":
                        resolved_path = resolve_alias(source, config)

                    normalized = _normalize(resolved_path) if resolved_path else None

                    if normalized and normalized not in all_valid_paths:
                        invalid_imports[full_path].append({
                            "type": import_type,
                            "import": source,
                            "reason": "Resolved path not found",
                        })

            for import_type in ("packages", "aliased_imports", "relative_imports"):
                validate_imports(imports.get(import_type, []), import_type)

        for key, value in sub_structure.items():
            if isinstance(value, dict) and key not in ("_files", "full_paths"):
                check_imports(value)

    check_imports(combined_structure)
    return dict(invalid_imports)
