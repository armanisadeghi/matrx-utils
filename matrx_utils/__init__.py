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

# fancy_prints + utils MUST be imported first because several submodules
# below (code_context.generate_module_readme, data_handling.data_transformer,
# data_in_code.make_updates, local_dev_utils.import_checker, and others)
# do ``from matrx_utils import vcprint`` / ``clear_terminal`` at their own
# top level. If those names aren't bound on this module yet, the import
# resolves the partially-initialised package and raises
# ``ImportError: cannot import name '<name>'``. Pulling these two blocks
# up here breaks every one of those cycles in one move.
#
# 2026-06-12: this guarantee had REGRESSED — the `from .fancy_prints import …`
# block sat BELOW this `code_context` import, so the very first submodule
# (`code_context.generate_module_readme`, whose top level does
# `from matrx_utils import vcprint`) hit a partially-initialised matrx_utils
# and raised `ImportError: cannot import name 'vcprint'`. That broke EVERY
# entrypoint whose first matrx_utils touch came in through matrx_connect —
# including server boot (aidream/api/app.py) and the matrx-graph test suite.
# Bind the names those submodules need BEFORE importing them. BOTH the
# fancy_prints names (vcprint, …) AND the utils names (clear_terminal,
# detached_task, …) must be bound here — submodules imported below
# (code_context.generate_module_readme, local_dev_utils.import_checker, …)
# top-level-import them from matrx_utils, so they must already exist on this
# partially-initialised module. Do NOT move these two blocks below the
# submodule imports or boot breaks with "cannot import name 'vcprint' /
# 'clear_terminal'".
from .fancy_prints import (
    MatrixPrintLog,
    is_sensitive_content,
    plt,
    pretty_print,
    print_link,
    print_truncated,
    redact_object,
    redact_string,
    shorten_for_print,
    shorten_string_for_print,
    to_matrx_json,
    vclist,
    vcprint,
)
from .utils import (
    async_test_wrapper,
    cleanup_async_resources,
    clear_terminal,
    detached_task,
    generate_and_save_directory_structure,
    generate_directory_structure,
)
# Foundational primitives (hashing / ids / timeutils / http_client) bind HERE,
# before the heavier submodules below, for the same reason as fancy_prints/utils
# above: they have ZERO matrx_utils-internal dependencies (stdlib + httpx only),
# and submodules imported further down (e.g. file_handling.cloud_sync.idempotency)
# top-level-import `stable_hash` / `new_id` from this module — so the names must
# already be bound on the partially-initialised package when those imports run.
from .hashing import (
    hash_bytes,
    hash_chunks,
    hash_text,
    stable_hash,
    stable_json,
)
from .ids import (
    new_hex,
    new_id,
    new_uuid,
)
from .suggest import (
    did_you_mean,
    format_options,
    suggestion_line,
)
from .timeutils import (
    UTC,
    parse_iso,
    to_iso,
    utcnow,
)
from .http_client import (
    DEFAULT_LIMITS,
    DEFAULT_RETRY,
    DEFAULT_TIMEOUT,
    RetryPolicy,
    async_client,
    fetch_json,
    request_with_retries,
    with_overrides,
)
from .backoff import (
    compute_backoff_ms,
    retry_async,
)
from .data_uri import (
    decode_data_uri,
    encode_data_uri,
    is_data_uri,
    strip_data_uri,
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
from .code_context.generate_module_readme import readme_orchestrator, run_cascade
from .code_context.generate_module_readme import run as generate_module_readme
from .conf import (
    NotConfiguredError,
    configure_audit_logger,
    configure_cdn_purger,
    configure_context,
    configure_quota_check,
    configure_settings,
    get_audit_logger,
    get_cdn_purger,
    get_quota_check,
    settings,
)
from .conf import (
    _restricted_env_vars as RESTRICTED_ENV_VAR_NAMES,
)
from .conf import (
    _restricted_fields_names as RESTRICTED_FIELD_NAMES,
)
from .conf import (
    _restricted_service_names as RESTRICTED_SERVICE_NAMES,
)
from .conf import (
    _restricted_task_and_definitions as RESTRICTED_TASK_AND_DEFINITIONS,
)
from .ctx import (
    SimpleUserContext,
    UserContext,
    clear_manual_context,
    context_for_user,
    get_active_context,
    get_active_organization_id,
    get_active_user_id,
    get_system_file_access_reason,
    is_authenticated,
    set_manual_context,
    system_file_access,
)
from .data_handling import DataTransformer
from .data_handling.errors import ValidationError
from .data_handling.validators import URLValidator, validate_email, validate_url
from .data_in_code.make_updates import (
    clean_all_history,
    clean_history,
    delete_from_history,
    fetch_data,
    update_data_in_code,
    update_data_in_code_with_ts,
    update_history,
)
from .diagnostics import (
    EventLoopLagWatchdog,
    InflightRequestRegistry,
    RequestMarker,
    get_inflight_registry,
    start_loop_lag_watchdog,
)
from .fancy_prints import (
    MatrixPrintLog,
    is_sensitive_content,
    plt,
    pretty_print,
    print_link,
    print_truncated,
    redact_object,
    redact_string,
    shorten_for_print,
    shorten_string_for_print,
    to_matrx_json,
    vclist,
    vcprint,
)
from .field_processing import (
    camel_to_snake,
    convert_list_elements,
    generate_complete_code,
    process_batch_field_definitions,
    process_field_definitions,
    process_object_field_definitions,
    snake_to_camel,
)
from .file_handling import (
    BackendRouter,
    BaseHandler,
    BatchHandler,
    CloudMixin,
    FileHandler,
    FileManager,
    ParsedStorageUrl,
    S3Backend,
    ServerBackend,
    StorageBackend,
    SupabaseBackend,
    is_cloud_uri,
    is_storage_url,
    open_any_file,
    parse_storage_url,
    parse_uri,
)
from .file_handling.backends import (
    LLMInputMode,
    LLMOutputFormat,
    get_for_llm,
    get_for_llm_async,
    push_from_llm,
    push_from_llm_async,
)
from .local_dev_utils.copy_project import copy_directory_with_progress
from .local_dev_utils.create_directories import create_structure
from .local_dev_utils.import_checker import (
    check_imports,
    collect_python_files,
    extract_imports,
    print_results,
)
from .local_dev_utils.link_generator import create_links, process_directory_structure
from .local_dev_utils.next_test_dir_config import (
    extract_pages,
    format_title,
    generate_typescript_code,
    save_typescript_code,
)
from .local_dev_utils.package_inspector import inspect_package
from .local_dev_utils.package_size_analyzer import get_package_sizes, run_package_size_report
from .local_dev_utils.package_usage_scanner import run_package_usage_scan
from .local_dev_utils.react_links_direct import react_link_generator
from .package_analysis import (
    CLI_PACKAGES,
    MENTION_SCAN_EXCLUDE_DIRS,
    MENTION_SCAN_EXCLUDE_FILES,
    PACKAGE_COMPANIONS,
    PACKAGES_TO_IGNORE,
    REPORT_REGISTRY,
    report_dir,
)
from .profiler.profile_utility import MatrxProfiler
from .react_analysis import (
    ReactAnalysisConfig,
    analyze_file_collisions,
    analyze_imports_from_directory_structure,
    analyze_react_exports,
    create_combined_structure,
    extract_and_analyze_all_exports,
    find_invalid_imports,
    find_name_collisions,
    generate_index_ts,
    get_default_configs_with_overrides,
    get_full_collision_summary,
    get_full_index_structure,
)
from .runtime_env import (
    MatrxRole,
    MatrxStage,
    RuntimeEnv,
    RuntimeEnvError,
    get_runtime_env,
    reset_runtime_env_cache,
)
from .quality_engine import (
    ADJUSTMENT_PRESETS,
    DEFAULT_COMPOSITE_WEIGHTS,
    QUALITY_AXES,
    UTILITY_COMPOSITE_WEIGHTS,
    QualityVector,
    adjust,
    clamp_q,
    compute_composite_quality,
    derive,
    from_visible_score,
    logit,
    preserve,
    sigmoid,
    to_visible_score,
    weighted_geometric_mean,
)
from .rendezvous import (
    Rendezvous,
    RendezvousStats,
    rendezvous,
)
from .secure_random import (
    secure_choice,
    secure_randint,
    secure_sample,
    secure_shuffle,
)
from .utils import (
    async_test_wrapper,
    cleanup_async_resources,
    clear_terminal,
    detached_task,
    generate_and_save_directory_structure,
    generate_directory_structure,
)

__all__ = [
    # rendezvous
    "Rendezvous",
    "RendezvousStats",
    "rendezvous",
    # suggest
    "did_you_mean",
    "format_options",
    "suggestion_line",
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
    "shorten_for_print",
    "shorten_string_for_print",
    "MatrixPrintLog",
    "to_matrx_json",
    # diagnostics
    "EventLoopLagWatchdog",
    "start_loop_lag_watchdog",
    "InflightRequestRegistry",
    "RequestMarker",
    "get_inflight_registry",
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
    "configure_context",
    "configure_cdn_purger",
    "configure_quota_check",
    "configure_audit_logger",
    "get_cdn_purger",
    "get_quota_check",
    "get_audit_logger",
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
    "clean_all_history",
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
    "readme_orchestrator",
    # runtime_env — the two-axis host identity (MATRX_STAGE / MATRX_ROLE)
    "MatrxStage",
    "MatrxRole",
    "RuntimeEnv",
    "RuntimeEnvError",
    "get_runtime_env",
    "reset_runtime_env_cache",
    # secure_random — the single CSPRNG selection primitive
    "secure_choice",
    "secure_randint",
    "secure_sample",
    "secure_shuffle",
    # hashing — the single deterministic content-hash primitive
    "stable_json",
    "stable_hash",
    "hash_text",
    "hash_bytes",
    "hash_chunks",
    # ids — the single identifier-minting primitive
    "new_id",
    "new_uuid",
    "new_hex",
    # timeutils — the single UTC/ISO-8601 time primitive
    "utcnow",
    "parse_iso",
    "to_iso",
    "UTC",
    # http_client — the single configured async client + transient-retry policy
    "async_client",
    "request_with_retries",
    "fetch_json",
    "RetryPolicy",
    "with_overrides",
    "DEFAULT_TIMEOUT",
    "DEFAULT_LIMITS",
    "DEFAULT_RETRY",
    # backoff — the single retry/backoff primitive (general; http_client delegates here)
    "compute_backoff_ms",
    "retry_async",
    # data_uri — the single data: URI encode/decode/detect/strip primitive
    "encode_data_uri",
    "decode_data_uri",
    "is_data_uri",
    "strip_data_uri",
    # quality_engine — pure-math Matrx Quality Model (04_matrx_quality_model.md)
    "QUALITY_AXES",
    "ADJUSTMENT_PRESETS",
    "DEFAULT_COMPOSITE_WEIGHTS",
    "UTILITY_COMPOSITE_WEIGHTS",
    "QualityVector",
    "clamp_q",
    "logit",
    "sigmoid",
    "from_visible_score",
    "to_visible_score",
    "preserve",
    "adjust",
    "derive",
    "weighted_geometric_mean",
    "compute_composite_quality",
]
