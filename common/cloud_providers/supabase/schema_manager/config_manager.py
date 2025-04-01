import os
from aidream.settings import BASE_DIR, TEMP_DIR
from common import vcprint, pretty_print
from common.supabase.schema_manager.config.tech_config import technology_config_defaults, framework_config_defaults, type_map_defaults, project_config_defaults, system_config_defaults, basic_config_defaults
from common.supabase.schema_manager.utilities import CommonUtils

verbose = False
class ColumnConfig:
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


class TableConfig:
    def __init__(self, config, table):
        self.table = table
        self.config = config
        self.utils = CommonUtils()
        self.loaded = False
        self.initialized = False
        self.column_configs = []

    def initialize(self):
        self.set_column_details()
        self.set_tech_specific_configs()
        self.initialized = True

    def set_column_details(self):
        if not hasattr(self.table, 'columns'):
            raise AttributeError("Table does not have 'columns' attribute")

        for column in self.table.columns:
            column_config = ColumnConfig(self.config, self.table, column)
            column_config.initialize()
            self.column_configs.append(column_config)

        return self.column_configs

    def set_tech_specific_configs(self):
        pass


class TechnologyConfig:
    """Class representing a technology configuration with precomputed values."""

    def __init__(self, tech_name):
        self.tech_name = tech_name
        vcprint(verbose=verbose, pretty=True, data=self.tech_name, title="Tech Name", color="blue")

        self.utils = CommonUtils()
        self.loaded = False
        self.initialized = False
        self.table_configs = []
        self.column_configs = []

    def set_configs(self, basic_config, system_configs, project_config, tech_config, framework_configs, type_map):
        self.basic_config = basic_config
        self.system_configs = system_configs
        self.project_config = project_config
        self.tech_config = tech_config
        self.framework_configs = framework_configs
        self.type_map = type_map
        self.loaded = True

    def set_configs_object(self, config_object, table):
        vcprint(verbose=verbose, pretty=True, data=config_object, title="Config Object", color="blue")
        self.table = table
        self.table_name = table.table_name
        self.basic_config = config_object['basic_config']
        self.system_configs = config_object['system_configs']
        self.project_config = config_object['project_config']
        self.tech_config = config_object['tech_config']
        self.framework_configs = config_object['framework_configs']
        self.type_map = config_object['type_map']
        self.initialize_configs()
        self.loaded = True

    def initialize_configs(self):
        """Initialize the technology configuration."""
        self.set_local_directories()
        self.set_production_directories()
        self.set_tech_configs()
        self.set_additional_project_configs()
        self.set_additional_framework_configs()
        self.generate_custom_info()
        self.name = self.get_name(self.table.table_name)
        self.file_name = self.get_file_name(self.table.table_name)
        self.local_full_path_and_file = self.get_local_full_path_and_file(self.table.table_name)
        self.code_save_dir = self.get_code_save_dir()
        self.import_with_brackets = self.get_import_with_brackets(self.table.table_name)
        self.import_without_brackets = self.get_import_without_brackets(self.table.table_name)
        self.file_location_print = self.get_file_location_print(self.table.table_name)
        self.initialized = True


    # "redux_selectors": {
    #     "name_format": "camel_case",
    #     "name_prefix": "",
    #     "name_suffix": "Selector",
    #     "save_dir": "redux/selectors/",
    #     "tech_dir": "redux/selectors/",
    #     "filename_prefix": "",
    #     "filename_suffix": "Selectors",
    #     "file_extension": "ts",
    #     "custom_configs": {},
    #     "project_type": "web_frontend"
    # },

    # system_config_defaults = {
    #     "code_save_dir": "code_gen_saves/",
    #     "frontend_import_root": "@/",
    # }

    def set_local_directories(self):
        """Location for saving files locally on the server."""
        self.local_code_save_root = os.path.normpath(os.path.join(TEMP_DIR, self.system_configs["code_save_dir"] or "ERROR-WITH-SYSTEM-CONFIG"))
        print(f"----------- Local code save root: {self.local_code_save_root}")
        self.local_code_save_dir = os.path.normpath(os.path.join(self.local_code_save_root, self.tech_config["save_dir"]))
        print(f"----------- Local code save dir: {self.local_code_save_dir}")
        self.local_full_tech_save_path = os.path.normpath(os.path.join(self.local_code_save_dir, self.get_file_name(self.table.table_name)))
        print(f"----------- Local full tech save dir: {self.local_full_tech_save_path}")

    def set_production_directories(self):
        """Location for where the generated code will be placed when used in the project natively."""
        vcprint(verbose=verbose, pretty=True, data=self.project_config, title="Project Config", color="green")
        self.project_root = self.project_config["root"]
        self.tech_dir = self.tech_config["tech_dir"]
        self.tech_project_dir = self.project_root + self.tech_dir

    def set_tech_configs(self):
        """Set the technology-specific configurations."""
        self.name_format = self.tech_config["name_format"]
        self.name_prefix = self.tech_config["name_prefix"]
        self.name_suffix = self.tech_config["name_suffix"]
        self.filename_prefix = self.tech_config["filename_prefix"]
        self.filename_suffix = self.tech_config["filename_suffix"]
        self.file_extension = self.tech_config["file_extension"]
        self.custom_configs = self.tech_config["custom_configs"]

    def set_additional_project_configs(self):
        """Set additional configurations for the project."""
        self.components_dir = self.project_config["components"]
        self.styles_dir = self.project_config["styles"]
        self.utilities_dir = self.project_config["utilities"]
        self.services_dir = self.project_config["services"]
        self.scripts_dir = self.project_config["scripts"]
        self.db_ops_dir = self.project_config["db_ops"]
        self.apis_dir = self.project_config["apis"]
        self.custom_project_configs = self.project_config["custom"]

    def set_additional_framework_configs(self):
        """Set additional configurations for the framework."""
        self.framework_root = self.framework_configs.get("project_root", "")
        self.framework_components_dir = self.framework_configs.get("components", "")
        self.framework_styles_dir = self.framework_configs.get("styles", "")
        self.framework_utilities_dir = self.framework_configs.get("utilities", "")
        self.framework_services_dir = self.framework_configs.get("services", "")
        self.framework_scripts_dir = self.framework_configs.get("scripts", "")
        self.framework_db_ops_dir = self.framework_configs.get("db_ops", "")
        self.framework_apis_dir = self.framework_configs.get("apis", "")
        self.custom_framework_configs = self.framework_configs.get("custom", {})

    def get_name(self, item_name):
        return getattr(self, self.name_format)(item_name)

    def get_file_name(self, item_name):
        return (f"{self.filename_prefix}{self.get_name(item_name)}{self.filename_suffix}.{self.file_extension}")

    def get_local_full_path_and_file(self, item_name):
        return f"{self.local_full_tech_save_dir}{self.get_file_name(item_name)}"
    def get_code_save_dir(self):
        return self.local_full_tech_save_dir

    def get_import_with_brackets(self, item_name):
        return f"import {{{ self.get_name(item_name) }}} from '{self.tech_project_dir}{self.filename_prefix}{self.get_name(item_name)}{self.filename_suffix}';"

    def get_import_without_brackets(self, item_name):
        return f"import {self.get_name(item_name)} from '{self.tech_project_dir}{self.filename_prefix}{self.get_name(item_name)}{self.filename_suffix}';"

    def get_file_location_print(self, item_name):
        return f"// File location: {self.tech_project_dir}{self.filename_prefix}{self.get_name(item_name)}{self.filename_suffix}.{self.file_extension}"

    def generate_custom_info(self, item_name=None):
        """Generate custom information for the technology."""
        if not item_name:
            item_name = self.table.table_name
        self.custom_info = {
            "name": self.get_name(item_name),
            "file_name": self.get_file_name(item_name),
            "local_code_save_root": self.local_code_save_root,
            "local_code_save_dir": self.local_code_save_dir,
            "local_full_path_and_file": self.get_local_full_path_and_file(item_name),
            "import_without_brackets": self.get_import_without_brackets(item_name),
            "import_with_brackets": self.get_import_with_brackets(item_name),
            "file_location_print": self.get_file_location_print(item_name),
        }
        pretty_print(self.custom_info, title="Custom Info", color="cyan")
        return self.custom_info

    def set_table_details(self, tables):
        """Set the table details for the technology."""
        for table in tables:
            table_config = TableConfig(self, table)
            table_config.initialize()
            self.table_configs.append(table_config)

    def camel_case(self, name):
        words = name.split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    def pascal_case(self, name):
        return ''.join(word.capitalize() for word in name.split('_'))

    def snake_case(self, name):
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')

    def to_dict(self):
        """Convert all attributes of the instance to a flat dictionary."""
        return {key: value for key, value in vars(self).items() if not key.startswith('_') and key != 'utils'}


class ConfigManager:
    def __init__(
            self,
            basic_config=None,
            project_configs_overrides=None,
            system_configs_overrides=None,
            technology_config_overrides=None,
            type_map_overrides=None,
            framework_configs_overrides=None,
    ):
        self.basic_configs = basic_config or basic_config_defaults

        self.project_configs = project_config_defaults
        if project_configs_overrides:
            self.project_configs.update(project_configs_overrides)

        self.system_configs = system_config_defaults
        if system_configs_overrides:
            self.system_configs.update(system_configs_overrides)

        self.framework_configs = framework_config_defaults
        if framework_configs_overrides:
            self.framework_configs.update(framework_configs_overrides)

        self.type_map = type_map_defaults
        if type_map_overrides:
            self.type_map.update(type_map_overrides)

        self.technology_configs = technology_config_defaults
        if technology_config_overrides:
            for key, override in technology_config_overrides.items():
                if key in self.technology_configs:
                    self.technology_configs[key].update(override)
                else:
                    self.technology_configs[key] = override

    def get_specific_technology_config(self, tech_name):
        if tech_name not in self.technology_configs:
            raise ValueError(f"Technology {tech_name} not found in configurations.")

        technology_specific_config = self.technology_configs[tech_name]

        project_type = technology_specific_config.get("project_type")
        vcprint(verbose=verbose, pretty=True, data=technology_specific_config, title=f"Technology Specific Config and project type: {project_type}", color="cyan")
        if not project_type:
            raise ValueError(f"Project type not found for technology {tech_name}.")

        tech_specific_project_config = self.project_configs.get(project_type)
        if not tech_specific_project_config:
            raise ValueError(f"Project configuration for type {project_type} not found.")

        configs = {
            "basic_config": self.basic_configs,
            "system_configs": self.system_configs,
            "project_config": tech_specific_project_config,
            "tech_config": technology_specific_config,
            "framework_configs": self.framework_configs,
            "type_map": self.type_map
        }
        return configs

    def create_technology_instances(self, tech_name):
        """Create an instance of TechnologyConfig for the technology and return the instance."""
        if tech_name not in self.technology_configs:
            raise ValueError(f"Technology {tech_name} not found in configurations.")

        technology_specific_config = self.technology_configs[tech_name]

        project_type = technology_specific_config.get("project_type")
        if not project_type:
            raise ValueError(f"Project type not found for technology {tech_name}.")

        tech_specific_project_config = self.project_configs.get(project_type)
        if not tech_specific_project_config:
            raise ValueError(f"Project configuration for type {project_type} not found.")

        technology_config_instance = TechnologyConfig(tech_name)

        technology_config_instance.set_configs(
            basic_config=self.basic_configs,
            system_configs=self.system_configs,
            project_config=tech_specific_project_config,
            tech_config=technology_specific_config,
            framework_configs=self.framework_configs,
            type_map=self.type_map
        )

        return technology_config_instance

    def get_local_code_save_directory(self):
        """Generate the local code save directory."""
        return os.path.normpath(os.path.join(TEMP_DIR, "code_gen_saves_DEFAULT"))

    def generate_custom_info(self, technology_name, item_name, overrides=None):
        tech_guidelines = self.technology_configs.get(technology_name)

        if not tech_guidelines or 'name_format' not in tech_guidelines:
            raise ValueError(f"Invalid or missing configuration for item_type: {technology_name}")

        # Get the naming method from the tech guidelines
        name_format_method = f"to_{tech_guidelines["name_format"]}"
        name = getattr(self, name_format_method)(item_name)

        # Construct the filename using the tech guidelines
        file_name = (
            f"{tech_guidelines['filename_prefix']}"
            f"{name}"
            f"{tech_guidelines['filename_suffix']}"
            f".{tech_guidelines['file_extension']}"
        )

        frontend_import_root = self.system_configs.get("frontend_import_root")
        save_directory = tech_guidelines["save_dir"]
        project_directory = tech_guidelines["tech_dir"]
        import_statement = f"import {name} from '{frontend_import_root}{project_directory}{file_name}';"
        file_location_print = f"// File location: {project_directory}{file_name}"
        local_parent_dir = self.get_local_code_save_directory()

        local_save_dir = os.path.join(local_parent_dir, save_directory, file_name)

        # Apply overrides if provided
        if overrides:
            file_name = overrides.get('file_name', file_name)
            save_directory = overrides.get('directory', save_directory)
            project_directory = overrides.get('project_directory', project_directory)
            frontend_import_root = overrides.get('frontend_import_root', frontend_import_root)
            import_statement = overrides.get('import_statement', import_statement)
            file_location_print = overrides.get('file_print_location', file_location_print)
            local_save_dir = overrides.get('local_save_dir', local_save_dir)

        self.custom_info = {
            "name": name,
            "file_name": file_name,
            "save_directory": save_directory,
            "project_directory": project_directory,
            "frontend_import_root": frontend_import_root,
            "import_statement": import_statement,
            "file_location_print": file_location_print,
            "local_save_dir": local_save_dir,
        }

        return self.custom_info

    def generate_directory_path(self, technology_name):
        """Generate a directory path based on the component type."""
        return self.technology_configs.get(technology_name, {}).get("project_dir", "")

    def to_camel_case(self, name):
        words = name.split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    def to_pascal_case(self, name):
        return ''.join(word.capitalize() for word in name.split('_'))

    def to_snake_case(self, name):
        return ''.join(['_' + c.lower() if c.isupper() else c for c in name]).lstrip('_')

    def generate_name_variations(self, name):
        """Generate all naming variations for a given name."""
        snake = self.to_camel_case(name)
        camel = self.to_pascal_case(snake)
        pascal = self.to_snake_case(snake)
        return {
            'snake_case': snake,
            'camel_case': camel,
            'pascal_case': pascal,
        }
