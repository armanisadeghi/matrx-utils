# common/supabase/schema_manager/schema_manager.py
import os

from common import print_link, pretty_print
from common.supabase.schema_manager.tables import Table
from common.supabase.schema_manager.technology_manager import TechnologyManager
from common.supabase.schema_manager.config_manager import ConfigManager
from common.supabase.sql_generator.auto_sql.info.local_schema import get_db_schema

import traceback
from colorama import Fore
import networkx as nx


class SchemaManager:
    def __init__(self, basic_config=None, default_technologies=None):
        self.config_manager = ConfigManager(basic_config=basic_config)
        self.tables = []
        self.schema = None
        self.loaded = False
        self.tables_initialized = False
        self.relations_set = False
        self.technologies_initialized = False
        self.default_technologies = default_technologies or ["typescript_types"]

    def load_schema(self, source="local"):
        try:
            if source == "local":
                self.schema = get_db_schema()
                for raw_table in self.schema['tables']:
                    table = Table(raw_table, self.config_manager)
                    table.load()
                    self.tables.append(table)
                self.loaded = True
                print(f"{Fore.GREEN}Schema loaded successfully. {len(self.tables)} tables loaded.")
        except Exception as e:
            print(f"{Fore.RED}Error loading schema: {str(e)}")
            print(f"{Fore.YELLOW}Traceback:")
            traceback.print_exc()

    def initialize_tables(self):
        if not self.loaded:
            print(f"{Fore.RED}Error: Schema must be loaded before initializing tables.")
            return

        for table in self.tables:
            table.initialize(self.default_technologies)
            table.technology_manager = TechnologyManager(table, self.config_manager)

        self.tables_initialized = True
        print(f"{Fore.GREEN}All tables initialized successfully.")

    def set_all_relations(self):
        if not self.loaded or not self.tables_initialized:
            print(f"{Fore.RED}Error: Schema must be loaded and tables must be initialized before setting relations.")
            return

        for table in self.tables:
            table.set_relations(self.tables)

        self.relations_set = True
        print(f"{Fore.GREEN}Relations set for all tables.")

    def initialize_technologies(self, additional_technologies=None):
        if not self.loaded or not self.tables_initialized or not self.relations_set:
            print(f"{Fore.RED}Error: Schema must be loaded, tables must be initialized, and relations must be set before initializing technologies.")
            return

        techs_to_use = self.default_technologies.copy()
        if additional_technologies:
            techs_to_use.extend([tech for tech in additional_technologies if tech not in techs_to_use])

        for table in self.tables:
            table.technology_manager.initialize_technologies(techs_to_use)

        self.technologies_initialized = True
        self.save_generated_content(techs_to_use)
        print(f"{Fore.GREEN}All technologies initialized and files saved for all tables.")

    def save_generated_content(self, technologies):
        for tech in technologies:
            for table in self.tables:
                tech_instance = table.technology_manager.get_technology(tech)
                if tech_instance and hasattr(tech_instance, 'file_content'):

                    file_path = tech_instance.local_full_path_and_file
                    print(f"{Fore.GREEN}File path: {file_path}")

                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w') as f:
                        f.write(tech_instance.file_content)
                    print_link(file_path)

    def run_complete_process(self, additional_technologies=None):
        if self.loaded:
            self.initialize_tables()
            if self.tables_initialized:
                self.set_all_relations()
                if self.relations_set:
                    self.initialize_technologies(additional_technologies)

    def initialize(self, additional_technologies=None):
        self.run_complete_process(additional_technologies)

    def get_generated_content(self, technology):
        if not self.technologies_initialized:
            print(f"{Fore.RED}Error: Technologies have not been initialized yet.")
            return {}

        content = {}
        for table in self.tables:
            tech_instance = table.technology_manager.get_technology(technology)
            if tech_instance and hasattr(tech_instance, 'file_content'):
                content[table.table_name] = tech_instance.file_content
        return content

    def get_raw_schema(self):
        return self.schema

    def get_table_names(self):
        return [table.table_name for table in self.tables]

    def get_table_details(self, table_name):
        for table in self.tables:
            if table.table_name == table_name:
                return {
                    "columns": [{
                        "Column": col.column_name,
                        "Data Type": col.data_type,
                        "Is Required": col.is_required,
                        "Default Value": col.default_value,
                        "Is Primary Key": col.is_primary_key,
                        "Is Foreign Key": col.is_foreign_key,
                        "Has Options": "Yes" if col.options else "No"
                    } for col in table.columns],
                    "inbound_foreign_keys": table.inbound_foreign_keys,
                    "outbound_foreign_keys": table.outbound_foreign_keys
                }
        return None

    def get_column_details(self, table_name, column_name):
        for table in self.tables:
            if table.table_name == table_name:
                for col in table.columns:
                    if col.column_name == column_name:
                        return col.raw_column
        return None

    def get_tables_summary(self):
        summary = []
        for table in self.tables:
            summary.append({
                "Table Name": table.table_name,
                "Primary Key": table.primary_key,
                "Column Count": len(table.columns),
                "Inbound FK Count": len(table.inbound_foreign_keys),
                "Outbound FK Count": len(table.outbound_foreign_keys)
            })
        return summary

    def get_relationships_graph(self):
        G = nx.DiGraph()
        for table in self.tables:
            for fk in table.outbound_foreign_keys:
                G.add_edge(table.table_name, fk['referenced_table'], key=fk['foreign_key_column'])
        return G


if __name__ == "__main__":
    basic_config = {
        "project_name": "ai_matrix",
        "frontend_framework": "next_js_14",
        "backend_server": "python",
        "backend_framework": "django",
        "database": "supabase",
    }

    schema_manager = SchemaManager(basic_config=basic_config)
    schema_manager.load_schema()

    schema_manager.initialize(["typescript_types", "redux_selectors"])


    # schema_manager.initialize(["typescript_types", "redux_selectors", "redux_models", "redux_middlewares", "redux_actions"])

    # Get generated content for TypeScript types and selectors
    typescript_types = schema_manager.get_generated_content('typescript_types')


    for typescript_type in typescript_types:
        print(typescript_type)

    #redux_models = schema_manager.get_generated_content('redux_models')
    redux_selectors = schema_manager.get_generated_content('redux_selectors')
    # redux_middlewares = schema_manager.get_generated_content('redux_middlewares')
    # redux_actions = schema_manager.get_generated_content('redux_actions')

    if typescript_types:
        recipe_example = typescript_types.get("recipe")
        if recipe_example:
            print("\nTypeScript Type for 'recipe':")
            print(recipe_example)

    # if redux_models:
    #     print(redux_models["arg"])
    #     print(redux_models["registered_function"])
    #     print(redux_models["recipe"])
    #
    if redux_selectors:
        selector_example = redux_selectors.get("recipe")
        if selector_example:
            print("\nRedux Selector for 'recipe':")
    #
    # if redux_actions:
    #     action_example = redux_actions.get("recipe")
    #     if action_example:
    #         print("\nRedux Actions for 'recipe':")
    #     print(action_example)
    #
    #
    # if redux_middlewares:
    #     middleware_example = redux_middlewares.get("recipe")
    #     if middleware_example:
    #         print("\nRedux Middleware for 'recipe':")
    #         print(middleware_example)





'''
# For a complete run with default technologies
schema_manager = SchemaManager()
schema_manager.run_complete_process()

# For a complete run with additional technologies
schema_manager = SchemaManager()
schema_manager.run_complete_process(["selector", "react_component"])

# For individual technology initialization (after loading schema and setting relations)
schema_manager = SchemaManager()
schema_manager.load_schema()
schema_manager.initialize_tables()
schema_manager.set_all_relations()
schema_manager.initialize_technology("typescript_type")
schema_manager.initialize_technology("selector")
'''
