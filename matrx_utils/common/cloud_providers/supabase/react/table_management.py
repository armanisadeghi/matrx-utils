from typing import List, Dict, Any
from common.supabase.react.column_management import Column

class Table:
    def __init__(
            self,
            table_name: str,
            columns: List[Dict[str, Any]],
            inbound_foreign_keys: List[Dict[str, Any]] = None,
            outbound_foreign_keys: List[Dict[str, Any]] = None,
            type_mappings: Dict[str, str] = None
    ):

        # Basic properties
        self.original_name = table_name
        self.name = Column.to_camel_case(table_name)
        self.columns = [Column(**col, type_mappings=type_mappings) for col in columns]
        self.inbound_foreign_keys = inbound_foreign_keys or []
        self.outbound_foreign_keys = outbound_foreign_keys or []

        # Derived properties
        self.snake_case_name = table_name.lower()
        self.camel_case_name = self.name
        self.type_name = self.get_type_name()

        # Placeholder for properties that depend on foreign keys
        self.imports = []
        self.ts_type_declaration = ""
        self.ts_imports_code = ""
        self.child_entity_list_names = {}
        self.parent_entity_names = {}

        # Other properties
        self.entity_list_name = f"{self.camel_case_name}List"
        self.redux_select_all_name = f"selectAll{self.type_name}"
        self.sql_table_name = self.snake_case_name
        self.js_var_name = self.camel_case_name
        self.ts_type_name = self.type_name
        self.python_var_name = self.snake_case_name
        self.api_endpoint_name = f"/api/{self.snake_case_name}"
        self.graphql_type_name = self.type_name
        self.form_component_name = f"{self.type_name}Form"
        self.table_component_name = f"{self.type_name}Table"
        self.selector_hook_name = f"use{self.type_name}Selector"
        self.dispatch_hook_name = f"use{self.type_name}Dispatch"
        self.service_class_name = f"{self.type_name}Service"
        self.test_suite_name = f"Test{self.type_name}"

    def initialize(self):
        """Initialize properties that depend on foreign keys."""
        self.imports = self.get_imports()
        self.ts_type_declaration = self.get_ts_type_declaration()
        self.ts_imports_code = "\n".join(self.imports)
        self.child_entity_list_names = self.get_child_entity_list_names()
        self.parent_entity_names = self.get_parent_entity_names()

        # This probably needs to have a separate method (But we need to wait to see how many we have total) - We will have more than just redux.
        self.redux_import_statements = self.get_imports()

    def add_inbound_foreign_key(self, fk: Dict):
        if 'referencing_table' not in fk:
            print(f"Warning: Missing 'referencing_table' key in inbound foreign key for table '{self.original_name}'.")
            print(f"Foreign key data: {fk}")
        self.inbound_foreign_keys.append(fk)

    def add_outbound_foreign_key(self, fk: Dict):
        if 'referenced_table' not in fk:
            print(f"Warning: Missing 'referenced_table' key in outbound foreign key for table '{self.original_name}'.")
            print(f"Foreign key data: {fk}")
        self.outbound_foreign_keys.append(fk)

    @staticmethod
    def to_camel_case(snake_str: str) -> str:
        components = snake_str.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    def get_type_name(self) -> str:
        """Calculate the TypeScript type name for this table."""
        return self.name[0].upper() + self.name[1:]

    def get_imports(self) -> List[str]:
        """Generate the necessary import statements for this table."""
        imports = []
        for fk in self.inbound_foreign_keys:
            referenced_table = fk["referenced_table"]
            referenced_table_name = Column.to_camel_case(referenced_table)
            upper_referenced_table_name = Column.to_upper_camel_case(referenced_table)
            imports.append(
                f"import {{{upper_referenced_table_name}}} from './{referenced_table_name}Type';"
            )
        return imports

    def get_ts_type_declaration(self) -> str:
        """Generate TypeScript type declaration for the table."""
        lines = [f"export type {self.type_name} = {{"]

        # Add TypeScript property definitions for columns
        lines.extend([col.ts_property_definition for col in self.columns])

        # Add TypeScript definitions for foreign keys
        if self.inbound_foreign_keys:
            for fk in self.inbound_foreign_keys:
                referenced_table = fk["referenced_table"]
                referenced_table_name = Column.to_camel_case(referenced_table)
                fk_field_name = Column.to_camel_case(referenced_table)
                lines.append(
                    f"    {fk_field_name}?: {referenced_table_name[0].upper() + referenced_table_name[1:]}[];"
                )

        lines.append("};")
        return "\n".join(lines)

    def get_child_entity_list_names(self) -> Dict[str, str]:
        """Get a dictionary of child entity list names if inbound foreign keys exist."""
        if not self.inbound_foreign_keys:
            return {}
        return {
            fk['referenced_table']: f"{Column.to_camel_case(fk['referenced_table'])}List"
            for fk in self.inbound_foreign_keys
        }

    def get_parent_entity_names(self) -> Dict[str, str]:
        """Get a dictionary of parent entity names if outbound foreign keys exist."""
        if not self.outbound_foreign_keys:
            return {}
        return {
            fk['referencing_table']: Column.to_camel_case(fk['referencing_table'])
            for fk in self.outbound_foreign_keys
        }


from typing import List, Dict, Any

from common.supabase.react.column_management import Column


class Table:
    def __init__(
            self,
            table_name: str,
            columns: List[Dict[str, Any]],
            inbound_foreign_keys: List[Dict[str, Any]] = None,
            outbound_foreign_keys: List[Dict[str, Any]] = None,
            type_mappings: Dict[str, str] = None
    ):
        # Backward-compatible properties
        self.name = Column.to_camel_case(table_name)
        self.columns = [Column(**col, type_mappings=type_mappings) for col in columns]
        self.inbound_foreign_keys = inbound_foreign_keys or []
        self.outbound_foreign_keys = outbound_foreign_keys or []

        # Forgotten
        self.type_name = self.get_type_name()
        self.imports = self.get_imports()

        # Additional properties for various use cases
        self.original_name = table_name  # Original table name
        self.camel_case_name = self.name  # Camel case version
        self.type_name = self.get_type_name()  # Pascal case
        self.snake_case_name = table_name.lower()  # Snake case
        self.entity_list_name = f"{self.camel_case_name}List"  # Entity list name

        # Redux and Selector Names
        self.redux_select_all_name = f"selectAll{self.type_name}"
        self.redux_import_statements = self.get_imports()

        # SQL, JavaScript, TypeScript, Python Use Cases
        self.sql_table_name = self.snake_case_name  # SQL compatible name
        self.js_var_name = self.camel_case_name  # JavaScript variable name
        self.ts_type_name = self.type_name  # TypeScript type name
        self.python_var_name = self.snake_case_name  # Python variable name

        # TypeScript Type Declaration
        self.ts_type_declaration = self.get_ts_type_declaration()
        self.ts_imports_code = "\n".join(self.imports)

        # Additional Use Cases and Roles
        self.api_endpoint_name = f"/api/{self.snake_case_name}"  # API endpoint path
        self.graphql_type_name = self.type_name  # GraphQL type name
        self.form_component_name = f"{self.type_name}Form"  # React form component name
        self.table_component_name = f"{self.type_name}Table"  # React table component name
        self.selector_hook_name = f"use{self.type_name}Selector"  # React Redux hook name
        self.dispatch_hook_name = f"use{self.type_name}Dispatch"  # React Redux dispatch hook name
        self.service_class_name = f"{self.type_name}Service"  # Service class name for business logic
        self.test_suite_name = f"Test{self.type_name}"  # Test suite class name

        # Encapsulated logic for child and parent entities
        self.child_entity_list_names = self.get_child_entity_list_names()
        self.parent_entity_names = self.get_parent_entity_names()

