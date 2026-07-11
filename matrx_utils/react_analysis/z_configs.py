import os


def get_default_configs_with_overrides(overrides=None):
    """
    Default configuration for React/TypeScript codebase analysis.
    Override any key by passing a dict to `overrides`.
    """
    config = {
        "root_directory": "",
        "project_root": "",
        "ignore_directories": [
            ".",
            "_dev",
            ".history",
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
            "__tests__",
        ],
        "include_directories": [],
        "ignore_filenames": ["__init__.py"],
        "include_filenames": [],
        "ignore_extensions": [],
        "include_extensions": [],
        "extensions_for_analysis": [".js", ".jsx", ".ts", ".tsx", ".json", ".mjs"],
        "remove_comments_for_extensions": [".js", ".jsx", ".ts", ".tsx"],
        "include_files_override": True,
        "ignore_dir_with_no_files": True,
        "include_text_output": True,
        "alias_map": {},
        "include_export_types": ["const", "function", "type", "interface"],
        "ignore_export_list": [
            "metadata",
            "viewport",
            "Layout",
            "Page",
            "pages",
            "Component",
            "App",
            "Container",
            "View",
            "DemoPage",
            "Demo",
            "Test",
            "TestPage",
            "TestComponent",
            "Home",
            "MODULE_HOME",
            "MODULE_NAME",
            "DEFAULT_OPTIONS",
        ],
        "root_save_path": os.path.join(os.getcwd(), "temp", "dir_structure"),
        "combined_structure_file": os.path.join(os.getcwd(), "temp", "dir_structure", "combined_structure.json"),
        "output_collisions_file": os.path.join(os.getcwd(), "temp", "dir_structure", "collisions.json"),
        "output_page_collisions_file": os.path.join(os.getcwd(), "temp", "dir_structure", "page_collisions.json"),
        "output_invalid_imports_file": os.path.join(os.getcwd(), "temp", "dir_structure", "invalid_imports.json"),
        "import_analysis_file": os.path.join(os.getcwd(), "temp", "dir_structure", "import_analysis.json"),
        "export_analysis_file": os.path.join(os.getcwd(), "temp", "dir_structure", "export_analysis.json"),
        "output_collision_summary_file": os.path.join(os.getcwd(), "temp", "dir_structure", "collision_summary.json"),
        "output_file_collision_summary_file": os.path.join(os.getcwd(), "temp", "dir_structure", "file_collision_summary.json"),
        "output_full_collision_summary_file": os.path.join(os.getcwd(), "temp", "dir_structure", "full_collision_summary.json"),
    }

    if overrides:
        config.update(overrides)

    return config
