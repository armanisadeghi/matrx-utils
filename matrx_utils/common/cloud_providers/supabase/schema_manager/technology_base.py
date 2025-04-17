# common/supabase/schema_manager/technology_base.py
from common import pretty_print
from common.supabase.schema_manager.config_manager import TechnologyConfig
from common.supabase.schema_manager.utilities import CommonUtils


class TechColumn:
    def __init__(self, config, table, column):
        self.table = table
        self.column = column
        self.config = config
        self.utils = CommonUtils()
        self.loaded = False
        self.initialized = False

    def initialize(self):
        self.set_tech_specific_configs()

        self.initialized = True

    def set_tech_specific_configs(self):
        pass


class Technology(TechnologyConfig):
    def __init__(self, table, technology_name, config_object):
        super().__init__(technology_name)
        self.table = table
        self.technology_name = technology_name
        self.config_manager = self.table.config_manager
        self.config_object = config_object
        self.set_configs_object(self.config_object, self.table)
        self.imports = set()
        self.code_blocks = []
        self.name = self.get_name(self.table.table_name)
        self.file_name = None
        self.save_directory = None
        self.project_directory = None
        self.frontend_import_root = None
        self.import_statement = None
        self.file_location_print = None
        self.local_save_dir = None
        self.type_name = None
        self.type_file_name = None
        self.type_directory = None
        self.type_import_statement = None
        self.initialized = False
        self.column_configs = []



    def initialize(self):
        """Initialize technology-specific configurations."""
        self.get_info_as_type()
        self.set_column_details()
        self.set_package_defaults()
        self.initialize_configs()
        self.generate_custom_info(self.name)
        self.initialized = True
        self.initialize_technology()

    def set_column_details(self):
        if not hasattr(self.table, 'columns'):
            raise AttributeError("Table does not have 'columns' attribute")

        for column in self.table.columns:
            column_config = TechColumn(self, self.table, column)
            column_config.initialize()
            self.column_configs.append(column_config)

        return self.column_configs

    def get_info_as_type(self):
        """Initialize technology-specific configurations."""
        config_info = self.config_manager.generate_custom_info("typescript_types", self.table.table_name)

        # Extract the original name from the configuration
        original_name = config_info["name"]

        # Add curly braces around the name in the import statement
        # Assuming the import statement is structured as: import Name from '<path>';
        original_import_statement = config_info["import_statement"]

        # Modify the import statement by inserting curly braces around the name
        parts = original_import_statement.split(' ')
        if len(parts) > 1 and parts[1] == original_name:
            parts[1] = f"{{ {original_name} }}"  # Use curly braces here
        self.type_import_statement = ' '.join(parts)

        # Print the modified import statement for debugging
        if original_name == "Arg":
            print(f"------------------------------------------------------------------")
            pretty_print({**config_info,
                          "import_statement": self.type_import_statement})

        # Assign other configuration values
        self.type_name = original_name
        self.type_file_name = config_info["file_name"]
        self.type_directory = config_info["project_directory"]

    def set_package_defaults(self):
        # Package Imports:
        self.create_selector = "import { createSelector } from '@reduxjs/toolkit';"
        self.redux_root_store = "import { RootState } from '@/redux/store';"
        self.redux_middlewares = "import { Middleware } from 'redux';"


    def add_import(self, import_statement):
        """Add an import statement to the set of imports."""
        self.imports.add(import_statement)

    def add_code_block(self, code_block):
        """Add a code block to the list of code blocks."""
        self.code_blocks.append(code_block)

    def get_imports(self):
        """Get all unique import statements."""
        return "\n".join(sorted(self.imports))

    def get_code_blocks(self):
        """Get all code blocks."""
        return "\n\n".join(self.code_blocks)
