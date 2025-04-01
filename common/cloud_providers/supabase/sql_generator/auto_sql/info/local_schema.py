from common import pretty_print

db_schema = {
    "tables": [
        {
            "table_name": "recipe_display",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "display",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "priority",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": "'1'::smallint",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "display_settings",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_display_display_fkey",
                    "local_referencing_column": "display",
                    "referenced_table": "display_option",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_display_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "arg",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "text",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "required",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "True",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "data_type",
                    "data_type": "data_type",
                    "options": [
                        "str",
                        "int",
                        "float",
                        "bool",
                        "dict",
                        "list",
                        "url"
                    ],
                    "is_required": False,
                    "default_value": "'str'::data_type",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "ready",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "False",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "registered_function",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "args_registered_function_fkey",
                    "local_referencing_column": "registered_function",
                    "referenced_table": "registered_function",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "system_function",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "public_name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "sample",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "input_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "output_options",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "rf_id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "recipe_function_function_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_function",
                    "referencing_column": "function"
                },
                {
                    "constraint_name": "tool_system_function_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "tool",
                    "referencing_column": "system_function"
                }
            ],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "system_function_function_fkey",
                    "local_referencing_column": "rf_id",
                    "referenced_table": "registered_function",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "automation_boundary_brokers",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "matrix",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "broker",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "spark_source",
                    "data_type": "data_source",
                    "options": [
                        "user_input",
                        "database",
                        "api",
                        "environment",
                        "file",
                        "chance",
                        "generated_data",
                        "function",
                        "none"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "beacon_destination",
                    "data_type": "data_destination",
                    "options": [
                        "user_output",
                        "database",
                        "file",
                        "api_response",
                        "function"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "boundary_brokers_broker_fkey",
                    "local_referencing_column": "broker",
                    "referenced_table": "broker",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "boundary_brokers_matrix_fkey",
                    "local_referencing_column": "matrix",
                    "referenced_table": "automation_matrix",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "registered_function",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "module_path",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "class_name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "return_broker",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "args_registered_function_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "arg",
                    "referencing_column": "registered_function"
                },
                {
                    "constraint_name": "system_function_function_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "system_function",
                    "referencing_column": "rf_id"
                }
            ],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "registered_function_return_broker_fkey",
                    "local_referencing_column": "return_broker",
                    "referenced_table": "broker",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "recipe_function",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "function",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "role",
                    "data_type": "function_role",
                    "options": [
                        "decision",
                        "validation",
                        "post_processing",
                        "pre-Processing",
                        "rating",
                        "comparison",
                        "save_data",
                        "other"
                    ],
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_function_function_fkey",
                    "local_referencing_column": "function",
                    "referenced_table": "system_function",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_function_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "tool",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "source",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": True,
                    "default_value": "'{\"host\": \"ame\"}'::jsonb",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "parameters",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "required_args",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "system_function",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "additional_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "recipe_tools_tool_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_tools",
                    "referencing_column": "tool"
                }
            ],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "tool_system_function_fkey",
                    "local_referencing_column": "system_function",
                    "referenced_table": "system_function",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "transformers",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "input_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "ourput_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "action_transformer_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "action",
                    "referencing_column": "transformer"
                }
            ],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "ai_endpoint",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "provider",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "additional_cost",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "True",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "cost_details",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "params",
                    "data_type": "json",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "recipe_broker",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "broker",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "broker_role",
                    "data_type": "broker_role",
                    "options": [
                        "input_broker",
                        "output_broker"
                    ],
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "required",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "True",
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_broker_broker_fkey",
                    "local_referencing_column": "broker",
                    "referenced_table": "broker",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_broker_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "recipe_processors",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "processor",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_processors_processor_fkey",
                    "local_referencing_column": "processor",
                    "referenced_table": "processors",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_processors_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "action",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "matrix",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "transformer",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "node_type",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "reference_id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "action_matrix_fkey",
                    "local_referencing_column": "matrix",
                    "referenced_table": "automation_matrix",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "action_transformer_fkey",
                    "local_referencing_column": "transformer",
                    "referenced_table": "transformers",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "ai_model",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "common_name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "class",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "provider",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "endpoints",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "context_window",
                    "data_type": "bigint",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "max_tokens",
                    "data_type": "bigint",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "capabilities",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "controls",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "recipe_model_ai_model_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_model",
                    "referencing_column": "ai_model"
                }
            ],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "data_input_component",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "options",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "include_other",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "min",
                    "data_type": "real",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "max",
                    "data_type": "real",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "step",
                    "data_type": "integer",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "min_rows",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "max_rows",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "acceptable_filetypes",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "src",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "classes",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "color_overrides",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "additional_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "broker_custom_component_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "broker",
                    "referencing_column": "custom_source_component"
                }
            ],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "data_output_component",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "component_type",
                    "data_type": "destination_component",
                    "options": [
                        "chatResponse",
                        "PlainText",
                        "Textarea",
                        "JsonViewer",
                        "CodeView",
                        "MarkdownViewer",
                        "RichTextEditor",
                        "TreeView",
                        "ImageView",
                        "AudioOutput",
                        "Presentation",
                        "RunCodeFront",
                        "RunCodeBack",
                        "ComplexMulti",
                        "FileOutput",
                        "Table",
                        "Form",
                        "VerticalList",
                        "HorizontalList",
                        "Flowchart",
                        "WordMap",
                        "GeographicMap",
                        "video",
                        "Spreadsheet",
                        "Timeline",
                        "GanttChart",
                        "NetworkGraph",
                        "Heatmap",
                        "3DModelViewer",
                        "LaTeXRenderer",
                        "DiffViewer",
                        "Checklist",
                        "KanbanBoard",
                        "PivotTable",
                        "InteractiveChart",
                        "SankeyDiagram",
                        "MindMap",
                        "Calendar",
                        "Carousel",
                        "PDFViewer",
                        "SVGEditor",
                        "DataFlowDiagram",
                        "UMLDiagram",
                        "GlossaryView",
                        "DecisionTree",
                        "WordHighlighter",
                        "SpectrumAnalyzer",
                        "LiveTraffic",
                        "WeatherMap",
                        "WeatherDashboard",
                        "Thermometer",
                        "SatelliteView",
                        "PublicLiveCam",
                        "Clock",
                        "BudgetVisualizer",
                        "MealPlanner",
                        "TaskPrioritization",
                        "VoiceSentimentAnalysis",
                        "NewsAggregator",
                        "FitnessTracker",
                        "TravelPlanner",
                        "BucketList",
                        "SocialMediaInfo",
                        "LocalEvents",
                        "NeedNewOption",
                        "none"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "ui_component",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "props",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "additional_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "processors",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "depends_default",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "default_extractors",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "recipe_processors_processor_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_processors",
                    "referencing_column": "processor"
                },
                {
                    "constraint_name": "processors_depends_default_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "processors",
                    "referencing_column": "depends_default"
                }
            ],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "processors_depends_default_fkey",
                    "local_referencing_column": "depends_default",
                    "referenced_table": "processors",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "recipe_model",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "ai_model",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "role",
                    "data_type": "model_role",
                    "options": [
                        "primary_model",
                        "verified_model",
                        "trial_model"
                    ],
                    "is_required": True,
                    "default_value": "'primary_model'::model_role",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "priority",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": "'1'::smallint",
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_model_ai_model_fkey",
                    "local_referencing_column": "ai_model",
                    "referenced_table": "ai_model",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_model_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "broker",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "value",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "data_type",
                    "data_type": "data_type",
                    "options": [
                        "str",
                        "int",
                        "float",
                        "bool",
                        "dict",
                        "list",
                        "url"
                    ],
                    "is_required": True,
                    "default_value": "'str'::data_type",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "ready",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "False",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default_source",
                    "data_type": "data_source",
                    "options": [
                        "user_input",
                        "database",
                        "api",
                        "environment",
                        "file",
                        "chance",
                        "generated_data",
                        "function",
                        "none"
                    ],
                    "is_required": False,
                    "default_value": "'none'::data_source",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "display_name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "tooltip",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "validation_rules",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "sample_entries",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "custom_source_component",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "additional_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "other_source_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default_destination",
                    "data_type": "data_destination",
                    "options": [
                        "user_output",
                        "database",
                        "file",
                        "api_response",
                        "function"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "output_component",
                    "data_type": "destination_component",
                    "options": [
                        "chatResponse",
                        "PlainText",
                        "Textarea",
                        "JsonViewer",
                        "CodeView",
                        "MarkdownViewer",
                        "RichTextEditor",
                        "TreeView",
                        "ImageView",
                        "AudioOutput",
                        "Presentation",
                        "RunCodeFront",
                        "RunCodeBack",
                        "ComplexMulti",
                        "FileOutput",
                        "Table",
                        "Form",
                        "VerticalList",
                        "HorizontalList",
                        "Flowchart",
                        "WordMap",
                        "GeographicMap",
                        "video",
                        "Spreadsheet",
                        "Timeline",
                        "GanttChart",
                        "NetworkGraph",
                        "Heatmap",
                        "3DModelViewer",
                        "LaTeXRenderer",
                        "DiffViewer",
                        "Checklist",
                        "KanbanBoard",
                        "PivotTable",
                        "InteractiveChart",
                        "SankeyDiagram",
                        "MindMap",
                        "Calendar",
                        "Carousel",
                        "PDFViewer",
                        "SVGEditor",
                        "DataFlowDiagram",
                        "UMLDiagram",
                        "GlossaryView",
                        "DecisionTree",
                        "WordHighlighter",
                        "SpectrumAnalyzer",
                        "LiveTraffic",
                        "WeatherMap",
                        "WeatherDashboard",
                        "Thermometer",
                        "SatelliteView",
                        "PublicLiveCam",
                        "Clock",
                        "BudgetVisualizer",
                        "MealPlanner",
                        "TaskPrioritization",
                        "VoiceSentimentAnalysis",
                        "NewsAggregator",
                        "FitnessTracker",
                        "TravelPlanner",
                        "BucketList",
                        "SocialMediaInfo",
                        "LocalEvents",
                        "NeedNewOption",
                        "none"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "tags",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": "'[]'::jsonb",
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "boundary_brokers_broker_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "automation_boundary_brokers",
                    "referencing_column": "broker"
                },
                {
                    "constraint_name": "registered_function_return_broker_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "registered_function",
                    "referencing_column": "return_broker"
                },
                {
                    "constraint_name": "recipe_broker_broker_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_broker",
                    "referencing_column": "broker"
                }
            ],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "broker_custom_component_fkey",
                    "local_referencing_column": "custom_source_component",
                    "referenced_table": "data_input_component",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "extractor",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "output_type",
                    "data_type": "data_type",
                    "options": [
                        "str",
                        "int",
                        "float",
                        "bool",
                        "dict",
                        "list",
                        "url"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default_identifier",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default_index",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "recipe_tools",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "tool",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_tools_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_tools_tool_fkey",
                    "local_referencing_column": "tool",
                    "referenced_table": "tool",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "display_option",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "customizable_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "additional_params",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "recipe_display_display_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_display",
                    "referencing_column": "display"
                }
            ],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "automation_matrix",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "average_seconds",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "is_automated",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "cognition_matrices",
                    "data_type": "cognition_matrices",
                    "options": [
                        "agent_crew",
                        "agent_mixture",
                        "workflow",
                        "conductor",
                        "monte_carlo",
                        "hypercluster",
                        "the_matrix",
                        "knowledge_matrix"
                    ],
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "boundary_brokers_matrix_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "automation_boundary_brokers",
                    "referencing_column": "matrix"
                },
                {
                    "constraint_name": "action_matrix_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "action",
                    "referencing_column": "matrix"
                }
            ],
            "outbound_foreign_keys": []
        },
        {
            "table_name": "recipe",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "character varying",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "description",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "tags",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "sample_output",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "is_public",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "status",
                    "data_type": "recipe_status",
                    "options": [
                        "live",
                        "draft",
                        "in_review",
                        "active_testing",
                        "archived",
                        "other"
                    ],
                    "is_required": True,
                    "default_value": "'draft'::recipe_status",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "version",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": "'1'::smallint",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "messages",
                    "data_type": "jsonb[]",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "post_result_options",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [
                {
                    "constraint_name": "recipe_display_recipe_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_display",
                    "referencing_column": "recipe"
                },
                {
                    "constraint_name": "recipe_function_recipe_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_function",
                    "referencing_column": "recipe"
                },
                {
                    "constraint_name": "recipe_broker_recipe_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_broker",
                    "referencing_column": "recipe"
                },
                {
                    "constraint_name": "recipe_processors_recipe_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_processors",
                    "referencing_column": "recipe"
                },
                {
                    "constraint_name": "recipe_model_recipe_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_model",
                    "referencing_column": "recipe"
                },
                {
                    "constraint_name": "recipe_tools_recipe_fkey",
                    "local_referenced_column": "id",
                    "referencing_table": "recipe_tools",
                    "referencing_column": "recipe"
                }
            ],
            "outbound_foreign_keys": []
        }
    ]
}

db_schema_small = {
    "tables": [
        {
            "table_name": "recipe_display",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "recipe",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "display",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                },
                {
                    "column_name": "priority",
                    "data_type": "smallint",
                    "options": None,
                    "is_required": False,
                    "default_value": "'1'::smallint",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "display_settings",
                    "data_type": "jsonb",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "recipe_display_display_fkey",
                    "local_referencing_column": "display",
                    "referenced_table": "display_option",
                    "referenced_column": "id"
                },
                {
                    "constraint_name": "recipe_display_recipe_fkey",
                    "local_referencing_column": "recipe",
                    "referenced_table": "recipe",
                    "referenced_column": "id"
                }
            ]
        },
        {
            "table_name": "arg",
            "primary_key": "id",
            "schema": [
                {
                    "column_name": "id",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": True,
                    "default_value": "gen_random_uuid()",
                    "is_primary_key": True,
                    "is_foreign_key": False
                },
                {
                    "column_name": "name",
                    "data_type": "text",
                    "options": None,
                    "is_required": True,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "required",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "True",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "default",
                    "data_type": "text",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "data_type",
                    "data_type": "data_type",
                    "options": [
                        "str",
                        "int",
                        "float",
                        "bool",
                        "dict",
                        "list",
                        "url"
                    ],
                    "is_required": False,
                    "default_value": "'str'::data_type",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "ready",
                    "data_type": "boolean",
                    "options": None,
                    "is_required": False,
                    "default_value": "False",
                    "is_primary_key": None,
                    "is_foreign_key": False
                },
                {
                    "column_name": "registered_function",
                    "data_type": "uuid",
                    "options": None,
                    "is_required": False,
                    "default_value": None,
                    "is_primary_key": None,
                    "is_foreign_key": True
                }
            ],
            "inbound_foreign_keys": [],
            "outbound_foreign_keys": [
                {
                    "constraint_name": "args_registered_function_fkey",
                    "local_referencing_column": "registered_function",
                    "referenced_table": "registered_function",
                    "referenced_column": "id"
                }
            ]
        }
    ]
}


def get_db_schema():
    return db_schema


def get_default_values(schema):
    # Use a set to collect unique default values
    default_values = set()

    # Iterate through each table in the schema
    for table in schema.get("tables", []):
        # Iterate through each column in the table's schema
        for column in table.get("schema", []):
            default_value = column.get("default_value")
            if default_value is not None:
                default_values.add(default_value)

    # Return the unique default values as a list
    return list(default_values)


# Execute the function and print the results
if __name__ == "__main__":
    unique_defaults = get_default_values(db_schema)
    print("Unique Default Values:", unique_defaults)
    pretty_print(unique_defaults)
