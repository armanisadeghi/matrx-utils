"""
react_links_direct — Generate Next.js navigation links via CodeContextBuilder.

Builds directory structure using the unified code_context system and then
produces a navigation links JSON from directories containing page.tsx.
"""
import json
import os

from utils.local_dev_utils.link_generator import process_directory_structure


default_config = {
    "root_directory": "",
    "ignore_directories": [
        ".",
        "notes",
        "templates",
        "venv",
        "external libraries",
        "scratches",
        "consoles",
        ".git",
        "node_modules",
        "__pycache__",
        ".github",
        ".idea",
        "frontend",
        ".next",
    ],
    "include_directories": [],
    "ignore_filenames": [],
    "include_filenames": ["page.tsx"],
    "ignore_extensions": [],
    "include_extensions": [],
    "include_files_override": True,
    "ignore_dir_with_no_files": True,
    "root_save_path": os.path.join(os.getcwd(), "temp", "dir_structure"),
    "exclude_dynamic_routes": True,
}


def react_link_generator(project_root=None, target_directory=None, exclude_dynamic_routes=True):
    """
    Generate Next.js navigation links for directories that contain page.tsx.

    Uses CodeContextBuilder to produce a _files-keyed JSON structure, then
    saves it to a temp file and extracts navigation links from it.
    """
    import json as _json
    import tempfile
    from utils.code_context import CodeContextBuilder

    root_dir = project_root or default_config["root_directory"]
    if target_directory:
        scan_root = os.path.join(root_dir, target_directory)
    else:
        scan_root = root_dir

    builder = CodeContextBuilder(
        project_root=scan_root,
        output_mode="tree_only",
        overrides={
            "include_files": {"add": ["page.tsx"]},
        },
        show_all_tree_directories=False,
        prune_empty_directories=True,
    )
    result = builder.build()
    structure = result.to_files_json(root=builder.project_root)

    save_path = default_config["root_save_path"]
    os.makedirs(save_path, exist_ok=True)
    root_name = os.path.basename(scan_root)
    structure_path = os.path.join(save_path, f"{root_name}_structure.json")
    with open(structure_path, "w") as f:
        _json.dump(structure, f, indent=4)

    links, links_output_file = process_directory_structure(
        structure_path, root_name, exclude_dynamic_routes
    )

    return links, links_output_file, structure_path


def main(config):
    links, links_output_file, directory_structure_path = react_link_generator(
        project_root=config.get("project_root"),
        target_directory=config.get("target_directory"),
        exclude_dynamic_routes=config.get("exclude_dynamic_routes", True),
    )
    print(json.dumps({"links": links}, indent=4))
    print(f"Links saved to: {links_output_file}")
    print(f"Structure saved to: {directory_structure_path}")


if __name__ == "__main__":
    config = {
        "project_root": "/path/to/project",
        "target_directory": "app",
        "exclude_dynamic_routes": True,
    }
    main(config)
