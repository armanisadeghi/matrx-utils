# common/supabase/schema_manager/react/hook.py

class Hook:
    def __init__(self, table, config_manager):
        self.table = table
        self.config_manager = config_manager
        self.file_name = self.config_manager.generate_file_name("react", self.table.camelCaseName)
        self.directory = self.config_manager.generate_directory_path("react")
        self.file_location_print = f"// File location: {self.directory}{self.file_name}"
        self.name = f"use{self.table.PascalCaseName}"
        self.import_statement = f"import {{ {self.name} }} from '{self.directory}{self.file_name}';"

    def generate_hook(self):
        return f"""import {{ useEffect, useState }} from 'react';
import {{ {self.table.PascalCaseName}Service }} from '../services/{self.table.snake_case}Service';
import {{ {self.table.PascalCaseName} }} from '../models/{self.table.snake_case}';
import {{ {self.table.PascalCaseName}Form }} from '../forms/{self.table.snake_case}Form';
"""
