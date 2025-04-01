fetch_structure = {
    "table_name": "table_name_here",
    "primary_key": "primary_key_column_name",
    "schema": [
        {
            "column_name": "column_name_here",
            "data_type": "data_type_here",
            "options": None,
            "is_required": False,
            "default_value": None,
            "is_primary_key": False,
            "is_foreign_key": False
        }
    ],
    "inbound_foreign_keys": [
        {
            "constraint_name": "inbound_constraint_name_here",
            "foreign_key_column": "column_name_here",
            "referenced_table": "referenced_table_name_here",
            "referenced_column": "referenced_column_name_here"
        }
    ],
    "outbound_foreign_keys": [
        {
            "constraint_name": "outbound_constraint_name_here",
            "foreign_key_column": "column_name_here",
            "referenced_table": "referenced_table_name_here",
            "referenced_column": "referenced_column_name_here"
        }
    ]
}

direct_structure = {
    "table_name": "table_name_here",
    "primary_key": {
        "table_schema": "public",
        "table_name": "recipe",
        "column_name": "id"
    },
    "columns": [
        {
            "column_name": "status",
            "data_type": "USER-DEFINED",
            "is_nullable": "NO",
            "column_default": "'draft'::recipe_status",
            "udt_name": "recipe_status",
            "options": ["live", "draft", "in_review", "active_testing", "archived", "other"],
        },
    ],
    "foreign_keys": [
        {
            "table_schema": "public",
            "constraint_name": "recipe_broker_broker_fkey",
            "table_name": "recipe_broker",
            "column_name": "broker",
            "foreign_table_schema": "public",
            "foreign_table_name": "broker",
            "foreign_column_name": "id"
        },
    ],
    "indexes": [
        {
            "schema_name": "schema_name_here",
            "table_name": "table_name_here",
            "index_name": "index_name_here",
            "index_definition": "index_definition_here"
        }
    ]
}
