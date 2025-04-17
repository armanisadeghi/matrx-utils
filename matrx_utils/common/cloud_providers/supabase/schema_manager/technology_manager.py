# common/supabase/schema_manager/technology_manager.py
from common import pretty_print
from common.supabase.schema_manager.javascript.helpers import JavaScriptHelper
from common.supabase.schema_manager.javascript.utils import JavaScriptUtil
from common.supabase.schema_manager.react.component import Component
from common.supabase.schema_manager.react.hook import Hook
from common.supabase.schema_manager.react.util import ReactUtil
from common.supabase.schema_manager.redux.actions import Action
from common.supabase.schema_manager.redux.middleware import Middleware
from common.supabase.schema_manager.redux.models import Model
from common.supabase.schema_manager.redux.reducers import Reducers
from common.supabase.schema_manager.redux.selectors import Selector
from common.supabase.schema_manager.redux.slice import Slices
from common.supabase.schema_manager.redux.store import Store
from common.supabase.schema_manager.supabase.rpcService import SupabaseRpcService
from common.supabase.schema_manager.supabase.service import SupabaseService
from common.supabase.schema_manager.typescript.helper import TypeScriptHelper
from common.supabase.schema_manager.typescript.types import TypeScriptType
from common.supabase.schema_manager.typescript.util import TypeScriptUtil
from colorama import Fore


class TechnologyManager:
    def __init__(self, table, config_manager):
        self.table = table
        self.config_manager = config_manager
        self.technologies = {}
        self.initialized_technologies = set()

        self.technology_classes = {
            "typescript_types": TypeScriptType,
            "redux_selectors": Selector,
            "redux_actions": Action,
            "redux_middlewares": Middleware,
            "redux_models": Model,
            "redux_reducers": Reducers,
            "redux_slices": Slices,
            "redux_store": Store,  # Assuming Store is a class for managing Redux stores
            "react_components": Component,
            "react_hooks": Hook,
            "react_utils": ReactUtil,
            "supabase_services": SupabaseService,
            "supabase_rpc_services": SupabaseRpcService,
            "typescript_helpers": TypeScriptHelper,
            "typescript_utils": TypeScriptUtil,
            "javascript_helpers": JavaScriptHelper,
            "javascript_utils": JavaScriptUtil,
            "supabase_db_ops": None,  # Placeholder for future implementation
            "supabase_rpc": None,     # Placeholder for future implementation
            "mantine_ui_components": None,  # Placeholder for Mantine UI components
            "tailwind_css": None,           # Placeholder for Tailwind CSS processing
            "shadcn_ui_components": None,   # Placeholder for Shadcn UI components
            "supabase_integration": None,   # Placeholder for Supabase integration
        }

        self.technologies = {}

        self.dependencies = {
            "selector": ["typescript_type"],
            "action": ["typescript_type"],
            "middleware": ["action"],
            "model": ["typescript_type"],
            "reducer": ["model"],
            "slice": ["reducer"],
            "store": ["slice"],
            "component": [],
            "hook": [],
            "supabase_service": ["model"],
            "supabase_rpc_service": ["model"],
            "typescript_helper": [],
            "typescript_util": ["typescript_helper"],
            "javascript_helper": [],
            "javascript_util": ["javascript_helper"],
            "supabase_db_op": [],
            "supabase_rpc": [],
            "mantine_ui_component": [],
            "tailwind_css": [],
            "shadcn_ui_component": [],
            "supabase_integration": [],
        }

    def initialize_technology(self, tech_name):
        if tech_name in self.initialized_technologies:
            print(f"{Fore.RED}Technology '{tech_name}' already initialized.")
            return

        if tech_name not in self.technology_classes:
            print(f"{Fore.YELLOW}Technology '{tech_name}' not found.")
            return

        if tech_name in self.technologies:
            return

        # Check and initialize dependencies first
        for dependency in self.dependencies.get(tech_name, []):
            self.initialize_technology(dependency)

        # Initialize the technology
        if self.technology_classes[tech_name] is not None:
            tech_configs = self.config_manager.get_specific_technology_config(tech_name)
            tech_instance = self.technology_classes[tech_name](self.table, tech_name, tech_configs)

            tech_instance.initialize()
            self.technologies[tech_name] = tech_instance
            setattr(self.table, tech_name, tech_instance)
            self.initialized_technologies.add(tech_name)
        else:
            print(f"{Fore.YELLOW}Technology '{tech_name}' is not implemented yet.")

    def initialize_technologies(self, tech_names):
        for tech_name in tech_names:
            self.initialize_technology(tech_name)

    def get_technology(self, tech_name):
        return self.technologies.get(tech_name)

    def get_initialized_technologies(self):
        return list(self.initialized_technologies)

    def add_import(self, tech_name, import_statement):
        """Add an import statement to a specific technology."""
        if tech_name in self.technologies:
            self.technologies[tech_name].add_import(import_statement)

    def add_code_block(self, tech_name, code_block):
        """Add a code block to a specific technology."""
        if tech_name in self.technologies:
            self.technologies[tech_name].add_code_block(code_block)

    def get_imports(self, tech_name):
        """Get imports for a specific technology."""
        if tech_name in self.technologies:
            return self.technologies[tech_name].get_imports()
        return ""

    def get_code_blocks(self, tech_name):
        """Get code blocks for a specific technology."""
        if tech_name in self.technologies:
            return self.technologies[tech_name].get_code_blocks()
        return ""

    def get_all_imports(self):
        """Get all imports for all technologies."""
        imports = set()
        for tech_name, tech_instance in self.technologies.items():
            imports.update(tech_instance.imports)
        return "\n".join(sorted(imports))




class AllTechnologies:
    def __init__(self):
        self.sql_basic = None
        self.sql_procedure = None
        self.sql_trigger = None
        self.sql_view = None
        self.sql_index = None
        self.sql_constraint = None
        self.supabase_integration = None
        self.python_basic = None
        self.python_oop = None
        self.python_function = None
        self.react_component = None
        self.react_hook = None
        self.react_utility = None
        self.redux_thunk = None
        self.supabase_db_op = None
        self.supabase_rpc = None
        self.mantine_ui_component = None
        self.tailwind_css = None
        self.shadcn_ui_component = None
