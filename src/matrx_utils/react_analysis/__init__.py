"""
react_analysis — React/TypeScript codebase intelligence pipeline.

Consumes the canonical _files-keyed JSON from utils.code_context to perform
export/import analysis, name collision detection, and invalid import validation.

Primary entry points:
    from utils.react_analysis import get_full_index_structure, ReactAnalysisConfig

    config = ReactAnalysisConfig(
        root_directory="/path/to/frontend",
        project_root="/path/to/project",
        alias_map={"@/": "/path/to/frontend"},
    )
    combined_structure = get_full_index_structure(config.to_dict(), save_json=True)
"""

from .get_and_analyze import get_full_index_structure, ReactAnalysisConfig
from .extract_exports import analyze_react_exports
from .extract_all_exports import extract_and_analyze_all_exports
from .analyze_react_imports import analyze_imports_from_directory_structure
from .name_collision_analyer import find_name_collisions, analyze_file_collisions
from .collision_summary import get_full_collision_summary
from .find_invalid_imports import find_invalid_imports
from .generate_react_index import generate_index_ts
from .generate_full_index_with_structure import create_combined_structure
from .z_configs import get_default_configs_with_overrides

__all__ = [
    "get_full_index_structure",
    "ReactAnalysisConfig",
    "analyze_react_exports",
    "extract_and_analyze_all_exports",
    "analyze_imports_from_directory_structure",
    "find_name_collisions",
    "analyze_file_collisions",
    "get_full_collision_summary",
    "find_invalid_imports",
    "generate_index_ts",
    "create_combined_structure",
    "get_default_configs_with_overrides",
]
