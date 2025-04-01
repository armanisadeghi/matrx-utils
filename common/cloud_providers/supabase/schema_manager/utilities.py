# common/supabase/schema_manager/constants.py


class CommonUtils:
    @staticmethod
    def to_camel_case(s: str) -> str:
        """Convert a snake_case string to camelCase."""
        words = s.split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    @staticmethod
    def to_pascal_case(s: str) -> str:
        """Convert a snake_case string to PascalCase."""
        return ''.join(word.capitalize() for word in s.split('_'))

    @staticmethod
    def to_snake_case(s: str) -> str:
        """Convert a PascalCase or camelCase string to snake_case."""
        return ''.join(['_' + c.lower() if c.isupper() else c for c in s]).lstrip('_')

    @staticmethod
    def generate_name_variations(name: str) -> dict:
        """Generate all naming variations for a given name."""
        snake = CommonUtils.to_snake_case(name)
        camel = CommonUtils.to_camel_case(snake)
        pascal = CommonUtils.to_pascal_case(snake)
        return {
            'snake_case': snake,
            'camel_case': camel,
            'pascal_case': pascal,
        }


class CodeParts:
    class FileStructure:
        location_comment = "// File location: {path}"

    class Imports:
        redux_toolkit = "import { createSlice, PayloadAction } from '@reduxjs/toolkit';"
        orm = "import orm from '@/redux/orm';"
        model = "import { {model_name} } from '../models/{model_name_lowercase}Model';"

    class Redux:
        initial_state = "const initialState = orm.getEmptyState();"
        slice_declaration = "const {model_name_lowercase}Slice = createSlice({"
        action_export = "export const {{ {action_names} }} = {model_name_lowercase}Slice.actions;"
        reducer_export = "export default {model_name_lowercase}Slice.reducer;"

    class TypeScript:
        interface_declaration = "interface {interface_name} {"
        type_declaration = "type {type_name} = {"

    class React:
        functional_component = "const {component_name}: React.FC = () => {"
        use_state_hook = "const [{state_name}, set{state_name_capitalized}] = useState<{state_type}>({initial_value});"

    class Common:
        function_declaration = "function {function_name}({params}) {"
        arrow_function = "const {function_name} = ({params}) => {"
        class_declaration = "class {class_name} {"


class CodeBlockTemplate:
    def create_crud_operations(self, table_name, model_name):
        return f"""
        async create{model_name}(data: Omit<{model_name}, 'id'>): Promise<{model_name}> {{
            const {{ data: result, error }} = await this.supabase.from('{table_name}').insert(data).single();
            if (error) throw error;
            return result;
        }}

        async get{model_name}(id: number): Promise<{model_name}> {{
            const {{ data, error }} = await this.supabase.from('{table_name}').select(`*`).eq('id', id).single();
            if (error) throw error;
            return data;
        }}

        async update{model_name}(id: number, updates: Partial<{model_name}>): Promise<{model_name}> {{
            const {{ data, error }} = await this.supabase.from('{table_name}').update(updates).eq('id', id).single();
            if (error) throw error;
            return data;
        }}

        async delete{model_name}(id: number): Promise<void> {{
            const {{ error }} = await this.supabase.from('{table_name}').delete().eq('id', id);
            if (error) throw error;
        }}
        """
    def ts_type_definition(self):
        properties = [col.ts_property_with_optionality() for col in self.schema]
        foreign_keys = [f"{fk['referenced_table'].camel_case}?: {fk['referenced_table'].pascal_case}[]" for fk in self.inbound_foreign_keys]
        all_properties = properties + foreign_keys
        return f"""export type {self.pascal_case} = {{
        {';\\n    '.join(all_properties)}
    }};"""

    def redux_orm_model_class(self):
        fields = [col.redux_orm_attr() for col in self.schema]
        foreign_keys = [f"{fk['referenced_table'].camel_case}: many('{fk['referenced_table'].pascal_case}')" for fk in self.inbound_foreign_keys]
        all_fields = fields + foreign_keys
        return f"""class {self.pascal_case} extends Model {{
        static modelName = '{self.pascal_case}';
        static fields = {{
            {',\\n        '.join(all_fields)}
        }};
    }}"""




