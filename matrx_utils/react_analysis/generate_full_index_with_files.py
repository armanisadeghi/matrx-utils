import os

from matrx_utils.react_analysis.analyze_react_imports import analyze_imports_from_directory_structure
from matrx_utils.react_analysis.extract_all_exports import extract_and_analyze_all_exports
from matrx_utils.react_analysis.generate_full_index_with_structure import create_combined_structure
from matrx_utils.react_analysis.utils import save_structure_to_json
from matrx_utils.react_analysis.z_configs import get_default_configs_with_overrides


def save_summary_to_txt(structure, output_file):
    """Write a human-readable summary of the combined structure to a text file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for file, details in structure.get("files", {}).items():
            f.write(f"File: {file}\n")
            f.write("  Exports:\n")
            f.write(f"    Default: {details['exports'].get('default', 'None')}\n")
            named_exports = details["exports"].get("named", [])
            f.write(f"    Named: {', '.join(named_exports) if named_exports else 'None'}\n")
            f.write("  Imports:\n")

            def write_import_list(import_type, imports):
                f.write(f"    {import_type.title()}:\n")
                for imp in imports:
                    source_or_path = imp.get("resolved_path", imp.get("source", "Unknown"))
                    default_import = imp.get("default", "None")
                    named_imports = ", ".join(imp.get("named", [])) if imp.get("named") else "None"
                    f.write(f"      {source_or_path} (default: {default_import}, named: {named_imports})\n")

            write_import_list("packages", details["imports"].get("packages", []))
            write_import_list("aliased", details["imports"].get("aliased_imports", []))
            write_import_list("relative", details["imports"].get("relative_imports", []))

            duplicates = details["imports"].get("duplicates", [])
            f.write("  Duplicates: " + (", ".join(duplicates) if duplicates else "None") + "\n")
            f.write("-" * 50 + "\n")
    print(output_file)


def save_combined_structure(export_analysis, import_analysis, config):
    combined_structure = {"files": {}}
    for file_path, exports in export_analysis.items():
        imports = import_analysis.get(file_path, {})
        combined_structure["files"][file_path] = {"exports": exports, "imports": imports}

    json_output_file = os.path.join(config["root_save_path"], "combined_structure.json")
    save_structure_to_json(combined_structure, json_output_file)

    summary_output_file = os.path.join(config["root_save_path"], "summary.txt")
    save_summary_to_txt(combined_structure, summary_output_file)

    return combined_structure, json_output_file, summary_output_file
