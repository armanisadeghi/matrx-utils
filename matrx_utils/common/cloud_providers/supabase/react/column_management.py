from typing import List, Dict, Any


class Column:
    def __init__(
        self,
        column_name: str,
        data_type: str,
        options: List[str] = None,
        is_primary_key: bool = False,
        is_required: bool = True,
        default_value: Any = None,
        is_foreign_key: bool = False,
        type_mappings: Dict[str, str] = None
    ):
        # Backward-compatible properties
        self.name = Column.to_camel_case(column_name)
        self.data_type = data_type
        self.is_primary_key = is_primary_key
        self.is_required = is_required
        self.default_value = self.parse_default_value(default_value)
        self.is_foreign_key = is_foreign_key
        self.options = options or []

        # Additional properties for various use cases
        self.original_name = column_name  # Original column name
        self.camel_case_name = self.name  # Camel case version
        self.upper_camel_case_name = Column.to_upper_camel_case(column_name)  # Pascal case
        self.snake_case_name = column_name.lower()  # Snake case

        # Redux and Selector Names
        self.redux_selector_name = f"selectAll{self.upper_camel_case_name}"
        self.redux_action_names = {
            "add": f"add{self.upper_camel_case_name}",
            "update": f"update{self.upper_camel_case_name}",
            "delete": f"delete{self.upper_camel_case_name}",
        }

        # SQL, JavaScript, TypeScript, Python Use Cases
        self.sql_column_name = self.snake_case_name  # SQL compatible name
        self.js_var_name = self.camel_case_name  # JavaScript variable name
        self.ts_type_name = self.upper_camel_case_name  # TypeScript type name
        self.python_var_name = self.snake_case_name  # Python variable name

        # TypeScript Type Mapping
        self.ts_type = self.get_typescript_type(type_mappings)
        self.ts_property_definition = f"{self.camel_case_name}: {self.ts_type};"


        # Additional Use Cases and Roles
        self.api_param_name = self.camel_case_name  # API parameter name
        self.api_response_key = self.camel_case_name  # API response key
        self.graphql_field_name = self.camel_case_name  # GraphQL field name
        self.form_input_name = self.camel_case_name  # HTML form input name
        self.component_prop_name = self.camel_case_name  # React component prop name
        self.test_var_name = f"mock_{self.snake_case_name}"  # Variable name for testing
        self.config_option_name = f"config_{self.snake_case_name}"  # Config file option name

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def to_upper_camel_case(snake_str: str) -> str:
        components = snake_str.split('_')
        return ''.join(x.title() for x in components)

    @staticmethod
    def parse_default_value(value: Any) -> Any:
        default_mappings = {
            "'draft'::recipe_status": '"draft"',
            'gen_random_uuid()': None,
            'True': 'true',
            'False': 'false',
            "'none'::data_source": '"none"',
            '\'{"host": "ame"}\'::jsonb': '{"host": "ame"}',
            "'1'::smallint": '1',
            "'str'::data_type": '"str"',
            "'primary_model'::model_role": '"primary_model"',
            "'[]'::jsonb": '[]'
        }
        return default_mappings.get(value, value)

    def get_typescript_type(self, type_mappings: Dict[str, str]) -> str:
        """Determine TypeScript type based on column naming conventions."""
        if not type_mappings:
            return "any"

        if self.original_name == "id" or self.original_name.endswith("Id"):
            return type_mappings.get("id", "string")

        if self.original_name in ["createdAt", "updatedAt"]:
            return type_mappings.get(self.original_name, "Date")

        if self.original_name.startswith("is"):
            return type_mappings.get("startsWithIs", "boolean")

        return type_mappings.get("default", "string")
