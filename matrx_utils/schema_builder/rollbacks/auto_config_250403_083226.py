"""

# matrx_utils\schema_builder\rollbacks\auto_config_250403_083226.py


recipe_auto_config = {
    "model_pascal": "Recipe",
    "model_name": "recipe",
    "model_name_plural": "recipes",
    "relations": [
        "compiled_recipe",
        "ai_agent",
        "recipe_display",
        "recipe_processor",
        "recipe_model",
        "recipe_broker",
        "recipe_message",
        "recipe_tool",
        "recipe_function",
    ],
    "filter_fields": ["status"],
    "include_to_dict": False,
    "include_active_methods": False,
}


ai_provider_auto_config = {
    "model_pascal": "AiProvider",
    "model_name": "ai_provider",
    "model_name_plural": "ai_providers",
    "relations": ["ai_settings", "ai_model"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


data_input_component_auto_config = {
    "model_pascal": "DataInputComponent",
    "model_name": "data_input_component",
    "model_name_plural": "data_input_components",
    "relations": ["message_broker", "broker", "data_broker"],
    "filter_fields": [
        "options",
        "component",
        "size",
        "height",
        "width",
        "min_height",
        "max_height",
        "min_width",
        "max_width",
        "orientation",
    ],
    "include_to_dict": False,
    "include_active_methods": False,
}


ai_model_auto_config = {
    "model_pascal": "AiModel",
    "model_name": "ai_model",
    "model_name_plural": "ai_models",
    "relations": ["ai_provider", "ai_model_endpoint", "ai_settings", "recipe_model"],
    "filter_fields": ["model_provider"],
    "include_to_dict": False,
    "include_active_methods": False,
}


broker_auto_config = {
    "model_pascal": "Broker",
    "model_name": "broker",
    "model_name_plural": "brokers",
    "relations": ["data_input_component", "recipe_broker", "registered_function", "automation_boundary_broker"],
    "filter_fields": ["data_type", "default_source", "custom_source_component", "default_destination", "output_component"],
    "include_to_dict": False,
    "include_active_methods": False,
}


data_output_component_auto_config = {
    "model_pascal": "DataOutputComponent",
    "model_name": "data_output_component",
    "model_name_plural": "data_output_components",
    "relations": ["data_broker"],
    "filter_fields": ["component_type"],
    "include_to_dict": False,
    "include_active_methods": False,
}


flashcard_data_auto_config = {
    "model_pascal": "FlashcardData",
    "model_name": "flashcard_data",
    "model_name_plural": "flashcard_datas",
    "relations": ["flashcard_history", "flashcard_set_relations", "flashcard_images"],
    "filter_fields": ["user_id", "shared_with"],
    "include_to_dict": False,
    "include_active_methods": False,
}


projects_auto_config = {
    "model_pascal": "Projects",
    "model_name": "projects",
    "model_name_plural": "project",
    "relations": ["project_members", "tasks"],
    "filter_fields": ["created_by"],
    "include_to_dict": False,
    "include_active_methods": False,
}


tasks_auto_config = {
    "model_pascal": "Tasks",
    "model_name": "tasks",
    "model_name_plural": "task",
    "relations": ["projects", "task_assignments", "task_attachments", "task_comments"],
    "filter_fields": ["project_id", "created_by"],
    "include_to_dict": False,
    "include_active_methods": False,
}


ai_endpoint_auto_config = {
    "model_pascal": "AiEndpoint",
    "model_name": "ai_endpoint",
    "model_name_plural": "ai_endpoints",
    "relations": ["ai_model_endpoint", "ai_settings"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


automation_matrix_auto_config = {
    "model_pascal": "AutomationMatrix",
    "model_name": "automation_matrix",
    "model_name_plural": "automation_matrixes",
    "relations": ["action", "automation_boundary_broker"],
    "filter_fields": ["cognition_matrices"],
    "include_to_dict": False,
    "include_active_methods": False,
}


data_broker_auto_config = {
    "model_pascal": "DataBroker",
    "model_name": "data_broker",
    "model_name_plural": "data_brokers",
    "relations": ["data_input_component", "data_output_component", "broker_value", "message_broker"],
    "filter_fields": ["data_type", "input_component", "color", "output_component"],
    "include_to_dict": False,
    "include_active_methods": False,
}


message_template_auto_config = {
    "model_pascal": "MessageTemplate",
    "model_name": "message_template",
    "model_name_plural": "message_templates",
    "relations": ["message_broker", "recipe_message"],
    "filter_fields": ["role", "type"],
    "include_to_dict": False,
    "include_active_methods": False,
}


registered_function_auto_config = {
    "model_pascal": "RegisteredFunction",
    "model_name": "registered_function",
    "model_name_plural": "registered_functions",
    "relations": ["broker", "system_function", "arg"],
    "filter_fields": ["return_broker"],
    "include_to_dict": False,
    "include_active_methods": False,
}


system_function_auto_config = {
    "model_pascal": "SystemFunction",
    "model_name": "system_function",
    "model_name_plural": "system_functions",
    "relations": ["registered_function", "tool", "recipe_function"],
    "filter_fields": ["rf_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


ai_settings_auto_config = {
    "model_pascal": "AiSettings",
    "model_name": "ai_settings",
    "model_name_plural": "ai_setting",
    "relations": ["ai_endpoint", "ai_model", "ai_provider", "ai_agent"],
    "filter_fields": ["ai_endpoint", "ai_provider", "ai_model"],
    "include_to_dict": False,
    "include_active_methods": False,
}


audio_label_auto_config = {
    "model_pascal": "AudioLabel",
    "model_name": "audio_label",
    "model_name_plural": "audio_labels",
    "relations": ["audio_recording"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


category_auto_config = {
    "model_pascal": "Category",
    "model_name": "category",
    "model_name_plural": "categories",
    "relations": ["subcategory"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


compiled_recipe_auto_config = {
    "model_pascal": "CompiledRecipe",
    "model_name": "compiled_recipe",
    "model_name_plural": "compiled_recipes",
    "relations": ["recipe", "applet"],
    "filter_fields": ["recipe_id", "user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


conversation_auto_config = {
    "model_pascal": "Conversation",
    "model_name": "conversation",
    "model_name_plural": "conversations",
    "relations": ["message"],
    "filter_fields": ["user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


display_option_auto_config = {
    "model_pascal": "DisplayOption",
    "model_name": "display_option",
    "model_name_plural": "display_options",
    "relations": ["recipe_display"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


flashcard_sets_auto_config = {
    "model_pascal": "FlashcardSets",
    "model_name": "flashcard_sets",
    "model_name_plural": "flashcard_set",
    "relations": ["flashcard_set_relations"],
    "filter_fields": ["user_id", "shared_with"],
    "include_to_dict": False,
    "include_active_methods": False,
}


processor_auto_config = {
    "model_pascal": "Processor",
    "model_name": "processor",
    "model_name_plural": "processors",
    "relations": ["self_reference", "recipe_processor"],
    "filter_fields": ["depends_default"],
    "include_to_dict": False,
    "include_active_methods": False,
}


subcategory_auto_config = {
    "model_pascal": "Subcategory",
    "model_name": "subcategory",
    "model_name_plural": "subcategories",
    "relations": ["category", "applet"],
    "filter_fields": ["category_id", "features"],
    "include_to_dict": False,
    "include_active_methods": False,
}


tool_auto_config = {
    "model_pascal": "Tool",
    "model_name": "tool",
    "model_name_plural": "tools",
    "relations": ["system_function", "recipe_tool"],
    "filter_fields": ["system_function"],
    "include_to_dict": False,
    "include_active_methods": False,
}


transformer_auto_config = {
    "model_pascal": "Transformer",
    "model_name": "transformer",
    "model_name_plural": "transformers",
    "relations": ["action"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


wc_claim_auto_config = {
    "model_pascal": "WcClaim",
    "model_name": "wc_claim",
    "model_name_plural": "wc_claims",
    "relations": ["wc_report"],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


wc_impairment_definition_auto_config = {
    "model_pascal": "WcImpairmentDefinition",
    "model_name": "wc_impairment_definition",
    "model_name_plural": "wc_impairment_definitions",
    "relations": ["wc_injury"],
    "filter_fields": ["finger_type"],
    "include_to_dict": False,
    "include_active_methods": False,
}


wc_report_auto_config = {
    "model_pascal": "WcReport",
    "model_name": "wc_report",
    "model_name_plural": "wc_reports",
    "relations": ["wc_claim", "wc_injury"],
    "filter_fields": ["claim_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


action_auto_config = {
    "model_pascal": "Action",
    "model_name": "action",
    "model_name_plural": "actions",
    "relations": ["automation_matrix", "transformer"],
    "filter_fields": ["matrix", "transformer"],
    "include_to_dict": False,
    "include_active_methods": False,
}


ai_agent_auto_config = {
    "model_pascal": "AiAgent",
    "model_name": "ai_agent",
    "model_name_plural": "ai_agents",
    "relations": ["ai_settings", "recipe"],
    "filter_fields": ["recipe_id", "ai_settings_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


ai_model_endpoint_auto_config = {
    "model_pascal": "AiModelEndpoint",
    "model_name": "ai_model_endpoint",
    "model_name_plural": "ai_model_endpoints",
    "relations": ["ai_endpoint", "ai_model"],
    "filter_fields": ["ai_model_id", "ai_endpoint_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


applet_auto_config = {
    "model_pascal": "Applet",
    "model_name": "applet",
    "model_name_plural": "applets",
    "relations": ["compiled_recipe", "subcategory"],
    "filter_fields": ["type", "compiled_recipe_id", "subcategory_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


arg_auto_config = {
    "model_pascal": "Arg",
    "model_name": "arg",
    "model_name_plural": "args",
    "relations": ["registered_function"],
    "filter_fields": ["data_type", "registered_function"],
    "include_to_dict": False,
    "include_active_methods": False,
}


audio_recording_auto_config = {
    "model_pascal": "AudioRecording",
    "model_name": "audio_recording",
    "model_name_plural": "audio_recordings",
    "relations": ["audio_label"],
    "filter_fields": ["user_id", "label"],
    "include_to_dict": False,
    "include_active_methods": False,
}


audio_recording_users_auto_config = {
    "model_pascal": "AudioRecordingUsers",
    "model_name": "audio_recording_users",
    "model_name_plural": "audio_recording_user",
    "relations": [],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


automation_boundary_broker_auto_config = {
    "model_pascal": "AutomationBoundaryBroker",
    "model_name": "automation_boundary_broker",
    "model_name_plural": "automation_boundary_brokers",
    "relations": ["broker", "automation_matrix"],
    "filter_fields": ["matrix", "broker", "spark_source", "beacon_destination"],
    "include_to_dict": False,
    "include_active_methods": False,
}


broker_value_auto_config = {
    "model_pascal": "BrokerValue",
    "model_name": "broker_value",
    "model_name_plural": "broker_values",
    "relations": ["data_broker"],
    "filter_fields": ["user_id", "data_broker", "tags"],
    "include_to_dict": False,
    "include_active_methods": False,
}


bucket_structures_auto_config = {
    "model_pascal": "BucketStructures",
    "model_name": "bucket_structures",
    "model_name_plural": "bucket_structure",
    "relations": [],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


bucket_tree_structures_auto_config = {
    "model_pascal": "BucketTreeStructures",
    "model_name": "bucket_tree_structures",
    "model_name_plural": "bucket_tree_structure",
    "relations": [],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


emails_auto_config = {
    "model_pascal": "Emails",
    "model_name": "emails",
    "model_name_plural": "email",
    "relations": [],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


extractor_auto_config = {
    "model_pascal": "Extractor",
    "model_name": "extractor",
    "model_name_plural": "extractors",
    "relations": [],
    "filter_fields": ["output_type"],
    "include_to_dict": False,
    "include_active_methods": False,
}


file_structure_auto_config = {
    "model_pascal": "FileStructure",
    "model_name": "file_structure",
    "model_name_plural": "file_structures",
    "relations": [],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


flashcard_history_auto_config = {
    "model_pascal": "FlashcardHistory",
    "model_name": "flashcard_history",
    "model_name_plural": "flashcard_histories",
    "relations": ["flashcard_data"],
    "filter_fields": ["flashcard_id", "user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


flashcard_images_auto_config = {
    "model_pascal": "FlashcardImages",
    "model_name": "flashcard_images",
    "model_name_plural": "flashcard_image",
    "relations": ["flashcard_data"],
    "filter_fields": ["flashcard_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


flashcard_set_relations_auto_config = {
    "model_pascal": "FlashcardSetRelations",
    "model_name": "flashcard_set_relations",
    "model_name_plural": "flashcard_set_relation",
    "relations": ["flashcard_data", "flashcard_sets"],
    "filter_fields": ["flashcard_id", "set_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


message_auto_config = {
    "model_pascal": "Message",
    "model_name": "message",
    "model_name_plural": "messages",
    "relations": ["conversation"],
    "filter_fields": ["conversation_id", "role", "type", "user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


message_broker_auto_config = {
    "model_pascal": "MessageBroker",
    "model_name": "message_broker",
    "model_name_plural": "message_brokers",
    "relations": ["data_broker", "data_input_component", "message_template"],
    "filter_fields": ["message_id", "broker_id", "default_component"],
    "include_to_dict": False,
    "include_active_methods": False,
}


project_members_auto_config = {
    "model_pascal": "ProjectMembers",
    "model_name": "project_members",
    "model_name_plural": "project_member",
    "relations": ["projects"],
    "filter_fields": ["project_id", "user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_broker_auto_config = {
    "model_pascal": "RecipeBroker",
    "model_name": "recipe_broker",
    "model_name_plural": "recipe_brokers",
    "relations": ["broker", "recipe"],
    "filter_fields": ["recipe", "broker", "broker_role"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_display_auto_config = {
    "model_pascal": "RecipeDisplay",
    "model_name": "recipe_display",
    "model_name_plural": "recipe_displays",
    "relations": ["display_option", "recipe"],
    "filter_fields": ["recipe", "display"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_function_auto_config = {
    "model_pascal": "RecipeFunction",
    "model_name": "recipe_function",
    "model_name_plural": "recipe_functions",
    "relations": ["system_function", "recipe"],
    "filter_fields": ["recipe", "function", "role"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_message_auto_config = {
    "model_pascal": "RecipeMessage",
    "model_name": "recipe_message",
    "model_name_plural": "recipe_messages",
    "relations": ["message_template", "recipe"],
    "filter_fields": ["message_id", "recipe_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_message_reorder_queue_auto_config = {
    "model_pascal": "RecipeMessageReorderQueue",
    "model_name": "recipe_message_reorder_queue",
    "model_name_plural": "recipe_message_reorder_queues",
    "relations": [],
    "filter_fields": [],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_model_auto_config = {
    "model_pascal": "RecipeModel",
    "model_name": "recipe_model",
    "model_name_plural": "recipe_models",
    "relations": ["ai_model", "recipe"],
    "filter_fields": ["recipe", "ai_model", "role"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_processor_auto_config = {
    "model_pascal": "RecipeProcessor",
    "model_name": "recipe_processor",
    "model_name_plural": "recipe_processors",
    "relations": ["processor", "recipe"],
    "filter_fields": ["recipe", "processor"],
    "include_to_dict": False,
    "include_active_methods": False,
}


recipe_tool_auto_config = {
    "model_pascal": "RecipeTool",
    "model_name": "recipe_tool",
    "model_name_plural": "recipe_tools",
    "relations": ["recipe", "tool"],
    "filter_fields": ["recipe", "tool"],
    "include_to_dict": False,
    "include_active_methods": False,
}


task_assignments_auto_config = {
    "model_pascal": "TaskAssignments",
    "model_name": "task_assignments",
    "model_name_plural": "task_assignment",
    "relations": ["tasks"],
    "filter_fields": ["task_id", "user_id", "assigned_by"],
    "include_to_dict": False,
    "include_active_methods": False,
}


task_attachments_auto_config = {
    "model_pascal": "TaskAttachments",
    "model_name": "task_attachments",
    "model_name_plural": "task_attachment",
    "relations": ["tasks"],
    "filter_fields": ["task_id", "uploaded_by"],
    "include_to_dict": False,
    "include_active_methods": False,
}


task_comments_auto_config = {
    "model_pascal": "TaskComments",
    "model_name": "task_comments",
    "model_name_plural": "task_comment",
    "relations": ["tasks"],
    "filter_fields": ["task_id", "user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


user_preferences_auto_config = {
    "model_pascal": "UserPreferences",
    "model_name": "user_preferences",
    "model_name_plural": "user_preference",
    "relations": [],
    "filter_fields": ["user_id"],
    "include_to_dict": False,
    "include_active_methods": False,
}


wc_injury_auto_config = {
    "model_pascal": "WcInjury",
    "model_name": "wc_injury",
    "model_name_plural": "wc_injuries",
    "relations": ["wc_impairment_definition", "wc_report"],
    "filter_fields": ["report_id", "impairment_definition_id", "side"],
    "include_to_dict": False,
    "include_active_methods": False,
}

"""
