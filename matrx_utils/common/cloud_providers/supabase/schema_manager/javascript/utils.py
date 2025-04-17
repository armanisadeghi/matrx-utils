# common/supabase/schema_manager/javascript/utils.py

class JavaScriptUtil:
    def __init__(self, table, config_manager):
        self.table = table
        self.config_manager = config_manager
        self.file_name = self.config_manager.generate_file_name("javascript", self.table.camelCaseName)
        self.directory = self.config_manager.generate_directory_path("javascript")
        self.file_location_print = f"// File location: {self.directory}{self.file_name}"
        self.name = f"{self.table.PascalCaseName}Util"
        self.import_statement = f"import {{ {self.name} }} from '{self.directory}{self.file_name}';"

