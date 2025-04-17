# common/supabase/schema_manager/redux/store.py
from common.supabase.schema_manager.technology_base import Technology

class Store:
    def __init__(self, table, config_manager):
        self.table = table
        self.config_manager = config_manager
        self.file_name = self.config_manager.generate_file_name("store", self.table.camelCaseName)
        self.directory = self.config_manager.generate_directory_path("redux")
        self.file_location_print = f"// File location: {self.directory}{self.file_name}"
        self.name = f"{self.table.PascalCaseName}Store"
        self.import_statement = f"import {{ {self.name} }} from '{self.directory}{self.file_name}';"


    def generate_store_file(self):
        file_content = f"""
// File location: redux/store.ts

import {{ configureStore }} from '@reduxjs/toolkit';
{self.generate_reducer_imports()}

export const store = configureStore({{
    reducer: {{
{self.generate_reducer_config()}
    }},
}});

export type {self.tables[0].get_root_state_name()} = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
"""
        return file_content

    def generate_reducer_imports(self):
        return "\n".join([table.get_import_statements()['reducer'] for table in self.tables])

    def generate_reducer_config(self):
        return "\n".join([f"        {table.camel_case}: {table.get_reducer_name()}," for table in self.tables])
