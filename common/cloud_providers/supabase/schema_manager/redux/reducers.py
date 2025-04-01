# common/supabase/schema_manager/redux/reducers.py
from common.supabase.schema_manager.technology_base import Technology

from enum import Enum

class ReducerType(Enum):
    INSTANCE_MODIFICATION = "instance_modification"
    IMMUTABLE_STATE = "immutable_state"
    FLAT_ARRAY = "flat_array"

class Reducers(Technology):
    def initialize(self):
        self.name = f"{self.table.PascalCaseName}Reducer"
        self.file_name = self.config_manager.generate_file_name("redux", self.table.camelCaseName)
        self.directory = self.config_manager.generate_directory_path("redux")
        self.import_statement = f"import {{ {self.name} }} from '{self.directory}{self.file_name}';"
        self.file_location_print = f"// File location: {self.directory}{self.file_name}"



    def generate_reducer_case(self, action_type, reducer_type):
        if reducer_type == ReducerType.INSTANCE_MODIFICATION:
            return self.generate_instance_modification_case(action_type)
        elif reducer_type == ReducerType.IMMUTABLE_STATE:
            return self.generate_immutable_state_case(action_type)
        elif reducer_type == ReducerType.FLAT_ARRAY:
            return self.generate_flat_array_case(action_type)
        else:
            raise ValueError(f"Unsupported reducer type: {reducer_type}")

    def generate_instance_modification_case(self, action_type):
        action_types = self.table.get_action_types()
        if action_type == action_types['ADD']:
            return f"""
        case {action_types['ADD']}:
            {self.table.get_model_name()}.create(action.payload);
            break;
"""
        elif action_type == action_types['UPDATE']:
            return f"""
        case {action_types['UPDATE']}:
            {self.table.get_model_name()}.withId(action.payload.id).update(action.payload);
            break;
"""
        # Add more cases as needed

    def generate_immutable_state_case(self, action_type):
        action_types = self.table.get_action_types()
        if action_type == action_types['ADD']:
            return f"""
        case {action_types['ADD']}:
            return {{
                ...state,
                {self.table.camel_case}s: [...state.{self.table.camel_case}s, action.payload]
            }};
"""
        elif action_type == action_types['UPDATE']:
            return f"""
        case {action_types['UPDATE']}:
            return {{
                ...state,
                {self.table.camel_case}s: state.{self.table.camel_case}s.map({self.table.camel_case} => 
                    {self.table.camel_case}.id === action.payload.id ? {{...{self.table.camel_case}, ...action.payload}} : {self.table.camel_case}
                )
            }};
"""
        # Add more cases as needed

    def generate_flat_array_case(self, action_type):
        action_types = self.table.get_action_types()
        if action_type == action_types['ADD']:
            return f"""
        case {action_types['ADD']}:
            return [
                ...state,
                {{
                    id: action.payload.id,
                    ...action.payload
                }}
            ];
"""
        elif action_type == action_types['UPDATE']:
            return f"""
        case {action_types['UPDATE']}:
            return state.map({self.table.camel_case} => 
                {self.table.camel_case}.id === action.payload.id ? {{...{self.table.camel_case}, ...action.payload}} : {self.table.camel_case}
            );
"""
        # Add more cases as needed

    def generate_reducer_file(self, reducer_type):
        action_types = self.table.get_action_types()
        cases = [self.generate_reducer_case(action_type, reducer_type) for action_type in action_types.values()]

        file_content = f"""
// File location: redux/reducers/{self.table.snake_case}Reducer.ts

import {{ {self.table.get_action_types().__str__()} }} from '../actions/{self.table.snake_case}Actions';
import {{ {self.table.get_state_type()} }} from '../types/{self.table.snake_case}Types';

const initialState: {self.table.get_state_type()} = {{
    // Initialize your state here
}};

export const {self.table.get_reducer_name()} = (state = initialState, action: any): {self.table.get_state_type()} => {{
    switch (action.type) {{
{' '.join(cases)}
        default:
            return state;
    }}
}};
"""
        return file_content
