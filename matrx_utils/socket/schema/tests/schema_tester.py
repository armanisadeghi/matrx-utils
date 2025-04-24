from aidream.services.socket_schema.processor import ValidationSystem
from common import vcprint, get_sample_data

verbose = True
SAMPLE_APP_NAME = "socket_tasks"
DEFAULT_SUB_APP = "sample_tasks"

tasks_register = {
    "SCRAPER": {
        "SUB_APP": None,
        "TASKS": {
            "GET_DOMAIN_CONFIG_BY_ID": [
                "get_domain_config_by_id_1",
                "get_domain_config_by_id_2",
            ],
            "CREATE_DOMAIN_CONFIG": [
                "create_domain_config_1",
                "create_domain_config_2",
            ],
            "UPDATE_DOMAIN_CONFIG": [
                "update_domain_config_1",
                "update_domain_config_2",
            ],
            "CREATE_DOMAIN": ["create_domain_1", "create_domain_2"],
            "CREATE_INTERACTION_SETTINGS": [
                "create_interaction_settings_1",
                "create_interaction_settings_2",
            ],
            "GET_NOISE_CONFIG_BY_ID": [
                "get_noise_config_by_id_1",
                "get_noise_config_by_id_2",
            ],
            "GET_NOISE_CONFIGS": ["get_noise_configs_1", "get_noise_configs_2"],
            "GET_FILTER_CONFIG_BY_ID": [
                "get_filter_config_by_id_1",
                "get_filter_config_by_id_2",
            ],
            "GET_FILTER_CONFIGS": ["get_filter_configs_1", "get_filter_configs_2"],
            "GET_INTERACTION_SETTINGS_BY_ID": [
                "get_interaction_settings_by_id_1",
                "get_interaction_settings_by_id_2",
            ],
            "CREATE_NOISE_CONFIG": ["create_noise_config_1", "create_noise_config_2"],
            "CREATE_FILTER_CONFIG": [
                "create_filter_config_1",
                "create_filter_config_2",
            ],
            "SAVE_NOISE_CONFIG": ["save_noise_config_1", "save_noise_config_2"],
            "SAVE_FILTER_CONFIG": ["save_filter_config_1", "save_filter_config_2"],
            "SAVE_INTERACTION_SETTINGS": [
                "save_interaction_settings_1",
                "save_interaction_settings_2",
            ],
            "QUICK_SCRAPE": ["quick_scrape_1", "quick_scrape_2"],
            "CREATE_SCRAPE_TASKS": ["create_scrape_tasks_1", "create_scrape_tasks_2"],
            "SCRAPE_PAGE": ["scrape_page_1", "scrape_page_2"],
            "PARSE_RESPONSE_BY_ID": [
                "parse_response_by_id_1",
                "parse_response_by_id_2",
            ],
            "PARSE_RESPONSES_BY_ID": [
                "parse_responses_by_id_1",
                "parse_responses_by_id_2",
            ],
            "GET_SCRAPE_HISTORY_BY_URL": [
                "get_scrape_history_by_url_1",
                "get_scrape_history_by_url_2",
            ],
            "GET_SCRAPE_HISTORY_BY_TASK_ID": [
                "get_scrape_history_by_task_id_1",
                "get_scrape_history_by_task_id_2",
            ],
            "GET_SCRAPE_TASK_DETAILS": [
                "get_scrape_task_details_1",
                "get_scrape_task_details_2",
            ],
            "CREATE_FULL_SITE_SCRAPE_TASK": [
                "create_full_site_scrape_task_1",
                "create_full_site_scrape_task_2",
            ],
            "GET_FULL_SITE_SCRAPE_PROGRESS": [
                "get_full_site_scrape_progress_1",
                "get_full_site_scrape_progress_2",
            ],
            "GET_FULL_SITE_SCRAPE_PROGRESS_DETAILED": [
                "get_full_site_scrape_progress_detailed_1",
                "get_full_site_scrape_progress_detailed_2",
            ],
            "CANCEL_FULL_SITE_SCRAPE_TASK": [
                "cancel_full_site_scrape_task_1",
                "cancel_full_site_scrape_task_2",
            ],
            "PAUSE_FULL_SITE_SCRAPE_TASK": [
                "pause_full_site_scrape_task_1",
                "pause_full_site_scrape_task_2",
            ],
            "RESUME_FULL_SITE_SCRAPE_TASK": [
                "resume_full_site_scrape_task_1",
                "resume_full_site_scrape_task_2",
            ],
            "GET_PARSED_PAGES": ["get_parsed_pages_1", "get_parsed_pages_2"],
            "VIEW_PARSED_PAGE": ["view_parsed_page_1", "view_parsed_page_2"],
            "CREATE_CONTENT_GROUPING_RUN": [
                "create_content_grouping_run_1",
                "create_content_grouping_run_2",
            ],
            "TRACK_CONTENT_GROUPING_RUN": [
                "track_content_grouping_run_1",
                "track_content_grouping_run_2",
            ],
        },
    },
    "MARKDOWN": {
        "SUB_APP": "markdown",
        "TASKS": {
            "GET_CODE_BLOCKS_BY_LANGUAGE": [
                "GET_PYTHON_CODE_BLOCKS_PAYLOAD",
                "GET_INVALID_LANGUAGE_CODE_BLOCKS_PAYLOAD",
            ],
            "GET_SECTION_BLOCKS": [
                "GET_SECTION_BLOCK_PAYLOAD_1",
                "GET_SECTION_BLOCK_PAYLOAD_2",
            ],
            "GET_SECTION_GROUPS": [
                "GET_SECTION_GROUPS_PAYLOAD_1",
                "GET_SECTION_GROUPS_PAYLOAD_2",
            ],
            "GET_SEGMENTS": ["GET_SEGMENTS_PAYLOAD_1", "GET_SEGMENTS_PAYLOAD_2"],
        },
    },
    "COCKPIT": {
        "SUB_APP": "cockpit_tasks",
        "TASKS": {"COCKPIT_INSTANT": ["cockpit_task_1"]},
    },
}


def get_task_sample(sample_name: str, sub_app=None):
    if not sub_app:
        use_sub_app = DEFAULT_SUB_APP
    else:
        use_sub_app = sub_app

    sample = get_sample_data(app_name=SAMPLE_APP_NAME, sub_app=use_sub_app, data_name=sample_name)
    if sample is None:
        raise ValueError(f"No sample found in app: {SAMPLE_APP_NAME} sub_app: {use_sub_app} with name: {sample_name}")

    return sample


def try_validate_task(definition_key, sample_name):
    try:
        service, task = definition_key.split(".")
    except Exception as e:
        raise ValueError(f"Invalid definition key: {e}")

    if not tasks_register.get(service.upper()):
        raise ValueError(f"No test inputs found for {service.upper()}")

    tasks = tasks_register[service.upper()]["TASKS"]
    if task not in tasks:
        raise ValueError(f"No task with name {task} found")

    sub_app = tasks_register[service.upper()]["SUB_APP"]

    sample_task = get_task_sample(sample_name=sample_name, sub_app=sub_app)

    vcprint(sample_task, color="bright_pink", pretty=True, title="Using Sample")
    result = ValidationSystem.validate(sample_task, definition_key=definition_key)

    passed = False if result.get("errors") else True

    vcprint(
        result,
        pretty=True,
        color="green" if passed else "red",
        title="Successfully Validated" if passed else "Validation failed",
    )

    try:
        assert not result.get("errors")
    except AssertionError:
        for field_name, field_error in result["errors"].items():
            vcprint(
                title=f"Error at field: '{field_name}'",
                data=field_error,
                color="yellow",
            )

    return passed


def try_validate_app(app_name):
    """
    Test all tasks for a specific app.
    Does not stop execution if validation fails for a task.

    Args:
        app_name: The app name to validate (e.g., "SCRAPER")

    Returns:
        dict: Results with task names as keys and pass/fail status as values
    """
    # App header with visual separator
    vcprint("=" * 80, color="blue")
    vcprint(
        f"VALIDATING APP: {app_name.upper()}",
        color="bright_lavender",
        title="APP VALIDATION START",
    )
    vcprint("=" * 80, color="blue")

    app_name = app_name.upper()
    if not tasks_register.get(app_name):
        vcprint(f"App '{app_name}' not found in tasks register", color="red")
        return {}

    app_config = tasks_register[app_name]
    sub_app = app_config["SUB_APP"]
    tasks = app_config["TASKS"]

    results = {}
    task_count = len(tasks)
    current_task = 0

    for task_name, sample_names in tasks.items():
        current_task += 1
        definition_key = f"{app_name}.{task_name}"

        # Task header with visual separator
        vcprint("-" * 60, color="pink")
        vcprint(
            f"TASK {current_task}/{task_count}: {definition_key}",
            color="bright_pink",
            title="TASK VALIDATION",
        )

        # Use the first sample for each task
        if not sample_names:
            vcprint(f"No samples defined for task {task_name}", color="yellow")
            results[task_name] = False
            continue

        for sample_name in sample_names:
            try:
                passed = try_validate_task(definition_key, sample_name)
                results[task_name] = passed
            except Exception as e:
                vcprint(f"Error validating {definition_key}: {str(e)}", color="red")
                results[task_name] = False

    # App summary with visual separator
    vcprint("-" * 60, color="pink")
    total = len(results)
    passed = sum(1 for result in results.values() if result)

    vcprint(
        f"APP {app_name} SUMMARY: {passed}/{total} tasks passed validation",
        color="green" if passed == total else "yellow",
        title="APP VALIDATION COMPLETE",
    )

    return results


def try_validate_all_apps():
    """
    Test all apps and their tasks.
    Does not stop execution if validation fails for an app or task.

    Returns:
        dict: Results with app names as keys and app results as values
    """
    # Overall header with visual separator
    vcprint("#" * 100, color="blue")
    vcprint(
        "VALIDATION SUITE: TESTING ALL APPS",
        color="bright_lavender",
        title="FULL VALIDATION START",
    )
    vcprint("#" * 100, color="blue")

    all_results = {}
    app_count = len(tasks_register)
    current_app = 0

    for app_name in tasks_register.keys():
        current_app += 1
        vcprint(f"APP {current_app}/{app_count}: {app_name}", color="blue")
        all_results[app_name] = try_validate_app(app_name)

    # Overall summary with visual separator
    vcprint("#" * 100, color="green")
    total_tasks = sum(len(app_results) for app_results in all_results.values())
    passed_tasks = sum(sum(1 for result in app_results.values() if result) for app_results in all_results.values())

    # Create a detailed results table
    vcprint("DETAILED RESULTS:", color="bright_lavender")
    for app_name, app_results in all_results.items():
        app_passed = sum(1 for result in app_results.values() if result)
        app_total = len(app_results)
        status_color = "green" if app_passed == app_total else "yellow" if app_passed > 0 else "red"
        vcprint(f"  {app_name}: {app_passed}/{app_total} passed", color=status_color)

        # Detailed task results for each app
        for task_name, passed in app_results.items():
            task_color = "green" if passed else "red"
            status = "✓" if passed else "✗"
            vcprint(f"    {status} {task_name}", color=task_color)

    success_rate = (passed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    overall_color = "green" if passed_tasks == total_tasks else "yellow"

    vcprint(
        f"OVERALL VALIDATION SUMMARY: {passed_tasks}/{total_tasks} tasks passed ({success_rate:.1f}%)",
        color=overall_color,
        title="VALIDATION COMPLETE",
    )
    vcprint("#" * 100, color="green")

    return all_results


if __name__ == "__main__":
    # Test a single task
    # try_validate_task(definition_key="MARKDOWN.GET_CODE_BLOCKS_BY_LANGUAGE", sample_name="quick_scrape_1")

    # Test a specific app
    try_validate_app("MARKDOWN")

    # Test all apps
    # try_validate_all_apps()
