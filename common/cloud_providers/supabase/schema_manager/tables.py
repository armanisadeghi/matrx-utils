from common import pretty_print
from common.supabase.schema_manager.columns import Column
from colorama import Fore
from common.supabase.schema_manager.technology_manager import TechnologyManager


class Table:
    def __init__(self, raw_table, config_manager):
        self.raw_table = raw_table
        self.config_manager = config_manager
        self.table_name = raw_table['table_name']
        self.primary_key = raw_table['primary_key']
        self.columns = [Column(self, col, self.config_manager) for col in raw_table['schema']]
        self.inbound_foreign_keys = raw_table['inbound_foreign_keys']
        self.outbound_foreign_keys = raw_table['outbound_foreign_keys']
        self.loaded = False
        self.initialized = False
        self.snake_case_name = self._to_snake_case(self.table_name)
        self.camelCaseName = self._to_camel_case(self.table_name)
        self.PascalCaseName = self._to_pascal_case(self.table_name)
        self.technology_manager = TechnologyManager(self, config_manager)

        # Pre-calculated values
        self.relations = []
        self.foreign_key_fields = []
        self.ts_type_properties = []
        self.static_options = []

        # Additional pre-calculated fields
        self.column_descriptions = []
        self.relationship_descriptions = []
        self.ts_interface = None

    def load(self):
        """Load all columns in the table."""
        for column in self.columns:
            column.load()
        self.loaded = True

    def __repr__(self):
        # List of column names
        column_names = " | ".join(column.column_name for column in self.columns)

        # Returning a formatted string with table names in different cases
        return (f"{self.table_name} | self.snake_case_name | self.PascalCaseName | self.camelCaseName:\n"
                f"--> Columns: {column_names}\n")

    def initialize(self, technologies):
        """Initialize the table with only the specified technologies."""
        if not self.loaded:
            print(f"{Fore.RED}Error: Table '{self.table_name}' cannot be initialized because it has not been loaded yet.")
            print(f"{Fore.YELLOW}Please call the load() method before initializing.")
            return

        # Initialize each column
        for column in self.columns:
            if not column.initialized:
                column.initialize()

        self.initialized = True
        self._set_column_descriptions()
        self._set_ts_interface()
        self._set_static_options()

    def set_relations(self, all_tables):
        """Set relations after all tables have been loaded."""
        self._set_relations(all_tables)
        self._set_ts_type_properties()
        # self._set_relationship_descriptions()

    def add_import(self, tech_name, import_statement):
        """Add an import statement to a specific technology."""
        self.technology_manager.add_import(tech_name, import_statement)

    def add_code_block(self, tech_name, code_block):
        """Add a code block to a specific technology."""
        self.technology_manager.add_code_block(tech_name, code_block)

    def _set_relations(self, all_tables):
        """Pre-calculate and store relations."""
        self.relations = []

        # Process outbound foreign keys
        for fk in self.outbound_foreign_keys:
            local_referencing_column = fk.get('local_referencing_column')
            referenced_table = fk.get('referenced_table')

            # Convert to camel case outside the append statement
            local_referencing_column_camel = self._to_camel_case(local_referencing_column)
            referenced_table_pascal = self._to_pascal_case(referenced_table)

            self.relations.append({
                'type': 'outbound',
                'constraint_name': fk.get('constraint_name'),
                'referenced_table': referenced_table,
                'referenced_table_snake_case': self._to_snake_case(referenced_table),
                'referenced_table_camel_case': self._to_camel_case(referenced_table),
                'referenced_table_pascal_case': referenced_table_pascal,
                'referenced_column': fk.get('referenced_column'),
                'referenced_column_snake_case': self._to_snake_case(fk.get('referenced_column')),
                'referenced_column_camel_case': self._to_camel_case(fk.get('referenced_column')),
                'referenced_column_pascal_case': self._to_pascal_case(fk.get('referenced_column')),
                'local_referencing_column': local_referencing_column,
                'local_referencing_column_snake_case': self._to_snake_case(local_referencing_column),
                'local_referencing_column_camel_case': local_referencing_column_camel,
                'local_referencing_column_pascal_case': self._to_pascal_case(local_referencing_column),
                'redux_orm_field': f"{local_referencing_column_camel}: fk({{\n"
                                               f"        to: '{referenced_table_pascal}',\n"
                                               f"        as: '{local_referencing_column_camel}',\n"
                                               f"        relatedName: '{self._to_camel_case(self.table_name)}s'\n"
                                               f"    }})"
            })

        # Process inbound foreign keys
        for fk in self.inbound_foreign_keys:
            referencing_table = fk.get('referencing_table')

            # Convert to camel case outside the append statement
            referencing_table_camel = self._to_camel_case(referencing_table)
            referencing_table_pascal = self._to_pascal_case(referencing_table)
            ts_property = f"{referencing_table_camel}?: {referencing_table_pascal}[];"
            import_statement = f"import {{ {referencing_table_pascal} }} from '@/types/{referencing_table_camel}Type';"

            self.relations.append({
                'type': 'inbound',
                'constraint_name': fk.get('constraint_name'),
                'referencing_table': referencing_table,
                'referencing_table_snake_case': self._to_snake_case(referencing_table),
                'referencing_table_camel_case': referencing_table_camel,
                'referencing_table_pascal_case': referencing_table_pascal,
                'referencing_column': fk.get('referencing_column'),
                'referencing_column_snake_case': self._to_snake_case(fk.get('referencing_column')),
                'referencing_column_camel_case': self._to_camel_case(fk.get('referencing_column')),
                'referencing_column_pascal_case': self._to_pascal_case(fk.get('referencing_column')),
                'local_referenced_column': fk.get('local_referenced_column'),
                'local_referenced_column_snake_case': self._to_snake_case(fk.get('local_referenced_column')),
                'local_referenced_column_camel_case': self._to_camel_case(fk.get('local_referenced_column')),
                'local_referenced_column_pascal_case': self._to_pascal_case(fk.get('local_referenced_column')),
                'redux_orm_field': f"{referencing_table_camel}: many('{referencing_table_pascal}')",
                'ts_property': ts_property,
                'import_statement': import_statement
            })

    def _set_ts_type_properties(self):
        """Pre-calculate and store TypeScript type properties."""
        self.ts_type_properties = [col.ts_property for col in self.columns if col.initialized]

    def _set_column_descriptions(self):
        """Pre-calculate and store descriptions of columns."""
        self.column_descriptions = [
            f"{col.column_name} ({col.data_type}): {'Required' if col.is_required else 'Optional'}"
            for col in self.columns
        ]

    def _set_ts_interface(self):
        """Pre-calculate and store the TypeScript interface definition."""
        properties = "\n  ".join(self.ts_type_properties)
        self.ts_interface = f"interface {self.PascalCaseName} {{\n  {properties}\n}}"

    def _set_static_options(self):
        """Pre-calculate and store static options for fields."""
        self.static_options = [
            col.options_enum for col in self.columns if col.options_enum is not None
        ]

    @staticmethod
    def _to_snake_case(name):
        """Convert a name to snake_case."""
        return name.lower().replace(' ', '_')

    @staticmethod
    def _to_camel_case(s):
        words = s.split('_')
        return words[0] + ''.join(word.capitalize() for word in words[1:])

    @staticmethod
    def _to_pascal_case(s):
        return ''.join(word.capitalize() for word in s.split('_'))

    def _create_ts_import_statement(self):
        """Generate the TypeScript import statement for the column."""
        return f"import {{ {self.PascalCaseName} }} from './{self.snake_case_name}Types';"

