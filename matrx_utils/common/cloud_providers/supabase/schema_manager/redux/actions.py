from common.supabase.schema_manager.technology_base import Technology


class Action(Technology):
    def initialize_technology(self):
        self.action_types = self._generate_action_types()
        self.action_creators = self._generate_action_creators()
        self.file_content = self.generate_action_file()

    def _generate_action_types(self):
        """Generate action types for the table."""
        base_types = {
            'ADD': f'ADD_{self.table.snake_case_name.upper()}',
            'UPDATE': f'UPDATE_{self.table.snake_case_name.upper()}',
            'DELETE': f'DELETE_{self.table.snake_case_name.upper()}',
            'UPSERT': f'UPSERT_{self.table.snake_case_name.upper()}',
        }

        # Add action types for relationships
        for relation in self.table.relations:
            if relation['type'] == 'inbound':
                child_name = relation['referencing_table_snake_case'].upper()
                base_types[f'ADD_{child_name}'] = f'ADD_{child_name}_TO_{self.table.snake_case_name.upper()}'
                base_types[f'REMOVE_{child_name}'] = f'REMOVE_{child_name}_FROM_{self.table.snake_case_name.upper()}'

        return base_types

    def _generate_action_creators(self):
        """Generate action creator names for the table."""
        base_creators = {
            'ADD': f'add{self.table.PascalCaseName}',
            'UPDATE': f'update{self.table.PascalCaseName}',
            'DELETE': f'delete{self.table.PascalCaseName}',
            'UPSERT': f'upsert{self.table.PascalCaseName}',
        }

        # Add action creators for relationships
        for relation in self.table.relations:
            if relation['type'] == 'inbound':
                child_name = relation['referencing_table_pascal_case']
                base_creators[f'ADD_{relation["referencing_table_snake_case"].upper()}'] = f'add{child_name}To{self.table.PascalCaseName}'
                base_creators[f'REMOVE_{relation["referencing_table_snake_case"].upper()}'] = f'remove{child_name}From{self.table.PascalCaseName}'

        return base_creators

    def generate_action_creators(self):
        action_creators = {}
        for action, creator_name in self.action_creators.items():
            # Use the base type key instead of the full name for the lookup
            base_type_key = action.split("_")[0]  # Use the first part of the action type key
            payload_type = f"{self.table.PascalCaseName}" if base_type_key not in ['DELETE', 'REMOVE'] else "string"
            action_creators[creator_name] = f"""
export const {creator_name} = (payload: {payload_type}) => {{
    return {{
        type: '{self.action_types[action]}',
        payload
    }};
}};
"""
        return action_creators

    def generate_action_file(self):
        return f"""{self.file_location_print}

{self.type_import_statement}

// Action Types
{self.generate_action_type_constants()}

// Action Creators
{self.generate_action_creator_functions()}
"""

    def generate_action_type_constants(self):
        return "\n".join([f"export const {name} = '{value}';" for name, value in self.action_types.items()])

    def generate_action_creator_functions(self):
        return "\n".join(self.generate_action_creators().values())
