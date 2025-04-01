# common/supabase/schema_manager/redux/middleware.py
from common.supabase.schema_manager.technology_base import Technology

class Middleware(Technology):
    def initialize_technology(self):
        self.middleware_cases = self.generate_all_middleware_cases()
        self.file_content = self.generate_middleware_file()


    def generate_middleware_case(self, child=None, action_type="add"):
        if child:
            action_name = f"{action_type}{child['PascalCaseName']}To{self.table.PascalCaseName}"
            service_method = f"{action_type}{child['PascalCaseName']}To{self.table.PascalCaseName}"
            error_message = f"Error {action_type.lower()}ing {child['PascalCaseName']} to {self.table.PascalCaseName}"
            payload = f"action.payload.{self.table.camelCaseName}Id, action.payload.{child['camelCaseName']}Id"
        else:
            action_name = f"{action_type}{self.table.PascalCaseName}"
            service_method = f"{action_type.lower()}{self.table.PascalCaseName}"
            error_message = f"Error {action_type.lower()}ing {self.table.PascalCaseName.lower()}"
            payload = "action.payload" if action_type != "delete" else "action.payload.id"

        return f"""
        case actions.{action_name}.type:
            try {{
                await {self.table.PascalCaseName}Service.{service_method}({payload});
            }} catch (error) {{
                console.error('{error_message}:', error);
            }}
            break;"""

    def generate_all_middleware_cases(self):
        cases = []
        for action_type in ["add", "update", "upsert", "delete"]:
            cases.append(self.generate_middleware_case(action_type=action_type))

        for relation in self.table.relations:
            if relation['type'] == 'inbound':
                child = {
                    'PascalCaseName': relation['referencing_table_pascal_case'],
                    'camelCaseName': relation['referencing_table_camel_case']
                }
                for action_type in ["add", "remove"]:
                    cases.append(self.generate_middleware_case(child, action_type))

        return "\n".join(cases)

    def generate_middleware_file(self):
        actions_info = self.config_manager.generate_custom_info("redux_actions", self.table.table_name)
        services_info = self.config_manager.generate_custom_info("supabase_services", self.table.table_name)

        return f"""{self.file_location_print}

{self.redux_middlewares}
import * as actions from '{actions_info['frontend_import_root']}{actions_info['project_directory']}{actions_info['file_name']}';
import {{ default as {self.table.PascalCaseName}Service }} from '{services_info['frontend_import_root']}{services_info['project_directory']}{services_info['file_name']}';

const middleware: Middleware = store => next => async action => {{
    const result = next(action);

    switch (action.type) {{
{self.middleware_cases}
        default:
            break;
    }}

    return result;
}};

export default middleware;
"""
