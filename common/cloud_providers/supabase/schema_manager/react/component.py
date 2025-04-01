# common/supabase/schema_manager/react/component.py

class Component:
    def __init__(self, table, config_manager):
        self.table = table
        self.config_manager = config_manager
        self.file_name = self.config_manager.generate_file_name("react", self.table.camelCaseName)
        self.directory = self.config_manager.generate_directory_path("react")
        self.file_location_print = f"// File location: {self.directory}{self.file_name}"
        self.name = f"{self.table.PascalCaseName}Component"
        self.import_statement = f"import {{ {self.name} }} from '{self.directory}{self.file_name}';"


    def generate_component(self):
        return f"""import React from 'react';
import {{ {self.table.PascalCaseName} }} from '../../types/{self.table.snake_case}Types';
"""
