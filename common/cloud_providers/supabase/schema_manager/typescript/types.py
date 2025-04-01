# common/supabase/schema_manager/redux/types.py
from common import pretty_print
from common.supabase.schema_manager.technology_base import Technology

class TypeScriptType(Technology):
    def initialize_technology(self):
        if self.table.table_name == "recipe":
            print(f"------------------------------------ {self.technology_name} ------------------------------------")
            print(f"Initializing Redux Model for {self.table}")
            print(f"Name: {self.name}")
            print(f"File name: {self.file_name}")
            print(f"Save Directory: {self.save_directory}")
            print(f"Project Directory: {self.project_directory}")
            print(f"Import statement: {self.import_statement}")
            print(f"File location print: {self.file_location_print}")
            print(f"Local save dir: {self.local_save_dir}")
            print(f"Type name: {self.type_name}")
            print(f"Type file name: {self.type_file_name}")
            print(f"Type directory: {self.type_directory}")
            print(f"Type import statement: {self.type_import_statement}")
            print(f"------------------------------------------------------------------------------------------------------")
            for relation in self.table.relations:
                pretty_print(relation)
            print(f"------------------------------------------------------------------------------------------------------")
        self.type_mapping = self.config_manager.type_map
        self.type_definition = self.generate_type_definition()
        self.imports = self.generate_imports()
        self.file_content = self.generate_type_file()
        self.column_types = self.generate_column_types()

    def generate_type_definition(self):
        """Generate the TypeScript type definition."""
        fields = []
        for column in self.table.columns:
            if not column.is_foreign_key:
                if column.options:
                    ts_type = column._create_options_enum()
                else:
                    ts_type = self.type_mapping.get(column.data_type, 'any')
                optional = '' if column.is_required else '?'
                fields.append(f"{column.camelCaseName}{optional}: {ts_type}")

        for relation in self.table.relations:
            ts_property = relation.get('ts_property')
            if ts_property:
                fields.append(ts_property)

        fields_str = '\n    '.join(fields)

        return f"""export type {self.name} = {{
    {fields_str}
}};
"""

    def generate_imports(self):
        """Generate import statements for related models."""
        imports = set()
        for relation in self.table.relations:
            import_statement = relation.get('import_statement')
            if import_statement:
                imports.add(import_statement)

        return '\n'.join(imports)

    def generate_type_file(self):
        """Generate the full content of the type file."""
        return f"""{self.file_location_print}
{self.imports}

{self.type_definition}"""

    def generate_column_types(self):
        """Generate a mapping of column names to their TypeScript types."""
        return {
            column.column_name: column.ts_options if column.options else self.type_mapping.get(column.data_type, 'any')
            for column in self.table.columns
        }
def generate_combined_types_file(tables):
    """Generate a combined TypeScript types file for all tables."""
    all_imports = set()
    all_types = []

    for table in tables:
        if hasattr(table, 'typescript_type'):
            all_imports.update(table.typescript_type.imports.split('\n'))
            all_types.append(table.typescript_type.type_definition)

    imports_str = '\n'.join(sorted(all_imports))
    types_str = '\n\n'.join(all_types)

    return f"""// File location: @/types/combinedTypes.ts
{imports_str}

{types_str}
"""
