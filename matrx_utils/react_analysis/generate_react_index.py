import os
import re
from pathlib import Path

from matrx_utils.react_analysis.extract_all_exports import extract_and_analyze_all_exports


def generate_index_ts(directory_structure, analysis_results, root_directory, output_file="index-gen.ts"):
    """
    Generate an index.ts barrel file from the export analysis.
    Duplicate names are commented out with explanatory messages.

    Args:
        directory_structure: _files-keyed dict (from CodeContextBuilder.build().to_files_json())
        analysis_results:    output of extract_and_analyze_all_exports()
        root_directory:      project root used to compute relative import paths
        output_file:         filename for the generated barrel (default: index-gen.ts)
    """
    output_lines = []
    name_tracker: dict[str, bool] = {}

    def get_import_path(file_path):
        relative_path = Path(file_path).relative_to(root_directory).as_posix()
        return re.sub(r"\.[a-zA-Z0-9]+$", "", f"./{relative_path}")

    named_exports = []
    default_exports = []

    for file_path, exports in analysis_results.items():
        import_path = get_import_path(file_path)

        if exports["default_export"]:
            component_name = exports["default_export"]
            if component_name in name_tracker:
                output_lines.append(f"// Duplicate default export '{component_name}' from '{import_path}' is commented out.")
                output_lines.append(f"// export {{ default as {component_name} }} from '{import_path}';")
            else:
                name_tracker[component_name] = True
                default_exports.append(f"export {{ default as {component_name} }} from '{import_path}';")

        for component_name in exports.get("named_exports", []):
            if component_name in name_tracker:
                output_lines.append(f"// Duplicate named export '{component_name}' from '{import_path}' is commented out.")
                output_lines.append(f"// import {{ {component_name} }} from '{import_path}';")
            else:
                name_tracker[component_name] = True
                named_exports.append((component_name, import_path))

    output_lines.extend(default_exports)

    grouped_export_names = []
    for component_name, import_path in named_exports:
        output_lines.append(f"import {{ {component_name} }} from '{import_path}';")
        grouped_export_names.append(component_name)

    grouped_export_names = sorted(set(grouped_export_names))
    grouped_export_names = [n for n in grouped_export_names if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", n)]

    if grouped_export_names:
        output_lines.append(f"export {{ {', '.join(grouped_export_names)} }};")

    output_file_path = Path(root_directory) / output_file
    with open(output_file_path, "w", encoding="utf-8") as file:
        file.write("\n".join(output_lines))
    print(str(output_file_path))
