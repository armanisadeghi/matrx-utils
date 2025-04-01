from common import pretty_print
from common.supabase.schema_manager.technology_base import Technology


class Model(Technology):
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

        self.add_import("import { Model, attr, fk, many } from 'redux-orm';")

        if any(column.data_type == 'uuid' and column.default_value == 'gen_random_uuid()' for column in self.table.columns):
            self.add_import("import { v4 as uuidv4 } from 'uuid';")

        self.model_fields = self.generate_model_fields()
        self.static_options = self.generate_static_options()
        self.generate_model_class()
        self.file_content = self.generate_model_file()

    def generate_model_fields(self):
        """Generate Redux ORM fields."""
        redux_orm_fields = []
        for column in self.table.columns:
            if not column.is_foreign_key:
                redux_orm_fields.append(column.redux_orm_attr())

        for relation in self.table.relations:
            redux_orm_fields.append(relation['redux_orm_field'])

        return ',\n        '.join(redux_orm_fields)

    def generate_static_options(self):
        """Generate static options for fields with enumerated values."""
        options = [col.options_enum for col in self.table.columns if col.options_enum is not None]
        if options:
            return '    static options = {\n        ' + ',\n        '.join(options) + '\n    };'
        return ''

    def generate_model_class(self):
        options_block = self.generate_static_options()
        class_definition = f"""class {self.table.PascalCaseName} extends Model {{
    static modelName = '{self.table.PascalCaseName}';
    static fields = {{
        {self.model_fields}
    }};
{options_block}
}}"""
        self.add_code_block(class_definition)

    def generate_model_file(self):
        return f"""{self.file_location_print}
{self.get_imports()}

{self.get_code_blocks()}

export default {self.table.PascalCaseName};
"""

    def add_import(self, import_statement):
        """Override to handle technology-specific imports."""
        super().add_import(import_statement)
