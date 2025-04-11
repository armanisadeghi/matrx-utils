# File: database/schema_builder/helpers/auto_config.py
recipe_auto_config = {'model_pascal': 'Recipe', 'model_name': 'recipe', 'model_name_plural': 'recipes', 'model_name_snake': 'recipe', 'relations': ['compiled_recipe', 'ai_agent', 'recipe_display', 'recipe_processor', 'recipe_model', 'recipe_broker', 'recipe_message', 'recipe_tool', 'recipe_function'], 'filter_fields': ['status', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_domain_auto_config = {'model_pascal': 'ScrapeDomain', 'model_name': 'scrape_domain', 'model_name_plural': 'scrape_domains', 'model_name_snake': 'scrape_domain', 'relations': ['scrape_path_pattern', 'scrape_job', 'scrape_domain_quick_scrape_settings', 'scrape_domain_disallowed_notes', 'scrape_domain_robots_txt', 'scrape_domain_notes', 'scrape_domain_sitemap', 'scrape_task', 'scrape_quick_failure_log'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_job_auto_config = {'model_pascal': 'ScrapeJob', 'model_name': 'scrape_job', 'model_name_plural': 'scrape_jobs', 'model_name_snake': 'scrape_job', 'relations': ['scrape_domain', 'scrape_cycle_tracker', 'scrape_task'], 'filter_fields': ['scrape_domain_id', 'start_urls', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_provider_auto_config = {'model_pascal': 'AiProvider', 'model_name': 'ai_provider', 'model_name_plural': 'ai_providers', 'model_name_snake': 'ai_provider', 'relations': ['ai_settings', 'ai_model'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


data_input_component_auto_config = {'model_pascal': 'DataInputComponent', 'model_name': 'data_input_component', 'model_name_plural': 'data_input_components', 'model_name_snake': 'data_input_component', 'relations': ['message_broker', 'broker', 'data_broker'], 'filter_fields': ['options', 'component'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_cache_policy_auto_config = {'model_pascal': 'ScrapeCachePolicy', 'model_name': 'scrape_cache_policy', 'model_name_plural': 'scrape_cache_policies', 'model_name_snake': 'scrape_cache_policy', 'relations': ['scrape_path_pattern_cache_policy'], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_path_pattern_auto_config = {'model_pascal': 'ScrapePathPattern', 'model_name': 'scrape_path_pattern', 'model_name_plural': 'scrape_path_patterns', 'model_name_snake': 'scrape_path_pattern', 'relations': ['scrape_domain', 'scrape_configuration', 'scrape_path_pattern_override', 'scrape_path_pattern_cache_policy'], 'filter_fields': ['scrape_domain_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_path_pattern_cache_policy_auto_config = {'model_pascal': 'ScrapePathPatternCachePolicy', 'model_name': 'scrape_path_pattern_cache_policy', 'model_name_plural': 'scrape_path_pattern_cache_policies', 'model_name_snake': 'scrape_path_pattern_cache_policy', 'relations': ['scrape_cache_policy', 'scrape_path_pattern', 'scrape_cycle_tracker', 'scrape_parsed_page'], 'filter_fields': ['scrape_cache_policy_id', 'scrape_path_pattern_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_model_auto_config = {'model_pascal': 'AiModel', 'model_name': 'ai_model', 'model_name_plural': 'ai_models', 'model_name_snake': 'ai_model', 'relations': ['ai_provider', 'ai_model_endpoint', 'ai_settings', 'recipe_model'], 'filter_fields': ['name', 'common_name', 'provider', 'model_class', 'model_provider'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


broker_auto_config = {'model_pascal': 'Broker', 'model_name': 'broker', 'model_name_plural': 'brokers', 'model_name_snake': 'broker', 'relations': ['data_input_component', 'recipe_broker', 'registered_function', 'automation_boundary_broker'], 'filter_fields': ['data_type', 'default_source', 'custom_source_component', 'default_destination', 'output_component'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


data_output_component_auto_config = {'model_pascal': 'DataOutputComponent', 'model_name': 'data_output_component', 'model_name_plural': 'data_output_components', 'model_name_snake': 'data_output_component', 'relations': ['data_broker'], 'filter_fields': ['component_type'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


flashcard_data_auto_config = {'model_pascal': 'FlashcardData', 'model_name': 'flashcard_data', 'model_name_plural': 'flashcard_datas', 'model_name_snake': 'flashcard_data', 'relations': ['flashcard_history', 'flashcard_set_relations', 'flashcard_images'], 'filter_fields': ['user_id', 'shared_with'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


organizations_auto_config = {'model_pascal': 'Organizations', 'model_name': 'organizations', 'model_name_plural': 'organization', 'model_name_snake': 'organizations', 'relations': ['permissions', 'organization_members', 'organization_invitations'], 'filter_fields': ['created_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


projects_auto_config = {'model_pascal': 'Projects', 'model_name': 'projects', 'model_name_plural': 'project', 'model_name_snake': 'projects', 'relations': ['project_members', 'tasks'], 'filter_fields': ['created_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_cycle_tracker_auto_config = {'model_pascal': 'ScrapeCycleTracker', 'model_name': 'scrape_cycle_tracker', 'model_name_plural': 'scrape_cycle_trackers', 'model_name_snake': 'scrape_cycle_tracker', 'relations': ['scrape_job', 'scrape_path_pattern_cache_policy', 'scrape_cycle_run', 'scrape_parsed_page'], 'filter_fields': ['scrape_path_pattern_cache_policy_id', 'scrape_job_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


tasks_auto_config = {'model_pascal': 'Tasks', 'model_name': 'tasks', 'model_name_plural': 'task', 'model_name_snake': 'tasks', 'relations': ['projects', 'task_assignments', 'task_attachments', 'task_comments'], 'filter_fields': ['project_id', 'created_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_endpoint_auto_config = {'model_pascal': 'AiEndpoint', 'model_name': 'ai_endpoint', 'model_name_plural': 'ai_endpoints', 'model_name_snake': 'ai_endpoint', 'relations': ['ai_model_endpoint', 'ai_settings'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


automation_matrix_auto_config = {'model_pascal': 'AutomationMatrix', 'model_name': 'automation_matrix', 'model_name_plural': 'automation_matrixes', 'model_name_snake': 'automation_matrix', 'relations': ['action', 'automation_boundary_broker'], 'filter_fields': ['cognition_matrices'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


data_broker_auto_config = {'model_pascal': 'DataBroker', 'model_name': 'data_broker', 'model_name_plural': 'data_brokers', 'model_name_snake': 'data_broker', 'relations': ['data_input_component', 'data_output_component', 'broker_value', 'message_broker'], 'filter_fields': ['data_type', 'input_component', 'color', 'output_component'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


message_template_auto_config = {'model_pascal': 'MessageTemplate', 'model_name': 'message_template', 'model_name_plural': 'message_templates', 'model_name_snake': 'message_template', 'relations': ['message_broker', 'recipe_message'], 'filter_fields': ['role', 'type'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


registered_function_auto_config = {'model_pascal': 'RegisteredFunction', 'model_name': 'registered_function', 'model_name_plural': 'registered_functions', 'model_name_snake': 'registered_function', 'relations': ['broker', 'system_function', 'arg'], 'filter_fields': ['return_broker'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_cycle_run_auto_config = {'model_pascal': 'ScrapeCycleRun', 'model_name': 'scrape_cycle_run', 'model_name_plural': 'scrape_cycle_runs', 'model_name_snake': 'scrape_cycle_run', 'relations': ['scrape_cycle_tracker', 'scrape_task', 'scrape_parsed_page'], 'filter_fields': ['scrape_cycle_tracker_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_override_auto_config = {'model_pascal': 'ScrapeOverride', 'model_name': 'scrape_override', 'model_name_plural': 'scrape_overrides', 'model_name_snake': 'scrape_override', 'relations': ['scrape_override_value', 'scrape_path_pattern_override'], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_task_auto_config = {'model_pascal': 'ScrapeTask', 'model_name': 'scrape_task', 'model_name_plural': 'scrape_tasks', 'model_name_snake': 'scrape_task', 'relations': ['scrape_cycle_run', 'scrape_domain', 'scrape_job', 'scrape_task_response', 'scrape_parsed_page'], 'filter_fields': ['scrape_domain_id', 'scrape_job_id', 'scrape_cycle_run_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


system_function_auto_config = {'model_pascal': 'SystemFunction', 'model_name': 'system_function', 'model_name_plural': 'system_functions', 'model_name_snake': 'system_function', 'relations': ['registered_function', 'tool', 'recipe_function'], 'filter_fields': ['rf_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_settings_auto_config = {'model_pascal': 'AiSettings', 'model_name': 'ai_settings', 'model_name_plural': 'ai_setting', 'model_name_snake': 'ai_settings', 'relations': ['ai_endpoint', 'ai_model', 'ai_provider', 'ai_agent'], 'filter_fields': ['ai_endpoint', 'ai_provider', 'ai_model'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


audio_label_auto_config = {'model_pascal': 'AudioLabel', 'model_name': 'audio_label', 'model_name_plural': 'audio_labels', 'model_name_snake': 'audio_label', 'relations': ['audio_recording'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


category_auto_config = {'model_pascal': 'Category', 'model_name': 'category', 'model_name_plural': 'categories', 'model_name_snake': 'category', 'relations': ['subcategory'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


compiled_recipe_auto_config = {'model_pascal': 'CompiledRecipe', 'model_name': 'compiled_recipe', 'model_name_plural': 'compiled_recipes', 'model_name_snake': 'compiled_recipe', 'relations': ['recipe', 'applet'], 'filter_fields': ['recipe_id', 'user_id', 'version'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


conversation_auto_config = {'model_pascal': 'Conversation', 'model_name': 'conversation', 'model_name_plural': 'conversations', 'model_name_snake': 'conversation', 'relations': ['message'], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


display_option_auto_config = {'model_pascal': 'DisplayOption', 'model_name': 'display_option', 'model_name_plural': 'display_options', 'model_name_snake': 'display_option', 'relations': ['recipe_display'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


flashcard_sets_auto_config = {'model_pascal': 'FlashcardSets', 'model_name': 'flashcard_sets', 'model_name_plural': 'flashcard_set', 'model_name_snake': 'flashcard_sets', 'relations': ['flashcard_set_relations'], 'filter_fields': ['user_id', 'shared_with'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


processor_auto_config = {'model_pascal': 'Processor', 'model_name': 'processor', 'model_name_plural': 'processors', 'model_name_snake': 'processor', 'relations': ['self_reference', 'recipe_processor'], 'filter_fields': ['depends_default'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_configuration_auto_config = {'model_pascal': 'ScrapeConfiguration', 'model_name': 'scrape_configuration', 'model_name_plural': 'scrape_configurations', 'model_name_snake': 'scrape_configuration', 'relations': ['scrape_path_pattern', 'scrape_parsed_page'], 'filter_fields': ['scrape_path_pattern_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_path_pattern_override_auto_config = {'model_pascal': 'ScrapePathPatternOverride', 'model_name': 'scrape_path_pattern_override', 'model_name_plural': 'scrape_path_pattern_overrides', 'model_name_snake': 'scrape_path_pattern_override', 'relations': ['scrape_override', 'scrape_path_pattern', 'scrape_parsed_page'], 'filter_fields': ['scrape_path_pattern_id', 'scrape_override_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_task_response_auto_config = {'model_pascal': 'ScrapeTaskResponse', 'model_name': 'scrape_task_response', 'model_name_plural': 'scrape_task_responses', 'model_name_snake': 'scrape_task_response', 'relations': ['scrape_task', 'scrape_parsed_page'], 'filter_fields': ['scrape_task_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


subcategory_auto_config = {'model_pascal': 'Subcategory', 'model_name': 'subcategory', 'model_name_plural': 'subcategories', 'model_name_snake': 'subcategory', 'relations': ['category', 'applet'], 'filter_fields': ['category_id', 'features'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


tool_auto_config = {'model_pascal': 'Tool', 'model_name': 'tool', 'model_name_plural': 'tools', 'model_name_snake': 'tool', 'relations': ['system_function', 'recipe_tool'], 'filter_fields': ['system_function'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


transformer_auto_config = {'model_pascal': 'Transformer', 'model_name': 'transformer', 'model_name_plural': 'transformers', 'model_name_snake': 'transformer', 'relations': ['action'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


wc_claim_auto_config = {'model_pascal': 'WcClaim', 'model_name': 'wc_claim', 'model_name_plural': 'wc_claims', 'model_name_snake': 'wc_claim', 'relations': ['wc_report'], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


wc_impairment_definition_auto_config = {'model_pascal': 'WcImpairmentDefinition', 'model_name': 'wc_impairment_definition', 'model_name_plural': 'wc_impairment_definitions', 'model_name_snake': 'wc_impairment_definition', 'relations': ['wc_injury'], 'filter_fields': ['finger_type'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


wc_report_auto_config = {'model_pascal': 'WcReport', 'model_name': 'wc_report', 'model_name_plural': 'wc_reports', 'model_name_snake': 'wc_report', 'relations': ['wc_claim', 'wc_injury'], 'filter_fields': ['claim_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


action_auto_config = {'model_pascal': 'Action', 'model_name': 'action', 'model_name_plural': 'actions', 'model_name_snake': 'action', 'relations': ['automation_matrix', 'transformer'], 'filter_fields': ['matrix', 'transformer'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


admins_auto_config = {'model_pascal': 'Admins', 'model_name': 'admins', 'model_name_plural': 'admin', 'model_name_snake': 'admins', 'relations': [], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_agent_auto_config = {'model_pascal': 'AiAgent', 'model_name': 'ai_agent', 'model_name_plural': 'ai_agents', 'model_name_snake': 'ai_agent', 'relations': ['ai_settings', 'recipe'], 'filter_fields': ['recipe_id', 'ai_settings_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_model_endpoint_auto_config = {'model_pascal': 'AiModelEndpoint', 'model_name': 'ai_model_endpoint', 'model_name_plural': 'ai_model_endpoints', 'model_name_snake': 'ai_model_endpoint', 'relations': ['ai_endpoint', 'ai_model'], 'filter_fields': ['ai_model_id', 'ai_endpoint_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


ai_training_data_auto_config = {'model_pascal': 'AiTrainingData', 'model_name': 'ai_training_data', 'model_name_plural': 'ai_training_datas', 'model_name_snake': 'ai_training_data', 'relations': [], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


applet_auto_config = {'model_pascal': 'Applet', 'model_name': 'applet', 'model_name_plural': 'applets', 'model_name_snake': 'applet', 'relations': ['compiled_recipe', 'subcategory'], 'filter_fields': ['type', 'compiled_recipe_id', 'subcategory_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


arg_auto_config = {'model_pascal': 'Arg', 'model_name': 'arg', 'model_name_plural': 'args', 'model_name_snake': 'arg', 'relations': ['registered_function'], 'filter_fields': ['data_type', 'registered_function'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


audio_recording_auto_config = {'model_pascal': 'AudioRecording', 'model_name': 'audio_recording', 'model_name_plural': 'audio_recordings', 'model_name_snake': 'audio_recording', 'relations': ['audio_label'], 'filter_fields': ['user_id', 'label'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


audio_recording_users_auto_config = {'model_pascal': 'AudioRecordingUsers', 'model_name': 'audio_recording_users', 'model_name_plural': 'audio_recording_user', 'model_name_snake': 'audio_recording_users', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


automation_boundary_broker_auto_config = {'model_pascal': 'AutomationBoundaryBroker', 'model_name': 'automation_boundary_broker', 'model_name_plural': 'automation_boundary_brokers', 'model_name_snake': 'automation_boundary_broker', 'relations': ['broker', 'automation_matrix'], 'filter_fields': ['matrix', 'broker', 'spark_source', 'beacon_destination'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


broker_value_auto_config = {'model_pascal': 'BrokerValue', 'model_name': 'broker_value', 'model_name_plural': 'broker_values', 'model_name_snake': 'broker_value', 'relations': ['data_broker'], 'filter_fields': ['user_id', 'data_broker', 'tags'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


bucket_structures_auto_config = {'model_pascal': 'BucketStructures', 'model_name': 'bucket_structures', 'model_name_plural': 'bucket_structure', 'model_name_snake': 'bucket_structures', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


bucket_tree_structures_auto_config = {'model_pascal': 'BucketTreeStructures', 'model_name': 'bucket_tree_structures', 'model_name_plural': 'bucket_tree_structure', 'model_name_snake': 'bucket_tree_structures', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


emails_auto_config = {'model_pascal': 'Emails', 'model_name': 'emails', 'model_name_plural': 'email', 'model_name_snake': 'emails', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


extractor_auto_config = {'model_pascal': 'Extractor', 'model_name': 'extractor', 'model_name_plural': 'extractors', 'model_name_snake': 'extractor', 'relations': [], 'filter_fields': ['output_type'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


file_structure_auto_config = {'model_pascal': 'FileStructure', 'model_name': 'file_structure', 'model_name_plural': 'file_structures', 'model_name_snake': 'file_structure', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


flashcard_history_auto_config = {'model_pascal': 'FlashcardHistory', 'model_name': 'flashcard_history', 'model_name_plural': 'flashcard_histories', 'model_name_snake': 'flashcard_history', 'relations': ['flashcard_data'], 'filter_fields': ['flashcard_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


flashcard_images_auto_config = {'model_pascal': 'FlashcardImages', 'model_name': 'flashcard_images', 'model_name_plural': 'flashcard_image', 'model_name_snake': 'flashcard_images', 'relations': ['flashcard_data'], 'filter_fields': ['flashcard_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


flashcard_set_relations_auto_config = {'model_pascal': 'FlashcardSetRelations', 'model_name': 'flashcard_set_relations', 'model_name_plural': 'flashcard_set_relation', 'model_name_snake': 'flashcard_set_relations', 'relations': ['flashcard_data', 'flashcard_sets'], 'filter_fields': ['flashcard_id', 'set_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


full_spectrum_positions_auto_config = {'model_pascal': 'FullSpectrumPositions', 'model_name': 'full_spectrum_positions', 'model_name_plural': 'full_spectrum_position', 'model_name_snake': 'full_spectrum_positions', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


message_auto_config = {'model_pascal': 'Message', 'model_name': 'message', 'model_name_plural': 'messages', 'model_name_snake': 'message', 'relations': ['conversation'], 'filter_fields': ['conversation_id', 'role', 'type', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


message_broker_auto_config = {'model_pascal': 'MessageBroker', 'model_name': 'message_broker', 'model_name_plural': 'message_brokers', 'model_name_snake': 'message_broker', 'relations': ['data_broker', 'data_input_component', 'message_template'], 'filter_fields': ['message_id', 'broker_id', 'default_component'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


organization_invitations_auto_config = {'model_pascal': 'OrganizationInvitations', 'model_name': 'organization_invitations', 'model_name_plural': 'organization_invitation', 'model_name_snake': 'organization_invitations', 'relations': ['organizations'], 'filter_fields': ['organization_id', 'role', 'invited_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


organization_members_auto_config = {'model_pascal': 'OrganizationMembers', 'model_name': 'organization_members', 'model_name_plural': 'organization_member', 'model_name_snake': 'organization_members', 'relations': ['organizations'], 'filter_fields': ['organization_id', 'user_id', 'role', 'invited_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


permissions_auto_config = {'model_pascal': 'Permissions', 'model_name': 'permissions', 'model_name_plural': 'permission', 'model_name_snake': 'permissions', 'relations': ['organizations'], 'filter_fields': ['resource_type', 'granted_to_user_id', 'granted_to_organization_id', 'permission_level', 'created_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


project_members_auto_config = {'model_pascal': 'ProjectMembers', 'model_name': 'project_members', 'model_name_plural': 'project_member', 'model_name_snake': 'project_members', 'relations': ['projects'], 'filter_fields': ['project_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_broker_auto_config = {'model_pascal': 'RecipeBroker', 'model_name': 'recipe_broker', 'model_name_plural': 'recipe_brokers', 'model_name_snake': 'recipe_broker', 'relations': ['broker', 'recipe'], 'filter_fields': ['recipe', 'broker', 'broker_role'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_display_auto_config = {'model_pascal': 'RecipeDisplay', 'model_name': 'recipe_display', 'model_name_plural': 'recipe_displays', 'model_name_snake': 'recipe_display', 'relations': ['display_option', 'recipe'], 'filter_fields': ['recipe', 'display'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_function_auto_config = {'model_pascal': 'RecipeFunction', 'model_name': 'recipe_function', 'model_name_plural': 'recipe_functions', 'model_name_snake': 'recipe_function', 'relations': ['system_function', 'recipe'], 'filter_fields': ['recipe', 'function', 'role'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_message_auto_config = {'model_pascal': 'RecipeMessage', 'model_name': 'recipe_message', 'model_name_plural': 'recipe_messages', 'model_name_snake': 'recipe_message', 'relations': ['message_template', 'recipe'], 'filter_fields': ['message_id', 'recipe_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_message_reorder_queue_auto_config = {'model_pascal': 'RecipeMessageReorderQueue', 'model_name': 'recipe_message_reorder_queue', 'model_name_plural': 'recipe_message_reorder_queues', 'model_name_snake': 'recipe_message_reorder_queue', 'relations': [], 'filter_fields': [], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_model_auto_config = {'model_pascal': 'RecipeModel', 'model_name': 'recipe_model', 'model_name_plural': 'recipe_models', 'model_name_snake': 'recipe_model', 'relations': ['ai_model', 'recipe'], 'filter_fields': ['recipe', 'ai_model', 'role'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_processor_auto_config = {'model_pascal': 'RecipeProcessor', 'model_name': 'recipe_processor', 'model_name_plural': 'recipe_processors', 'model_name_snake': 'recipe_processor', 'relations': ['processor', 'recipe'], 'filter_fields': ['recipe', 'processor'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


recipe_tool_auto_config = {'model_pascal': 'RecipeTool', 'model_name': 'recipe_tool', 'model_name_plural': 'recipe_tools', 'model_name_snake': 'recipe_tool', 'relations': ['recipe', 'tool'], 'filter_fields': ['recipe', 'tool'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_domain_disallowed_notes_auto_config = {'model_pascal': 'ScrapeDomainDisallowedNotes', 'model_name': 'scrape_domain_disallowed_notes', 'model_name_plural': 'scrape_domain_disallowed_note', 'model_name_snake': 'scrape_domain_disallowed_notes', 'relations': ['scrape_domain'], 'filter_fields': ['scrape_domain_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_domain_notes_auto_config = {'model_pascal': 'ScrapeDomainNotes', 'model_name': 'scrape_domain_notes', 'model_name_plural': 'scrape_domain_note', 'model_name_snake': 'scrape_domain_notes', 'relations': ['scrape_domain'], 'filter_fields': ['scrape_domain_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_domain_quick_scrape_settings_auto_config = {'model_pascal': 'ScrapeDomainQuickScrapeSettings', 'model_name': 'scrape_domain_quick_scrape_settings', 'model_name_plural': 'scrape_domain_quick_scrape_setting', 'model_name_snake': 'scrape_domain_quick_scrape_settings', 'relations': ['scrape_domain'], 'filter_fields': ['scrape_domain_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_domain_robots_txt_auto_config = {'model_pascal': 'ScrapeDomainRobotsTxt', 'model_name': 'scrape_domain_robots_txt', 'model_name_plural': 'scrape_domain_robots_txts', 'model_name_snake': 'scrape_domain_robots_txt', 'relations': ['scrape_domain'], 'filter_fields': ['scrape_domain_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_domain_sitemap_auto_config = {'model_pascal': 'ScrapeDomainSitemap', 'model_name': 'scrape_domain_sitemap', 'model_name_plural': 'scrape_domain_sitemaps', 'model_name_snake': 'scrape_domain_sitemap', 'relations': ['scrape_domain'], 'filter_fields': ['scrape_domain_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_override_value_auto_config = {'model_pascal': 'ScrapeOverrideValue', 'model_name': 'scrape_override_value', 'model_name_plural': 'scrape_override_values', 'model_name_snake': 'scrape_override_value', 'relations': ['scrape_override'], 'filter_fields': ['scrape_override_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_parsed_page_auto_config = {'model_pascal': 'ScrapeParsedPage', 'model_name': 'scrape_parsed_page', 'model_name_plural': 'scrape_parsed_pages', 'model_name_snake': 'scrape_parsed_page', 'relations': ['scrape_configuration', 'scrape_cycle_run', 'scrape_cycle_tracker', 'scrape_path_pattern_cache_policy', 'scrape_path_pattern_override', 'scrape_task', 'scrape_task_response'], 'filter_fields': ['scrape_path_pattern_cache_policy_id', 'scrape_task_id', 'scrape_task_response_id', 'scrape_cycle_run_id', 'scrape_cycle_tracker_id', 'scrape_configuration_id', 'scrape_path_pattern_override_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


scrape_quick_failure_log_auto_config = {'model_pascal': 'ScrapeQuickFailureLog', 'model_name': 'scrape_quick_failure_log', 'model_name_plural': 'scrape_quick_failure_logs', 'model_name_snake': 'scrape_quick_failure_log', 'relations': ['scrape_domain'], 'filter_fields': ['scrape_domain_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


task_assignments_auto_config = {'model_pascal': 'TaskAssignments', 'model_name': 'task_assignments', 'model_name_plural': 'task_assignment', 'model_name_snake': 'task_assignments', 'relations': ['tasks'], 'filter_fields': ['task_id', 'user_id', 'assigned_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


task_attachments_auto_config = {'model_pascal': 'TaskAttachments', 'model_name': 'task_attachments', 'model_name_plural': 'task_attachment', 'model_name_snake': 'task_attachments', 'relations': ['tasks'], 'filter_fields': ['task_id', 'uploaded_by'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


task_comments_auto_config = {'model_pascal': 'TaskComments', 'model_name': 'task_comments', 'model_name_plural': 'task_comment', 'model_name_snake': 'task_comments', 'relations': ['tasks'], 'filter_fields': ['task_id', 'user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


user_preferences_auto_config = {'model_pascal': 'UserPreferences', 'model_name': 'user_preferences', 'model_name_plural': 'user_preference', 'model_name_snake': 'user_preferences', 'relations': [], 'filter_fields': ['user_id'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}


wc_injury_auto_config = {'model_pascal': 'WcInjury', 'model_name': 'wc_injury', 'model_name_plural': 'wc_injuries', 'model_name_snake': 'wc_injury', 'relations': ['wc_impairment_definition', 'wc_report'], 'filter_fields': ['report_id', 'impairment_definition_id', 'side'], 'include_core_relations': True, 'include_active_relations': False, 'include_filter_fields': True, 'include_active_methods': False, 'include_or_not_methods': False, 'include_to_dict_methods': False, 'include_to_dict_relations': False}