# common/supabase/schema_manager/redux/slice.py
from common.supabase.schema_manager.technology_base import Technology

class Slices:
    def __init__(self, table, config_manager):
        self.table = table
        self.config_manager = config_manager
        self.file_name = self.config_manager.generate_file_name("slice", self.table.camelCaseName)
        self.directory = self.config_manager.generate_directory_path("slice")
        self.file_location_print = f"// File location: {self.directory}{self.file_name}"
        self.name = f"{self.table.PascalCaseName}Slice"
        self.import_statement = f"import {{ {self.name} }} from '{self.directory}{self.file_name}';"


    def generate_slice_file(self):
        file_content = f"""
// File location: redux/slices/{self.table.snake_case}Slice.ts

import {{ createSlice, PayloadAction }} from '@reduxjs/toolkit';
import {{ {self.table.get_type_names()['entity']}, {self.table.get_type_names()['state']} }} from '../types/{self.table.snake_case}Types';

{self.table.get_import_statements()['type']}

const initialState: {self.table.get_type_names()['state']} = {{
    {self.table.camel_case}s: [],
}};

export const {self.table.get_slice_name()} = createSlice({{
    name: '{self.table.camel_case}',
    initialState,
    reducers: {{
        add{self.table.pascal_case}: (state, action: PayloadAction<{self.table.get_type_names()['entity']}>) => {{
            state.{self.table.camel_case}s.push(action.payload);
        }},
        update{self.table.pascal_case}: (state, action: PayloadAction<{self.table.get_type_names()['entity']}>) => {{
            const index = state.{self.table.camel_case}s.findIndex({self.table.camel_case} => {self.table.camel_case}.id === action.payload.id);
            if (index !== -1) {{
                state.{self.table.camel_case}s[index] = action.payload;
            }}
        }},
        delete{self.table.pascal_case}: (state, action: PayloadAction<string>) => {{
            state.{self.table.camel_case}s = state.{self.table.camel_case}s.filter({self.table.camel_case} => {self.table.camel_case}.id !== action.payload);
        }},
    }},
}});

export const {{
    add{self.table.pascal_case},
    update{self.table.pascal_case},
    delete{self.table.pascal_case},
}} = {self.table.get_slice_name()}.actions;

export default {self.table.get_slice_name()}.reducer;
"""
        return file_content

# common/supabase/schema_manager/redux/types.py
class Types:
    def __init__(self, table):
        self.table = table

    def generate_types_file(self):
        file_content = f"""
// File location: redux/types/{self.table.snake_case}Types.ts

export interface {self.table.get_type_names()['entity']} {{
    id: string;
{self.generate_entity_properties()}
}}

export interface {self.table.get_type_names()['state']} {{
    {self.table.camel_case}s: {self.table.get_type_names()['entity']}[];
}}

export interface {self.table.get_type_names()['payload']} {{
{self.generate_payload_properties()}
}}
"""
        return file_content

    def generate_entity_properties(self):
        return "\n".join([f"    {column.ts_property_with_optionality()};" for column in self.table.schema])

    def generate_payload_properties(self):
        return "\n".join([f"    {column.ts_property_with_optionality()};" for column in self.table.schema if not column.is_primary_key])
