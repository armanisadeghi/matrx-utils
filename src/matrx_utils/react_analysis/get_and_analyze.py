"""
React/TypeScript Codebase Analysis Pipeline
============================================
Entry point for full frontend codebase intelligence.

This module is a CONSUMER of utils.code_context: it calls CodeContextBuilder to generate
the canonical _files-keyed JSON, then runs export/import analysis, collision detection,
and invalid import validation on top of that data.

Typical usage:
    from matrx_utils.react_analysis import get_full_index_structure, ReactAnalysisConfig

    config = ReactAnalysisConfig(
        root_directory="/path/to/frontend",
        project_root="/path/to/project",
        alias_map={"@/": "/path/to/frontend"},
    )
    combined_structure = get_full_index_structure(config.to_dict(), save_json=True)
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from matrx_utils.react_analysis.analyze_react_imports import analyze_imports_from_directory_structure
from matrx_utils.react_analysis.extract_all_exports import extract_and_analyze_all_exports
from matrx_utils.react_analysis.generate_full_index_with_structure import create_combined_structure
from matrx_utils.react_analysis.find_invalid_imports import find_invalid_imports
from matrx_utils.react_analysis.name_collision_analyer import find_name_collisions, analyze_file_collisions
from matrx_utils.react_analysis.collision_summary import get_full_collision_summary
from matrx_utils.react_analysis.utils import save_structure_to_json, save_combined_structure_to_txt
from matrx_utils.react_analysis.z_configs import get_default_configs_with_overrides


@dataclass
class ReactAnalysisConfig:
    """
    Typed configuration wrapper for the React analysis pipeline.
    Delegates to get_default_configs_with_overrides for dict-based APIs.
    """
    root_directory: str = ""
    project_root: str = ""
    root_save_path: str = field(default_factory=lambda: os.path.join(os.getcwd(), "temp", "react_analysis"))
    alias_map: dict[str, str] = field(default_factory=dict)
    extensions_for_analysis: list[str] = field(default_factory=lambda: [".js", ".jsx", ".ts", ".tsx", ".mjs"])
    remove_comments_for_extensions: list[str] = field(default_factory=lambda: [".js", ".jsx", ".ts", ".tsx"])
    include_export_types: list[str] = field(default_factory=lambda: ["const", "function", "type", "interface"])
    ignore_export_list: list[str] = field(default_factory=list)
    ignore_directories: list[str] = field(default_factory=lambda: [
        ".", "_dev", ".history", "node_modules", "__pycache__", ".git", ".next", "__tests__",
    ])

    def to_dict(self) -> dict[str, Any]:
        base = get_default_configs_with_overrides()
        overrides: dict[str, Any] = {
            "root_directory": self.root_directory,
            "project_root": self.project_root,
            "root_save_path": self.root_save_path,
            "alias_map": self.alias_map,
            "extensions_for_analysis": self.extensions_for_analysis,
            "remove_comments_for_extensions": self.remove_comments_for_extensions,
            "include_export_types": self.include_export_types,
            "ignore_export_list": self.ignore_export_list,
            "ignore_directories": self.ignore_directories,
            # Derive output file paths from root_save_path
            "combined_structure_file": os.path.join(self.root_save_path, "combined_structure.json"),
            "output_collisions_file": os.path.join(self.root_save_path, "collisions.json"),
            "output_page_collisions_file": os.path.join(self.root_save_path, "page_collisions.json"),
            "output_invalid_imports_file": os.path.join(self.root_save_path, "invalid_imports.json"),
            "import_analysis_file": os.path.join(self.root_save_path, "import_analysis.json"),
            "export_analysis_file": os.path.join(self.root_save_path, "export_analysis.json"),
            "output_collision_summary_file": os.path.join(self.root_save_path, "collision_summary.json"),
            "output_file_collision_summary_file": os.path.join(self.root_save_path, "file_collision_summary.json"),
            "output_full_collision_summary_file": os.path.join(self.root_save_path, "full_collision_summary.json"),
        }
        base.update(overrides)
        return base


def _build_directory_structure(config: dict) -> dict:
    """
    Use CodeContextBuilder to generate the canonical _files-keyed JSON structure.
    This replaces the old generate_and_save_directory_structure() call.
    """
    from matrx_utils.code_context import CodeContextBuilder

    root_dir = config["root_directory"]
    project_root = config.get("project_root", root_dir)

    # Map react analysis config → CodeContextBuilder overrides
    ignore_dirs = config.get("ignore_directories", [])
    include_dirs = config.get("include_directories", [])

    builder = CodeContextBuilder(
        project_root=project_root,
        subdirectory=os.path.relpath(root_dir, project_root) if root_dir != project_root else None,
        output_mode="tree_only",
        overrides={
            "exclude_directories": {"add": ignore_dirs},
            "include_extensions": {"add": config.get("extensions_for_analysis", [])},
            "include_directories": {"add": include_dirs} if include_dirs else {},
        },
        show_all_tree_directories=False,
        prune_empty_directories=config.get("ignore_dir_with_no_files", True),
    )
    result = builder.build()
    return result.to_files_json(root=Path(project_root))


def get_full_index_structure(config: dict, save_json: bool = False, save_text: bool = False) -> dict:
    """
    Full React analysis pipeline.

    1. Builds directory structure via CodeContextBuilder (canonical _files-keyed JSON).
    2. Analyzes exports across all supported files.
    3. Analyzes imports across all supported files.
    4. Merges into a combined structure with per-file exports+imports.
    5. Detects name collisions and invalid imports.

    Returns:
        combined_structure (dict) — _files-keyed JSON with exports/imports per file.
    """
    directory_structure = _build_directory_structure(config)

    export_analysis = extract_and_analyze_all_exports(
        directory_structure=directory_structure,
        config=config,
    )

    import_analysis = analyze_imports_from_directory_structure(
        directory_structure=directory_structure,
        config=config,
    )

    combined_structure = create_combined_structure(
        config=config,
        directory_structure=directory_structure,
        export_analysis=export_analysis,
        import_analysis=import_analysis,
    )

    invalid_imports = find_invalid_imports(combined_structure, config)
    name_collisions = find_name_collisions(combined_structure)
    page_collisions = analyze_file_collisions(combined_structure, name_collisions)
    get_full_collision_summary(combined_structure=combined_structure, config=config, verbose=False)

    if save_json:
        save_structure_to_json(combined_structure, config.get("combined_structure_file"))
        save_structure_to_json(name_collisions, config.get("output_collisions_file"))
        save_structure_to_json(page_collisions, config.get("output_page_collisions_file"))
        save_structure_to_json(invalid_imports, config.get("output_invalid_imports_file"))

    if save_text:
        summary_output_file = os.path.join(config.get("root_save_path", ""), "summary.txt")
        save_combined_structure_to_txt(combined_structure, summary_output_file)

    return combined_structure


if __name__ == "__main__":
    overrides = {
        "root_directory": "/path/to/your/frontend",
        "project_root": "/path/to/your/project",
    }
    config = get_default_configs_with_overrides(overrides=overrides)
    combined_structure = get_full_index_structure(config=config, save_json=True, save_text=True)
