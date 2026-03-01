"""
matrx_utils — unified utilities for Matrx projects.

All public APIs are importable from the root:

    from matrx_utils import (
        vcprint,
        FileManager,
        DataTransformer,
        CodeContextBuilder,
        ...
    )
"""

from .fancy_prints import (
    vclist,
    vcprint,
    pretty_print,
    print_link,
    print_truncated,
    plt,
    redact_object,
    redact_string,
    is_sensitive_content,
    MatrixPrintLog,
    to_matrx_json,
)
from .data_handling import DataTransformer
from .data_handling.validators import URLValidator, validate_url, validate_email
from .data_handling.errors import ValidationError
from .utils import (
    generate_directory_structure,
    generate_and_save_directory_structure,
    clear_terminal,
    cleanup_async_resources,
    async_test_wrapper,
)
from .file_handling import (
    FileManager,
    open_any_file,
    FileHandler,
    BatchHandler,
    BaseHandler,
    CloudMixin,
    StorageBackend,
    S3Backend,
    SupabaseBackend,
    ServerBackend,
    BackendRouter,
    is_cloud_uri,
    parse_uri,
    parse_storage_url,
    is_storage_url,
    ParsedStorageUrl,
)
from .file_handling.backends import (
    get_for_llm,
    get_for_llm_async,
    push_from_llm,
    push_from_llm_async,
    LLMInputMode,
    LLMOutputFormat,
)
from .field_processing import (
    camel_to_snake,
    snake_to_camel,
    convert_list_elements,
    process_field_definitions,
    process_object_field_definitions,
    process_batch_field_definitions,
    generate_complete_code,
)
from .conf import (
    settings,
    configure_settings,
    NotConfiguredError,
)
from .conf import (
    _restricted_task_and_definitions as RESTRICTED_TASK_AND_DEFINITIONS,
    _restricted_env_vars as RESTRICTED_ENV_VAR_NAMES,
    _restricted_service_names as RESTRICTED_SERVICE_NAMES,
    _restricted_fields_names as RESTRICTED_FIELD_NAMES,
)
from .react_analysis import (
    get_full_index_structure,
    ReactAnalysisConfig,
    analyze_react_exports,
    extract_and_analyze_all_exports,
    analyze_imports_from_directory_structure,
    find_name_collisions,
    analyze_file_collisions,
    get_full_collision_summary,
    find_invalid_imports,
    generate_index_ts,
    create_combined_structure,
    get_default_configs_with_overrides,
)
from .code_context import (
    ASTAnalyzer,
    ClassInfo,
    CodeContextBuilder,
    CodeContextConfig,
    CodeContextResult,
    CodeExtractor,
    DirectoryTree,
    FileDiscovery,
    FileNode,
    FunctionCallAnalyzer,
    FunctionCallGraph,
    FunctionCallInfo,
    FunctionInfo,
    ModuleAST,
    OutputMode,
    SignatureBlock,
    SignatureExtractor,
)
from .package_analysis import (
    CLI_PACKAGES,
    PACKAGE_COMPANIONS,
    PACKAGES_TO_IGNORE,
    report_dir,
    REPORT_REGISTRY,
    MENTION_SCAN_EXCLUDE_DIRS,
    MENTION_SCAN_EXCLUDE_FILES,
)
from .profiler.profile_utility import MatrxProfiler
from .data_in_code.make_updates import (
    update_data_in_code,
    update_history,
    clean_history,
    delete_from_history,
    fetch_data,
    update_data_in_code_with_ts,
)
from .local_dev_utils.import_checker import (
    check_imports,
    collect_python_files,
    extract_imports,
    print_results,
)
from .local_dev_utils.package_inspector import inspect_package
from .local_dev_utils.package_size_analyzer import get_package_sizes, run_package_size_report
from .local_dev_utils.package_usage_scanner import run_package_usage_scan
from .local_dev_utils.link_generator import create_links, process_directory_structure
from .local_dev_utils.react_links_direct import react_link_generator
from .local_dev_utils.create_directories import create_structure
from .local_dev_utils.copy_project import copy_directory_with_progress
from .local_dev_utils.next_test_dir_config import (
    extract_pages,
    format_title,
    generate_typescript_code,
    save_typescript_code,
)
from .code_context.generate_module_readme import run as generate_module_readme, run_cascade

__all__ = [
    # fancy_prints
    "vclist",
    "vcprint",
    "pretty_print",
    "print_link",
    "print_truncated",
    "plt",
    "redact_object",
    "redact_string",
    "is_sensitive_content",
    "MatrixPrintLog",
    "to_matrx_json",
    # data_handling
    "DataTransformer",
    "URLValidator",
    "validate_url",
    "validate_email",
    "ValidationError",
    # utils
    "generate_directory_structure",
    "generate_and_save_directory_structure",
    "clear_terminal",
    "cleanup_async_resources",
    "async_test_wrapper",
    # file_handling
    "FileManager",
    "open_any_file",
    "FileHandler",
    "BatchHandler",
    "BaseHandler",
    "CloudMixin",
    "StorageBackend",
    "S3Backend",
    "SupabaseBackend",
    "ServerBackend",
    "BackendRouter",
    "is_cloud_uri",
    "parse_uri",
    "parse_storage_url",
    "is_storage_url",
    "ParsedStorageUrl",
    "get_for_llm",
    "get_for_llm_async",
    "push_from_llm",
    "push_from_llm_async",
    "LLMInputMode",
    "LLMOutputFormat",
    # field_processing
    "camel_to_snake",
    "snake_to_camel",
    "convert_list_elements",
    "process_field_definitions",
    "process_object_field_definitions",
    "process_batch_field_definitions",
    "generate_complete_code",
    # conf
    "configure_settings",
    "settings",
    "NotConfiguredError",
    "RESTRICTED_SERVICE_NAMES",
    "RESTRICTED_ENV_VAR_NAMES",
    "RESTRICTED_TASK_AND_DEFINITIONS",
    "RESTRICTED_FIELD_NAMES",
    # react_analysis
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
    # code_context
    "ASTAnalyzer",
    "ClassInfo",
    "CodeContextBuilder",
    "CodeContextConfig",
    "CodeContextResult",
    "CodeExtractor",
    "DirectoryTree",
    "FileDiscovery",
    "FileNode",
    "FunctionCallAnalyzer",
    "FunctionCallGraph",
    "FunctionCallInfo",
    "FunctionInfo",
    "ModuleAST",
    "OutputMode",
    "SignatureBlock",
    "SignatureExtractor",
    # package_analysis
    "CLI_PACKAGES",
    "PACKAGE_COMPANIONS",
    "PACKAGES_TO_IGNORE",
    "report_dir",
    "REPORT_REGISTRY",
    "MENTION_SCAN_EXCLUDE_DIRS",
    "MENTION_SCAN_EXCLUDE_FILES",
    # profiler
    "MatrxProfiler",
    # data_in_code
    "update_data_in_code",
    "update_history",
    "clean_history",
    "delete_from_history",
    "fetch_data",
    "update_data_in_code_with_ts",
    # local_dev_utils
    "check_imports",
    "collect_python_files",
    "extract_imports",
    "print_results",
    "inspect_package",
    "get_package_sizes",
    "run_package_size_report",
    "run_package_usage_scan",
    "create_links",
    "process_directory_structure",
    "react_link_generator",
    "create_structure",
    "copy_directory_with_progress",
    "extract_pages",
    "format_title",
    "generate_typescript_code",
    "save_typescript_code",
    "generate_module_readme",
    "run_cascade",
]
