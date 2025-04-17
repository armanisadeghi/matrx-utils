from colorama import Fore

class Column:
    def __init__(self, table, raw_column, config_manager):
        self.raw_column = raw_column
        self.column_name = raw_column['column_name']
        self.data_type = raw_column['data_type']
        self.options = raw_column['options']
        self.is_required = raw_column['is_required']
        self.default_value = raw_column['default_value']
        self.is_primary_key = raw_column['is_primary_key']
        self.is_foreign_key = raw_column['is_foreign_key']
        self.config_manager = config_manager
        self.type_mapping = self.config_manager.type_map
        self.loaded = False
        self.initialized = False
        self.table = table


        # Calculated fields
        self.snake_case_name = None
        self.camelCaseName = None
        self.PascalCaseName = None

        # Pre-calculated fields for code generation
        self.ts_type = None
        self.ts_property = None
        self.redux_orm_field = None
        self.ts_import_statement = None
        self.ts_property_with_optionality = None
        self.redux_orm_many = None
        self.options_enum = None
        self.added_imports = []




    def load(self):
        """Load column data."""
        self.loaded = True
        self.snake_case_name = self.column_name.lower()
        self.camelCaseName = self._to_camel_case(self.column_name)
        self.PascalCaseName = self._to_pascal_case(self.column_name)

    def initialize(self):
        """Initialize column after loading."""
        if not self.loaded:
            print(f"{Fore.RED}Error: Column '{self.column_name}' cannot be initialized because it has not been loaded yet.")
            print(f"{Fore.YELLOW}Please call the load() method before initializing.")
            return

        self.initialized = True
        # print(f"\n\n{Fore.BLUE}Initializing column '{self.column_name}' --------------------------------------------------------")
        self.ts_type = self._get_ts_type()
        # print(f"{Fore.YELLOW}TypeScript type: {self.ts_type}")
        self.ts_property = self._get_ts_property()
        # print(f"{Fore.YELLOW}TypeScript property: {self.ts_property}")
        self.redux_orm_field = self._get_redux_orm_field()
        # print(f"{Fore.YELLOW}Redux ORM field: {self.redux_orm_field}")
        self.ts_property_with_optionality = self._create_ts_property_with_optionality()
        # print(f"{Fore.YELLOW}TypeScript property with optionality: {self.ts_property_with_optionality}")
        self.redux_orm_many = self._create_redux_orm_many()
        # print(f"{Fore.YELLOW}Redux ORM many: {self.redux_orm_many}")

        # Create options enum if applicable
        if self.options:
            self.options_enum = self._create_options_enum()
            # print(f"{Fore.YELLOW}Options enum: {self.options_enum}")
        else:
            # print(f"{Fore.YELLOW}No options found for column '{self.column_name}'.")
            pass

        # print(f"{Fore.BLUE}------------------------------------------------------------------------------------------------------\n\n")
    def __repr__(self):

        # Returning a formatted string with table names in different cases
        return (f"{self.column_name} | self.snake_case_name | self.PascalCaseName | self.camelCaseName:\n"
                f"--> Table:\n  {self.table.table_name}\n"
                f"--> Is Foreign Key:\n  {self.is_foreign_key}\n")

    @staticmethod
    def _to_camel_case(s):
        words = s.split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    @staticmethod
    def _to_pascal_case(s):
        return ''.join(word.capitalize() for word in s.split('_'))

    def _get_ts_type(self):

        return self.type_mapping.get(self.data_type, 'any')

    def generate_type_field(self, column):
        """Generate TypeScript type field for a column."""
        ts_type = self.type_mapping.get(column.data_type, 'any')
        optional = '' if column.is_required else '?'
        self.ts_type = f"{column.camelCaseName}{optional}: {ts_type};"

    def _get_ts_property(self):
        optional = '' if self.is_required else '?'
        return f"{self.camelCaseName}{optional}: {self.ts_type}"

    def _get_redux_orm_field(self):
        if self.is_foreign_key:
            return f"{self.camelCaseName}: fk('{self.PascalCaseName}')"
        else:
            return f"{self.camelCaseName}: attr()"

    def _create_ts_property_with_optionality(self):
        """Generate the TypeScript property declaration with optionality."""
        optional = '?' if not self.is_required else ''
        return f"{self.camelCaseName}{optional}: {self.ts_type}"

    def _create_redux_orm_many(self):
        """Generate the Redux ORM many relationship declaration for foreign keys."""
        return f"{self.camelCaseName}: many('{self.PascalCaseName}')"

    def _clean_default_value(self, value):
        if value is None:
            return None

        if value == "True" or value == "False":
            return value

        if isinstance(value, str):
            if '::' in value:
                value = value.split('::')[0]

            if value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

        try:
            return int(value)
        except (ValueError, TypeError):
            return value

    def _format_default_value(self):
        cleaned_default_value = self._clean_default_value(self.default_value)

        if cleaned_default_value is None:
            if self.options:
                return f'"{self.options[0]}"'
            return 'null'

        if self.data_type == 'boolean':
            return str(cleaned_default_value).lower()
        elif self.data_type in ['text', 'varchar', 'character varying']:
            escaped_value = str(cleaned_default_value).strip().replace('"', '\\"')
            return f'"{escaped_value}"'
        elif self.data_type in ['integer', 'bigint', 'numeric', 'smallint']:
            return str(cleaned_default_value)
        elif self.data_type == 'uuid' and cleaned_default_value == 'gen_random_uuid()':
            self._add_import('redux_models', "import { v4 as uuidv4 } from 'uuid';")
            return 'uuidv4()'
        elif self.data_type in ['jsonb', 'json']:
            return '{}'
        elif self.data_type.endswith('[]'):
            return '[]'

        return f'"{cleaned_default_value}"'

    def redux_orm_attr(self):
        """Generate Redux ORM attribute string."""
        formatted_default = self._format_default_value()

        if self.is_required and formatted_default == 'null':
            # For required fields with no default, we don't set a default in Redux ORM
            return f"{self.camelCaseName}: attr()"
        else:
            # For optional fields or fields with a default value
            return f"{self.camelCaseName}: attr({{ getDefault: () => {formatted_default} }})"

    def _create_options_enum(self):
        """Create enum representation for options if available."""
        options_str = ' | '.join(f'"{option}"' for option in self.options)
        self.ts_options = options_str
        self.options_enum = f"{self.camelCaseName}: [{', '.join(f'"{option}"' for option in self.options)}]"
        self.model_options = f'    static options = {{\n        {self.options_enum}\n    }};'
        return options_str

    def _add_import(self, technology, import_statement):
        """Add an import statement to the table for a specific technology."""
        self.table.add_import(technology, import_statement)

    def _add_code_block(self, technology, code_block):
        """Add a code block to the table for a specific technology."""
        self.table.add_code_block(technology, code_block)
