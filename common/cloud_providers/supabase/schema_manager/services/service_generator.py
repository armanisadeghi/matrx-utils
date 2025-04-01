# common/supabase/schema_manager/services/service_generator.py

from typing import List
from ..tables import Table


class ServiceParts:
    supabase_import = "import supabase from '@/utils/supabase/client';"
    supabase_client_import = "import { SupabaseClient } from '@supabase/supabase-js';"

    @staticmethod
    def model_import(model_name: str) -> str:
        return f"import {{ {model_name} }} from '../models/{model_name.lower()}Model';"

    @staticmethod
    def class_declaration(class_name: str) -> str:
        return f"""
class {class_name} {{
    private supabase: SupabaseClient;

    constructor(supabase: SupabaseClient) {{
        this.supabase = supabase;
    }}
"""

    @staticmethod
    def create_method(table_name: str, model_name: str) -> str:
        return f"""
    async create{model_name}(data: Omit<{model_name}, 'id'>): Promise<{model_name}> {{
        const {{ data: result, error }} = await this.supabase.from('{table_name}').insert(data).single();
        if (error) throw error;
        return result;
    }}
"""

    @staticmethod
    def get_method(table_name: str, model_name: str) -> str:
        return f"""
    async get{model_name}(id: number): Promise<{model_name}> {{
        const {{ data, error }} = await this.supabase.from('{table_name}').select(`*`).eq('id', id).single();
        if (error) throw error;
        return data;
    }}
"""

    @staticmethod
    def update_method(table_name: str, model_name: str) -> str:
        return f"""
    async update{model_name}(id: number, updates: Partial<{model_name}>): Promise<{model_name}> {{
        const {{ data, error }} = await this.supabase.from('{table_name}').update(updates).eq('id', id).single();
        if (error) throw error;
        return data;
    }}
"""

    @staticmethod
    def upsert_method(table_name: str, model_name: str) -> str:
        return f"""
    async upsert{model_name}(data: {model_name}): Promise<{model_name}> {{
        const {{ data: result, error }} = await this.supabase.from('{table_name}').upsert(data).single();
        if (error) throw error;
        return result;
    }}
"""

    @staticmethod
    def delete_method(table_name: str, model_name: str) -> str:
        return f"""
    async delete{model_name}(id: number): Promise<void> {{
        const {{ error }} = await this.supabase.from('{table_name}').delete().eq('id', id);
        if (error) throw error;
    }}
"""

    @staticmethod
    def add_relation_method(parent: str, child: str) -> str:
        return f"""
    async add{child}To{parent}({parent.lower()}Id: number, {child.lower()}Id: number): Promise<void> {{
        const {{ error }} = await this.supabase.from('{parent.lower()}_{child.lower()}_relation').insert({{ {parent.lower()}_id: {parent.lower()}Id, {child.lower()}_id: {child.lower()}Id }});
        if (error) throw error;
    }}
"""

    @staticmethod
    def remove_relation_method(parent: str, child: str) -> str:
        return f"""
    async remove{child}From{parent}({parent.lower()}Id: number, {child.lower()}Id: number): Promise<void> {{
        const {{ error }} = await this.supabase.from('{parent.lower()}_{child.lower()}_relation').delete().match({{ {parent.lower()}_id: {parent.lower()}Id, {child.lower()}_id: {child.lower()}Id }});
        if (error) throw error;
    }}
"""


def generate_service_file(table: Table) -> str:
    model_name = table.pascal_case
    table_name = table.snake_case

    methods = [
        ServiceParts.create_method(table_name, model_name),
        ServiceParts.get_method(table_name, model_name),
        ServiceParts.update_method(table_name, model_name),
        ServiceParts.upsert_method(table_name, model_name),
        ServiceParts.delete_method(table_name, model_name)
    ]

    for relation in table.relations:
        methods.append(ServiceParts.add_relation_method(model_name, relation['related_model']))
        methods.append(ServiceParts.remove_relation_method(model_name, relation['related_model']))

    service_content = f"""// File location: services/{table_name}Service.ts

{ServiceParts.supabase_import}
{ServiceParts.supabase_client_import}
{ServiceParts.model_import(model_name)}

{ServiceParts.class_declaration(f"{model_name}Service")}
{"".join(methods)}
}}

export default new {model_name}Service(supabase);
"""
    return service_content


def generate_all_services(tables: List[Table]) -> dict:
    """
    Generate service files for all tables in the project.

    :param tables: List of all tables in the project
    :return: Dictionary with table names as keys and service file contents as values
    """
    services = {}
    for table in tables:
        services[table.name] = generate_service_file(table)
    return services
