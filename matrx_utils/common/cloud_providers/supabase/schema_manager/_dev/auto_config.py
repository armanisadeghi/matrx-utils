import os
from aidream.settings import BASE_DIR, TEMP_DIR
from common.supabase.schema_manager.utilities import CommonUtils


class TechnologyConfig:
    """Class representing a technology configuration with precomputed values."""

    def __init__(self, name, config, project_config, framework_configs, system_configs, utils):
        self.name = name
        self.utils = utils
        self.system_configs = system_configs
        self.project_config = project_config
        self.framework_configs = framework_configs

        self.name_format = config["name_format"]
        self.name_prefix = config["name_prefix"]
        self.name_suffix = config["name_suffix"]
        self.save_dir = os.path.normpath(config["save_dir"])
        self.project_dir = os.path.normpath(config["project_dir"]) if config["project_dir"] else ""
        self.filename_prefix = config["filename_prefix"]
        self.filename_suffix = config["filename_suffix"]
        self.file_extension = config["file_extension"]
        self.custom_configs = config["custom_configs"]

        # Project default values based on project type
        self.project_root = project_config["root"]
        self.components_dir = project_config["components"]
        self.styles_dir = project_config["styles"]
        self.utilities_dir = project_config["utilities"]
        self.services_dir = project_config["services"]
        self.scripts_dir = project_config["scripts"]
        self.db_ops_dir = project_config["db_ops"]
        self.apis_dir = project_config["apis"]
        self.custom_project_configs = project_config["custom"]

        # Framework-specific configurations
        self.framework_root = framework_configs.get("project_root", "")
        self.framework_components_dir = framework_configs.get("components", "")
        self.framework_styles_dir = framework_configs.get("styles", "")
        self.framework_utilities_dir = framework_configs.get("utilities", "")
        self.framework_services_dir = framework_configs.get("services", "")
        self.framework_scripts_dir = framework_configs.get("scripts", "")
        self.framework_db_ops_dir = framework_configs.get("db_ops", "")
        self.framework_apis_dir = framework_configs.get("apis", "")
        self.custom_framework_configs = framework_configs.get("custom", {})

        # Directly calculated values
        self.computed_name = self._compute_name(self.name)
        self.file_name = f"{self.filename_prefix}{self.computed_name}{self.filename_suffix}.{self.file_extension}"
        self.local_save_dir = os.path.normpath(os.path.join(TEMP_DIR, self.save_dir, self.file_name))

        # Values requiring further computation
        self.import_statement = self._compute_import_statement()
        self.file_location_print = self._compute_file_location_print()

    def _compute_name(self, item_name):
        """Compute the name using the specified format."""
        name_format_method = getattr(self.utils, f"to_{self.name_format}")
        return name_format_method(item_name)

    def _compute_import_statement(self):
        """Compute the import statement for the technology."""
        import_path = f"{self.project_root}{self.project_dir}/{self.file_name}" if self.project_dir else f"{self.project_root}{self.file_name}"
        return f"import {self.computed_name} from '{import_path}';"

    def _compute_file_location_print(self):
        """Generate the file location print statement."""
        location_path = f"{self.project_dir}/{self.file_name}" if self.project_dir else self.file_name
        return f"// File location: {location_path}"

    def to_dict(self):
        """Convert all attributes of the instance to a flat dictionary."""
        return {key: value for key, value in vars(self).items() if not key.startswith('_') and key != 'utils'}


class ConfigManager:
    def __init__(
        self,
        project_configs_overrides=None,
        system_configs_overrides=None,
        technology_config_overrides=None,
        type_map_overrides=None,
        framework_configs_overrides=None,
    ):
        self.utils = CommonUtils()

        # Framework-specific configurations
        self.framework_configs = {
            "next_js_14": {
                "project_root": "@/",
                "app_dir": "app",
                "api_dir": "app/api",
                "config_files": [
                    "next.config.js",
                    "tsconfig.json",
                    "jest.config.js",
                ],
                "components": "components",
                "styles": "styles",
                "utilities": "utils",
                "services": "services",
                "scripts": "scripts",
                "db_ops": "db_ops",
                "apis": "apis",
                "custom": {},
            },
        }

        if framework_configs_overrides:
            self.framework_configs.update(framework_configs_overrides)

        # Project type configurations
        self.project_configs = {
            "web_frontend": {
                "root": "@/",
                "components": "components",
                "styles": "styles",
                "utilities": "utils",
                "services": "services",
                "scripts": "scripts",
                "db_ops": "db_ops",
                "apis": "apis",
                "custom": {},
            },
            "web_backend": {
                "root": "/",
                "components": "components",
                "styles": "styles",
                "utilities": "utils",
                "services": "services",
                "scripts": "scripts",
                "db_ops": "db_ops",
                "apis": "apis",
                "custom": {},
            },
            "mobile": {
                "root": "@/",
                "components": "components",
                "styles": "styles",
                "utilities": "utils",
                "services": "services",
                "scripts": "scripts",
                "db_ops": "db_ops",
                "apis": "apis",
                "custom": {},
            },
            "desktop": {
                "root": "@/",
                "components": "components",
                "styles": "styles",
                "utilities": "utils",
                "services": "services",
                "scripts": "scripts",
                "db_ops": "db_ops",
                "apis": "apis",
                "custom": {},
            },
            "cloud_database": {
                "root": "/",
                "components": "",
                "styles": "",
                "utilities": "",
                "services": "",
                "scripts": "",
                "db_ops": "",
                "apis": "",
                "custom": {},
            },
            "local_database": {
                "root": "",
                "components": "",
                "styles": "",
                "utilities": "",
                "services": "",
                "scripts": "",
                "db_ops": "",
                "apis": "",
                "custom": {},
            },

            "cloud": {
                "root": "@/",
                "components": "components",
                "styles": "styles",
                "utilities": "utils",
                "services": "services",
                "scripts": "scripts",
                "db_ops": "db_ops",
                "apis": "apis",
                "custom": {},
            },
        }

        if project_configs_overrides:
            self.project_configs.update(project_configs_overrides)

        # System configurations
        self.system_configs = {
            "code_save_dir": "code_gen_saves",
        }
        if system_configs_overrides:
            self.system_configs.update(system_configs_overrides)

        # Initialize type map and apply overrides if any
        self.type_map = {
            "uuid": "string",
            "text": "string",
            "character varying": "string",
            "boolean": "boolean",
            "smallint": "number",
            "bigint": "number",
            "integer": "number",
            "real": "number",
            "double precision": "number"
        }
        if type_map_overrides:
            self.type_map.update(type_map_overrides)

        # Initialize technology configurations and apply overrides
        self.technology_configs = {
            "typescript_types": {
                "name_format": "pascal_case",
                "name_prefix": "",
                "name_suffix": "Types",
                "save_dir": "typescript/types",
                "project_dir": "types/",
                "filename_prefix": "",
                "filename_suffix": "Types",
                "file_extension": "ts",
                "custom_configs": {},
                "project_type": "web_frontend"
            },
            "typescript_helpers": {
                "name_format": "camel_case",
                "name_prefix": "",
                "name_suffix": "Helper",
                "save_dir": "typescript/helpers",
                "project_dir": "",
                "filename_prefix": "",
                "filename_suffix": "Helper",
                "file_extension": "ts",
                "custom_configs": {},
                "project_type": "web_frontend"
            },
            "typescript_utils": {
                "name_format": "camel_case",
                "name_prefix": "",
                "name_suffix": "Util",
                "save_dir": "typescript/utils",
                "project_dir": "",
                "filename_prefix": "",
                "filename_suffix": "Util",
                "file_extension": "ts",
                "custom_configs": {},
                "project_type": "web_frontend"
            },
            "python_classes": {
                "name_format": "pascal_case",
                "name_prefix": "",
                "name_suffix": "Class",
                "save_dir": "python/classes",
                "project_dir": "",
                "filename_prefix": "",
                "filename_suffix": "Class",
                "file_extension": "py",
                "custom_configs": {},
                "project_type": "web_backend"
            },
            "python_modules": {
                "name_format": "snake_case",
                "name_prefix": "",
                "name_suffix": "_module",
                "save_dir": "python/modules",
                "project_dir": "",
                "filename_prefix": "",
                "filename_suffix": "_module",
                "file_extension": "py",
                "custom_configs": {},
                "project_type": "web_backend"
            }
        }
        if technology_config_overrides:
            for key, override in technology_config_overrides.items():
                if key in self.technology_configs:
                    self.technology_configs[key].update(override)
                else:
                    self.technology_configs[key] = override

        # Create technology instances with the updated configurations
        self._create_technology_instances()

    def _create_technology_instances(self):
        """Create instances for each technology configuration."""
        self.technology_instances = {}
        for tech_name, config in self.technology_configs.items():
            project_type = config.get("project_type")
            project_config = self.project_configs[project_type]
            framework_config = self.framework_configs.get("next_js_14", {})
            self.technology_instances[tech_name] = TechnologyConfig(
                tech_name, config, project_config, framework_config, self.system_configs, self.utils
            )

    def __getattr__(self, item):
        if item in self.technology_instances:
            return self.technology_instances[item]
        raise AttributeError(f"No configuration available for '{item}'")

    def get_local_code_save_directory(self):
        """Generate the local code save directory."""
        return os.path.normpath(os.path.join(TEMP_DIR, "generated_code"))


# Example usage
technology_config_overrides = {}

config_manager = ConfigManager(technology_config_overrides=technology_config_overrides)

# Get the flat dictionary representation for TypeScript helpers
typescript_helpers_dict = config_manager.typescript_helpers.to_dict()
print("TypeScript Helpers Configuration:")
for key, value in typescript_helpers_dict.items():
    print(f"{key}: {value}")

# Get the flat dictionary representation for Python modules
python_modules_dict = config_manager.python_modules.to_dict()
print("\nPython Modules Configuration:")
for key, value in python_modules_dict.items():
    print(f"{key}: {value}")
