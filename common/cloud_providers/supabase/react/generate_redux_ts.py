import os
from typing import List, Dict, Any
from common.supabase.manage_schema import get_full_schema
from common.supabase.react.column_management import Column
from common.supabase.react.config import get_config
from supabase import create_client, Client
from common import print_link, vcprint, pretty_print
from common.supabase.react.table_management import Table
from common.supabase.sql_generator.auto_sql.info.local_schema import get_db_schema
import traceback

verbose = False

local_schema = get_db_schema()


class TableFactory:
    @staticmethod
    def create_table(table_info: Dict) -> Table:
        try:
            table_name = table_info["table_name"]
            columns = table_info["schema"]
        except KeyError as e:
            print(f"Error: Missing required key in table_info: {e}")
            print(f"Table info: {table_info}")
            raise

        try:
            return Table(
                table_name=table_name,
                columns=columns,
                inbound_foreign_keys=[],
                outbound_foreign_keys=[]
            )
        except Exception as e:
            print(f"Error creating table '{table_name}': {str(e)}")
            print(f"Table info: {table_info}")
            print(traceback.format_exc())
            raise


import traceback


class RelationshipManager:
    @staticmethod
    def establish_relationships(tables: Dict[str, Table], schema_tables: List[Dict]):
        # First pass: Process outbound foreign keys
        for table_info in schema_tables:
            table_name = table_info["table_name"]
            if table_name not in tables:
                print(f"Error: Table '{table_name}' not found in processed tables. Skipping relationship establishment for this table.")
                continue

            table = tables[table_name]
            outbound_fks = table_info.get("outbound_foreign_keys", [])

            for i, fk in enumerate(outbound_fks):
                referenced_table = fk.get("referenced_table")
                if not referenced_table:
                    print(f"Warning: Missing 'referenced_table' key in outbound foreign key #{i + 1} for table '{table_name}'.")
                    print(f"Foreign key data: {fk}")
                    continue

                if referenced_table not in tables:
                    print(f"Warning: Referenced table '{referenced_table}' not found for outbound foreign key in table '{table_name}'")
                else:
                    try:
                        fk['referencing_table'] = table_name
                        table.add_outbound_foreign_key(fk)
                        # Add as inbound foreign key to the referenced table
                        tables[referenced_table].add_inbound_foreign_key(fk)
                    except Exception as e:
                        print(f"Error adding outbound foreign key to table '{table_name}': {str(e)}")
                        print(f"Foreign key data: {fk}")
                        print(traceback.format_exc())

        # Second pass: Process inbound foreign keys (for any that weren't caught in the first pass)
        for table_info in schema_tables:
            table_name = table_info["table_name"]
            table = tables[table_name]
            inbound_fks = table_info.get("inbound_foreign_keys", [])

            for i, fk in enumerate(inbound_fks):
                if 'referencing_table' not in fk:
                    # Try to find the referencing table based on the constraint name
                    constraint_name = fk.get('constraint_name', '')
                    referencing_table = constraint_name.split('_')[0] if '_' in constraint_name else None
                    if referencing_table and referencing_table in tables:
                        fk['referencing_table'] = referencing_table
                    else:
                        print(f"Warning: Unable to determine referencing table for inbound foreign key #{i + 1} in table '{table_name}'.")
                        print(f"Foreign key data: {fk}")
                        continue

                try:
                    table.add_inbound_foreign_key(fk)
                except Exception as e:
                    print(f"Error adding inbound foreign key to table '{table_name}': {str(e)}")
                    print(f"Foreign key data: {fk}")
                    print(traceback.format_exc())

        # After establishing all relationships, initialize each table
        for table in tables.values():
            table.initialize()

class CodeGenerator:
    def __init__(self, schema_source="local"):
        self.config = get_config()
        self.directories = self.config["directories"]
        self.schema_source = schema_source
        self.tables = []
        self.db_schema = None
        self.table_factory = TableFactory()
        self.relationship_manager = RelationshipManager()

        self.initialize_directories()

        try:
            if self.schema_source == "cloud":
                self.load_cloud_schema()
            else:
                self.load_local_schema()

            self.tables = self._initialize_tables()

            vcprint(verbose=verbose, pretty=True, data=self.tables, title="Table Names", color='green')

        except Exception as e:
            print(f"Failed to initialize database schema: {str(e)}")
            print(traceback.format_exc())
            if self.schema_source == "cloud":
                print("Attempting to load local schema as fallback...")
                try:
                    self.load_local_schema()
                    self.tables = self._initialize_tables()
                except Exception as e:
                    print(f"Failed to load local schema: {str(e)}")
                    print(traceback.format_exc())
                    self.tables = []
            else:
                print("Unable to load schema. Initializing with empty table list.")
                self.tables = []

    def load_cloud_schema(self):
        url: str = os.environ.get("SUPABASE_MATRIX_URL")
        key: str = os.environ.get("SUPABASE_MATRIX_KEY")
        supabase: Client = create_client(url, key)
        self.client = supabase
        schema = get_full_schema()
        schema_dict = vars(schema)
        self.db_schema = schema_dict.get('data', [])

    def load_local_schema(self):
        self.db_schema = local_schema

    def initialize_directories(self):
        """Create necessary directories for code generation."""
        for key, sub_dir in self.directories.items():
            full_path = os.path.join(self.directories["react_dir"], sub_dir)
            os.makedirs(full_path, exist_ok=True)
            vcprint(verbose=verbose, title="Directory Created", data=full_path, color="red")

    def _initialize_tables(self) -> List[Table]:
        """Initialize tables from the database schema."""
        schema_tables = self.db_schema.get("tables", [])
        if not schema_tables:
            print("Warning: No tables found in the schema.")
            return []

        tables = {}

        # First pass: Create Table objects
        for table_info in schema_tables:
            try:
                table_name = table_info["table_name"]
            except KeyError:
                print(f"Error: Missing 'table_name' key in table_info: {table_info}")
                continue

            print(f"Processing table: {table_name}")
            try:
                table = self.table_factory.create_table(table_info)
                tables[table_name] = table
            except Exception as e:
                print(f"Error creating table '{table_name}': {str(e)}")
                print(f"Table info: {table_info}")
                print(traceback.format_exc())

        # Second pass: Establish relationships
        try:
            self.relationship_manager.establish_relationships(tables, schema_tables)
        except Exception as e:
            print(f"Error establishing relationships: {str(e)}")
            print(traceback.format_exc())

        # Third pass: Initialize tables
        for table in tables.values():
            try:
                table.initialize()
            except Exception as e:
                print(f"Error initializing table '{table.original_name}': {str(e)}")
                print(traceback.format_exc())

        vcprint(verbose=verbose, pretty=True, data=list(tables.values()), title="Processed Tables", color='green')
        return list(tables.values())

    def map_to_typescript_type(self, column_name: str) -> str:
        """Map database columns to TypeScript types based on naming conventions."""
        type_mappings = self.config["typescript_type_mappings"]
        if column_name == "id" or column_name.endswith("Id"):
            return type_mappings["id"]
        if column_name in ["createdAt", "updatedAt"]:
            return type_mappings[column_name]
        if column_name.startswith("is"):
            return type_mappings["startsWithIs"]
        return type_mappings["default"]

    def get_table_filename(self, table_name: str, suffix_key: str) -> str:
        """Generate a standardized filename for a given table and suffix."""
        suffix = self.config["naming_conventions"][suffix_key]
        filename_format = self.config["naming_conventions"]["filename_format"]
        filename = filename_format.format(table_name=table_name, suffix=suffix)
        return filename

    def write_to_file(self, directory: str, filename: str, content: str):
        """Write content to a file in the specified directory."""
        full_path = os.path.join(self.directories["react_dir"], directory)
        if not os.path.exists(full_path):
            os.makedirs(full_path)
        save_path = os.path.join(full_path, filename)
        try:
            with open(save_path, "w") as f:
                f.write(content)
        except IOError as e:
            print(f"Failed to write to file {save_path}: {str(e)}")
            raise

    def generate_types(self):
        """Generate TypeScript types for all tables."""
        for table in self.tables:
            file_header = f"// types/{table.type_name}.ts\n"
            lines = [f"export type {table.type_name} = {{"]

            for column in table.columns:
                ts_type = self.map_to_typescript_type(column.name)
                lines.append(f"    {column.name}: {ts_type};")

            if table.inbound_foreign_keys:
                for fk in table.inbound_foreign_keys:
                    referenced_table = fk["referenced_table"]
                    referenced_table_name = Table.to_camel_case(referenced_table)
                    fk_field_name = Column.to_camel_case(referenced_table)
                    lines.append(f"    {fk_field_name}?: {referenced_table_name[0].upper() + referenced_table_name[1:]}[];")

            imports_code = "\n".join(table.imports)
            lines.append("};")

            type_code = "\n".join(lines)
            filename = self.get_table_filename(table.name, "type_suffix")
            self.write_to_file(self.directories["typescript_dir"], filename, f"{file_header}\n{imports_code}\n\n{type_code}")

    def generate_types_new(self):
        """Generate TypeScript types for all tables."""
        for table in self.tables:
            file_header = f"// types/{table.type_name}.ts\n"
            imports_code = table.ts_imports_code
            type_code = table.ts_type_declaration
            filename = self.get_table_filename(table.name, "type_suffix")
            self.write_to_file(self.directories["typescript_dir"], filename, f"{file_header}\n{imports_code}\n\n{type_code}_new")

    def generate_index(self):
        """Generate an index.ts file to export all generated files in a directory."""
        for directory, suffix in [
            (self.directories["typescript_dir"], self.config["naming_conventions"]["type_suffix"]),
            (self.directories["models_dir"], self.config["naming_conventions"]["model_suffix"]),
        ]:
            lines = ["// Index file for all generated types"]
            for table in self.tables:
                table_name = table.name
                lines.append(f"export * from './{table_name}{suffix}';")

            index_code = "\n".join(lines)
            self.write_to_file(directory, "index.ts", index_code)

    def generate_model_index(self):
        """Generate index.ts for models."""
        lines = ["// redux/models/index.ts"]
        for table in self.tables:
            table_name = table.name
            model_name = table_name[0].upper() + table_name[1:] + "Model"
            lines.append(f"import {model_name} from './{table_name}Model';")
        lines.append("\nexport {")
        for table in self.tables:
            table_name = table.name
            model_name = table_name[0].upper() + table_name[1:] + "Model"
            lines.append(f"    {model_name},")
        lines.append("};")

        model_index_code = "\n".join(lines)
        self.write_to_file(self.directories["models_dir"], "index.ts", model_index_code)

    def generate_model(self, table: Table):
        """
        Generate a Redux-ORM model class for a table including relationships.
        """

        def get_default_value(column: Column) -> str:
            """Get the default value for a column, if any."""
            if column.default_value is not None:
                return f"{{getDefault: () => {column.default_value}}}"
            if not column.is_required:
                return "{getDefault: () => null}"
            return ""

        def process_columns(columns: List[Column]) -> List[str]:
            """Generate attribute definitions for the columns."""
            return [
                f"        {column.name}: attr({get_default_value(column)}),"
                for column in columns if not column.is_foreign_key
            ]

        def process_inbound_foreign_keys(foreign_keys: List[Dict[str, Any]]) -> List[str]:
            """Generate many-to-many relationship definitions."""
            return [
                f"        {Column.to_camel_case(fk['referenced_table'])}: many('{fk['referenced_table'].capitalize()}'),"
                for fk in foreign_keys or []
            ]

        def process_outbound_foreign_keys(foreign_keys: List[Dict[str, Any]]) -> List[str]:
            """Generate foreign key relationship definitions."""
            return [
                (f"        {Column.to_camel_case(fk['foreign_key_column'])}: fk({{"
                 f"\n            to: '{fk['referenced_table'].capitalize()}',"
                 f"\n            as: '{fk['foreign_key_column']}',"
                 f"\n            relatedName: '{table.name}'}}),")
                for fk in foreign_keys or []
            ]

        # Constructing model class lines
        lines = [
            f"// redux/models/{table.type_name}Model.ts",
            "import {Model, attr, fk, many} from 'redux-orm';",
            "",
            "",
            f"class {table.type_name} extends Model {{",
            f"    static modelName = '{table.type_name}';",
            "    static fields = {"
        ]

        # Add processed columns and relationships to model fields
        lines.extend(process_columns(table.columns))
        lines.extend(process_inbound_foreign_keys(table.inbound_foreign_keys))
        lines.extend(process_outbound_foreign_keys(table.outbound_foreign_keys))

        lines.append("    };")
        lines.append("}")
        lines.append("")
        lines.append(f"export default {table.type_name};")

        # Join lines to form complete content
        content = "\n".join(lines)
        filename = self.get_table_filename(table.name, "model_suffix")
        self.write_to_file(self.directories["models_dir"], filename, content)

    def generate_slice(self, table: Table):
        """Generate a Redux slice using createSlice for an entity."""
        entity_name = table.name
        capitalized_name = table.type_name

        lines = [
            f"// redux/slices/{entity_name}Slice.ts",
            "import {createSlice, PayloadAction} from '@reduxjs/toolkit';",
            "import orm from '@/redux/orm';",
            f"import {{ {capitalized_name} }} from '../models/{entity_name}Model';",
            "",
            "const initialState = orm.getEmptyState();",
            "",
            f"const {entity_name}Slice = createSlice({{",
            f"    name: '{entity_name}',",
            "    initialState,",
            "    reducers: {",
            f"        add{capitalized_name}: (state, action: PayloadAction<Omit<{capitalized_name}, 'id'>>) => {{",
            "            const session = orm.session(state);",
            f"            const {{ {capitalized_name} }} = session;",
            f"            {capitalized_name}.create(action.payload);",
            "        },",
            f"        update{capitalized_name}: (state, action: PayloadAction<{capitalized_name}>) => {{",
            "            const session = orm.session(state);",
            f"            const {{ {capitalized_name} }} = session;",
            f"            const entity = {capitalized_name}.withId(action.payload.id);",
            "            if (entity) {",
            "                entity.update(action.payload);",
            "            }",
            "        },",
            f"        delete{capitalized_name}: (state, action: PayloadAction<string>) => {{",
            "            const session = orm.session(state);",
            f"            const {{ {capitalized_name} }} = session;",
            f"            const entity = {capitalized_name}.withId(action.payload);",
            "            if (entity) {",
            "                entity.delete();",
            "            }",
            "        },",
        ]

        for fk in table.inbound_foreign_keys:
            referenced_table = Column.to_camel_case(fk['referenced_table'])
            referenced_type = referenced_table[0].upper() + referenced_table[1:]
            lines.extend([
                f"        add{referenced_type}To{capitalized_name}: (state, action: PayloadAction<{{ {entity_name}Id: string, {referenced_table}Id: string }}>) => {{",
                "            const session = orm.session(state);",
                f"            const {{ {capitalized_name} }} = session;",
                f"            const entity = {capitalized_name}.withId(action.payload.{entity_name}Id);",
                "            if (entity) {",
                f"                entity.{referenced_table}s.add(action.payload.{referenced_table}Id);",
                "            }",
                "        },",
                f"        remove{referenced_type}From{capitalized_name}: (state, action: PayloadAction<{{ {entity_name}Id: string, {referenced_table}Id: string }}>) => {{",
                "            const session = orm.session(state);",
                f"            const {{ {capitalized_name} }} = session;",
                f"            const entity = {capitalized_name}.withId(action.payload.{entity_name}Id);",
                "            if (entity) {",
                f"                entity.{referenced_table}s.remove(action.payload.{referenced_table}Id);",
                "            }",
                "        },",
            ])

        lines.extend([
            "    },",
            "});",
            "",
            f"export const {{ add{capitalized_name}, update{capitalized_name}, delete{capitalized_name}"
        ])

        for fk in table.inbound_foreign_keys:
            referenced_table = Column.to_camel_case(fk['referenced_table'])
            referenced_type = referenced_table[0].upper() + referenced_table[1:]
            lines.extend([
                f", add{referenced_type}To{capitalized_name}, remove{referenced_type}From{capitalized_name}"
            ])

        lines.extend([
            f" }} = {entity_name}Slice.actions;",
            f"export default {entity_name}Slice.reducer;"
        ])

        content = "\n".join(lines)
        filename = self.get_table_filename(table.name, "slice_suffix")
        self.write_to_file(self.directories["slice_dir"], filename, content)

    def generate_middleware(self, table: Table):
        """Generate middleware for handling side-effects related to an entity, including relationships."""
        entity_name = table.name
        capitalized_name = table.type_name

        lines = [
            f"// redux/middleware/{entity_name}Middleware.ts",
            "import {Middleware} from 'redux';",
            f"import * as actions from '../slices/{entity_name}Slice';",
            f"import {{ default as {capitalized_name}Service }} from '../services/{entity_name}Service';",
            "",
            "const middleware: Middleware = store => next => async action => {",
            "    const result = next(action);",
            "",
            "    switch (action.type) {",
            f"        case actions.add{capitalized_name}.type:",
            "            try {",
            f"                await {capitalized_name}Service.create{capitalized_name}(action.payload);",
            "            } catch (error) {",
            f"                console.error('Error creating {entity_name}:', error);",
            "            }",
            "            break;",
            f"        case actions.update{capitalized_name}.type:",
            "            try {",
            f"                await {capitalized_name}Service.update{capitalized_name}(action.payload.id, action.payload);",
            "            } catch (error) {",
            f"                console.error('Error updating {entity_name}:', error);",
            "            }",
            "            break;",
            f"        case actions.delete{capitalized_name}.type:",
            "            try {",
            f"                await {capitalized_name}Service.delete{capitalized_name}(action.payload);",
            "            } catch (error) {",
            f"                console.error('Error deleting {entity_name}:', error);",
            "            }",
            "            break;",
        ]

        for fk in table.inbound_foreign_keys:
            referenced_table = Column.to_camel_case(fk['referenced_table'])
            referenced_type = referenced_table[0].upper() + referenced_table[1:]
            lines.extend([
                f"        case actions.add{referenced_type}To{capitalized_name}.type:",
                "            try {",
                f"                await {capitalized_name}Service.add{referenced_type}To{capitalized_name}(action.payload.{entity_name.lower()}Id, action.payload.{referenced_table.lower()}Id);",
                "            } catch (error) {",
                f"                console.error('Error adding {referenced_type} to {entity_name}:', error);",
                "            }",
                "            break;",
                f"        case actions.remove{referenced_type}From{capitalized_name}.type:",
                "            try {",
                f"                await {capitalized_name}Service.remove{referenced_type}From{capitalized_name}(action.payload.{entity_name.lower()}Id, action.payload.{referenced_table.lower()}Id);",
                "            } catch (error) {",
                f"                console.error('Error removing {referenced_type} from {entity_name}:', error);",
                "            }",
                "            break;",
            ])

        lines.extend([
            "        default:",
            "            break;",
            "    }",
            "",
            "    return result;",
            "};",
            "",
            "export default middleware;"
        ])

        content = "\n".join(lines)
        filename = self.get_table_filename(table.name, "middleware_suffix")
        self.write_to_file(self.directories["middleware_dir"], filename, content)

    def generate_reducer(self, table: Table):
        """
        Generate a Redux-ORM reducer function for an entity including relationships.
        """
        entity_name = table.name
        capitalized_name = table.type_name

        lines = [
            f"// redux/reducers/{entity_name}Reducer.ts",
            f"import {{ {capitalized_name} }} from '../models';",
            "import {AnyAction} from 'redux';",
            f"import * as actions from '../slices/{entity_name}Slice';",
            "",
            f"export function {entity_name}Reducer(",
            f"    action: AnyAction,",
            f"    {capitalized_name}: typeof {capitalized_name},",
            "    session: any",
            ") {",
            "    let instance;",
            "    switch (action.type) {",
            f"        case actions.add{capitalized_name}.type:",
            f"            {capitalized_name}.create(action.payload);",
            "            break;",
            f"        case actions.update{capitalized_name}.type:",
            f"            instance = {capitalized_name}.withId(action.payload.id);",
            "            if (instance) instance.update(action.payload);",
            "            break;",
            f"        case actions.upsert{capitalized_name}.type:",
            f"            {capitalized_name}.upsert(action.payload);",
            "            break;",
            f"        case actions.delete{capitalized_name}.type:",
            f"            instance = {capitalized_name}.withId(action.payload);",
            "            if (instance) instance.delete();",
            "            break;",
        ]

        for fk in table.inbound_foreign_keys or []:
            referenced_table = Column.to_camel_case(fk['referenced_table'])
            referenced_type = referenced_table[0].upper() + referenced_table[1:]
            lines.extend([
                f"        case actions.add{referenced_type}To{capitalized_name}.type:",
                f"            instance = {capitalized_name}.withId(action.payload.{entity_name.lower()}Id);",
                "            if (instance) {",
                f"                instance.{referenced_table}s.add(action.payload.{referenced_table}Id);",
                "            }",
                "            break;",
                f"        case actions.remove{referenced_type}From{capitalized_name}.type:",
                f"            instance = {capitalized_name}.withId(action.payload.{entity_name.lower()}Id);",
                "            if (instance) {",
                f"                instance.{referenced_table}s.remove(action.payload.{referenced_table}Id);",
                "            }",
                "            break;",
            ])

        lines.extend([
            "        default:",
            "            break;",
            "    }",
            "}"
        ])

        content = "\n".join(lines)
        filename = self.get_table_filename(entity_name, "reducer_suffix")
        self.write_to_file(self.directories["reducers_dir"], filename, content)

    def generate_action_creators(self, table: Table):
        """
        Generate action creators for an entity, including relationship management.
        """
        entity_name = table.name
        capitalized_name = table.type_name

        lines = [
            f"// redux/actions/{entity_name}Actions.ts",
            "import {createAction} from '@reduxjs/toolkit';",
            "",
            f"export const add{capitalized_name} = createAction<{capitalized_name}>('ADD_{entity_name.upper()}');",
            f"export const update{capitalized_name} = createAction<{capitalized_name}>('UPDATE_{entity_name.upper()}');",
            f"export const delete{capitalized_name} = createAction<number>('DELETE_{entity_name.upper()}');",
        ]

        for fk in table.inbound_foreign_keys or []:
            referenced_table = fk['referenced_table']
            referenced_table_name = Table.to_camel_case(referenced_table)
            lines.extend([
                f"export const add{referenced_table_name.capitalize()}To{capitalized_name} = createAction<{{ {entity_name.lower()}Id: number, {referenced_table_name.lower()}Id: number }}>('ADD_{referenced_table_name.upper()}_TO_{entity_name.upper()}');",
                f"export const remove{referenced_table_name.capitalize()}From{capitalized_name} = createAction<{{ {entity_name.lower()}Id: number, {referenced_table_name.lower()}Id: number }}>('REMOVE_{referenced_table_name.upper()}_FROM_{entity_name.upper()}');",
            ])

        content = "\n".join(lines)
        filename = self.get_table_filename(entity_name, "action_creators_suffix")
        self.write_to_file(self.directories["actions_dir"], filename, content)

    def generate_service(self, table: Table):
        """
        Generate a service class for handling API operations, including FK relationships.
        """
        entity_name = table.name
        capitalized_name = table.type_name

        def generate_fk_methods(foreign_keys: List[Dict[str, Any]]) -> List[str]:
            """Generate methods for handling inbound FK relationships."""
            methods = []
            for fk in foreign_keys or []:
                referenced_table = fk['referenced_table']
                referenced_table_name = Table.to_camel_case(referenced_table)
                methods.extend([
                    "",
                    f"    async add{referenced_table_name.capitalize()}To{capitalized_name}({entity_name.lower()}Id: number, {referenced_table_name.lower()}Id: number): Promise<void> {{",
                    f"        const {{ error }} = await this.supabase.from('{entity_name}_{referenced_table_name.lower()}_relation').insert({{ {entity_name.lower()}_id: {entity_name.lower()}Id, {referenced_table_name.lower()}_id: {referenced_table_name.lower()}Id }});",
                    "        if (error) throw error;",
                    "    }",
                    "",
                    f"    async remove{referenced_table_name.capitalize()}From{capitalized_name}({entity_name.lower()}Id: number, {referenced_table_name.lower()}Id: number): Promise<void> {{",
                    f"        const {{ error }} = await this.supabase.from('{entity_name}_{referenced_table_name.lower()}_relation').delete().match({{ {entity_name.lower()}_id: {entity_name.lower()}Id, {referenced_table_name.lower()}_id: {referenced_table_name.lower()}Id }});",
                    "        if (error) throw error;",
                    "    }",
                ])
            return methods

        lines = [
            "import supabase from '@/utils/supabase/client';",
            "import {SupabaseClient} from '@supabase/supabase-js';",
            f"import {{ {capitalized_name} }} from '../models/{entity_name}Model';",
            "",
            f"class {capitalized_name}Service {{",
            "    private supabase: SupabaseClient;",
            "",
            f"    constructor(supabase: SupabaseClient) {{",
            "        this.supabase = supabase;",
            "    }",
            "",
            f"    async create{capitalized_name}(data: Omit<{capitalized_name}, 'id'>): Promise<{capitalized_name}> {{",
            f"        const {{ data: result, error }} = await this.supabase.from('{entity_name}s').insert(data).single();",
            "        if (error) throw error;",
            "        return result;",
            "    }",
            "",
            f"    async get{capitalized_name}(id: number): Promise<{capitalized_name}> {{",
            f"        const {{ data, error }} = await this.supabase.from('{entity_name}s').select(`*`).eq('id', id).single();",
            "        if (error) throw error;",
            "        return data;",
            "    }",
            "",
            f"    async update{capitalized_name}(id: number, updates: Partial<{capitalized_name}>): Promise<{capitalized_name}> {{",
            f"        const {{ data, error }} = await this.supabase.from('{entity_name}s').update(updates).eq('id', id).single();",
            "        if (error) throw error;",
            "        return data;",
            "    }",
            "",
            f"    async upsert{capitalized_name}(data: {capitalized_name}): Promise<{capitalized_name}> {{",
            f"        const {{ data: result, error }} = await this.supabase.from('{entity_name}s').upsert(data).single();",
            "        if (error) throw error;",
            "        return result;",
            "    }",
            "",
            f"    async delete{capitalized_name}(id: number): Promise<void> {{",
            f"        const {{ error }} = await this.supabase.from('{entity_name}s').delete().eq('id', id);",
            "        if (error) throw error;",
            "    }",
        ]

        lines.extend(generate_fk_methods(table.inbound_foreign_keys))

        lines.extend([
            "}",
            "",
            f"export default new {capitalized_name}Service(supabase);"
        ])

        content = "\n".join(lines)
        filename = self.get_table_filename(entity_name, "service_suffix")
        self.write_to_file(self.directories["service_dir"], filename, content)

    def generate_selectors(self, table: Table):
        """
        Generate Redux-ORM selectors for an entity and its relationships.
        """
        entity_name = table.name
        capitalized_name = table.type_name

        lines = [
            f"// redux/selectors/{entity_name}Selectors.ts",
            "import {createSelector} from 'redux-orm';",
            "import orm from '@/redux/orm';",
            "",
            f"export const selectAll{capitalized_name} = createSelector(orm.{capitalized_name});",
            "",
            f"export const select{capitalized_name}ById = createSelector(",
            f"    orm.{capitalized_name},",
            f"    (_, id) => id,",
            f"    ({capitalized_name.lower()}, id) => {capitalized_name.lower()}.withId(id)",
            ");",
            ""
        ]

        # Relationship selectors
        for fk in table.inbound_foreign_keys:
            child_name = Column.to_camel_case(fk['referenced_table'])
            capitalized_child = child_name[0].upper() + child_name[1:]
            lines.extend([
                f"export const select{capitalized_name}With{capitalized_child} = createSelector(",
                f"    orm.{capitalized_name},",
                f"    orm.{capitalized_child},",
                f"    ({capitalized_name.lower()}, {child_name}) => {capitalized_name.lower()}.map(",
                "        parent => ({",
                "            ...parent.ref,",
                f"            {child_name}: parent.{child_name}.toModelArray().map(child => child.ref)",
                "        })",
                "    )",
                ");",
                ""
            ])

        for fk in table.outbound_foreign_keys:
            parent_name = Column.to_camel_case(fk['referenced_table'])
            capitalized_parent = parent_name[0].upper() + parent_name[1:]
            lines.extend([
                f"export const select{capitalized_name}With{capitalized_parent} = createSelector(",
                f"    orm.{capitalized_name},",
                f"    orm.{capitalized_parent},",
                f"    ({capitalized_name.lower()}, {parent_name}) => {capitalized_name.lower()}.map(",
                "        child => ({",
                "            ...child.ref,",
                f"            {parent_name}: child.{parent_name}.ref",
                "        })",
                "    )",
                ");",
                ""
            ])

        content = "\n".join(lines)
        filename = self.get_table_filename(entity_name, "selector_suffix")
        self.write_to_file(self.directories["selectors_dir"], filename, content)

    def generate_component(self, table: Table):
        """
        Generate a React component for an entity using Mantine UI, handling child relationships.
        """
        entity_name = table.name
        capitalized_name = table.type_name.capitalize()
        entity_list_name = f"{entity_name}List"

        # Determine child entities from inbound foreign keys
        child_entities = [
            fk['referenced_table'] for fk in table.inbound_foreign_keys or []
        ]

        def to_camel_case(snake_str):
            components = snake_str.split('_')
            return components[0] + ''.join(x.title() for x in components[1:])

        lines = [
            f"// components/{capitalized_name}List.tsx",
            "import React, { useState } from 'react';",
            "import {useSelector, useDispatch} from 'react-redux';",
            "import {Table, Button, Modal, TextInput, Group, List, Divider} from '@mantine/core';",
            f"import {{ add{capitalized_name}, update{capitalized_name}, delete{capitalized_name} }} from '@/redux/slices/{entity_name}Slice';",
            f"import {{ selectAll{capitalized_name} }} from '@/redux/selectors/{entity_name}Selectors';",
        ]

        for child in child_entities:
            child_camel = to_camel_case(child)
            lines.append(f"import {{ selectAll{child_camel} }} from '@/redux/selectors/{child}Selectors';")

        lines.extend([
            "",
            f"const {capitalized_name}List: React.FC = () => {{",
            "  const dispatch = useDispatch();",
            f"  const {entity_list_name} = useSelector(selectAll{capitalized_name});",
        ])

        # Selectors for child entities
        for child in child_entities:
            child_camel = to_camel_case(child)
            lines.append(f"  const {child_camel}List = useSelector(selectAll{child_camel});")

        lines.extend([
            "  const [opened, setOpened] = useState(false);",
            f"  const [selected{capitalized_name}, setSelected{capitalized_name}] = useState(null);",
            "  const [formData, setFormData] = useState({",
        ])

        for column in table.columns:
            lines.append(f"    {column.name}: '',")

        lines.extend([
            "  });",
            "",
            "  const handleChange = (field, value) => {",
            "    setFormData({ ...formData, [field]: value });",
            "  };",
            "",
            "  const handleSubmit = (e) => {",
            "    e.preventDefault();",
            f"    if (selected{capitalized_name}) {{",
            f"      dispatch(update{capitalized_name}(formData));",
            "    } else {",
            f"      dispatch(add{capitalized_name}(formData));",
            "    }",
            "    setOpened(false);",
            "    setFormData({",
        ])

        for column in table.columns:
            lines.append(f"      {column.name}: '',")

        lines.extend([
            "    });",
            "  };",
            "",
            "  const handleEdit = (entity) => {",
            f"    setSelected{capitalized_name}(entity);",
            "    setFormData(entity);",
            "    setOpened(true);",
            "  };",
            "",
            "  const handleDelete = (id) => {",
            f"    dispatch(delete{capitalized_name}(id));",
            "  };",
            "",
            "  return (",
            "    <div>",
            "      <Group justify='space-between' mb='md'>",  # Correct prop
            f"        <h3>{capitalized_name} List</h3>",
            "        <Button onClick={() => { setOpened(true); setSelected{capitalized_name}(null); }}>Add New</Button>",
            "      </Group>",
            "      <Table highlightOnHover withTableBorder>",  # Correct prop
            "        <thead>",
            "          <tr>",
        ])

        for column in table.columns:
            lines.append(f"            <th>{column.name.replace('_', ' ').capitalize()}</th>")

        lines.extend([
            "            <th>Actions</th>",
            "          </tr>",
            "        </thead>",
            "        <tbody>",
            f"          {{{entity_list_name}.map(({entity_name}) => (",
            "            <React.Fragment key={`${entity_name.id}`}>",
            f"            <tr key={{{entity_name}.id}}>",
        ])

        for column in table.columns:
            lines.append(f"              <td>{{{entity_name}.{column.name}}}</td>")

        lines.extend([
            "              <td>",
            f"                <Button onClick={{() => handleEdit({entity_name})}}>Edit</Button>",
            f"                <Button color='red' onClick={{() => handleDelete({entity_name}.id)}}>Delete</Button>",
            "              </td>",
            "            </tr>",
            f"            {child_entities and f'<tr key={{{entity_name}.id}}_childs>'}",  # Fixed here
            "              <td colSpan={6}>",
            f"                <Divider my='sm' label='{entity_name} Children' />",
        ])

        # Render child elements if they exist
        if child_entities:
            lines.append(f"            <tr key={{{entity_name}.id}}_childs>")
            lines.append("              <td colSpan={6}>")
            lines.append(f"                <Divider my='sm' label='{entity_name} Children' />")
            for child in child_entities:
                child_camel = Column.to_camel_case(child)
                lines.extend([
                    "                <List size='sm' withPadding>",
                    f"                  {{{child_camel}List.filter(child => child.{entity_name}_id === {entity_name}.id).map(child => (",
                    "                    <List.Item key={child.id}>{child.name} - {child.description}</List.Item>",
                    "                  ))}}",
                    "                </List>",
                ])
            lines.append("              </td>")
            lines.append("            </tr>")

        lines.extend([
            "            </React.Fragment>",  # Close fragment
            "          ))}}",
            "        </tbody>",
            "      </Table>",
            f"      <Modal opened={{opened}} onClose={{() => setOpened(false)}} title={{selected{capitalized_name} ? 'Edit' : 'Add New'}}>",
            "        <form onSubmit={handleSubmit}>",
        ])

        for column in table.columns:
            lines.append(f"          <TextInput label='{column.name.replace('_', ' ').capitalize()}' value={{formData.{column.name}}} onChange={{(e) => handleChange('{column.name}', e.target.value)}} />")

        lines.extend([
            "          <Group justify='flex-end' mt='md'>",
            f"            <Button type='submit'>{{selected{capitalized_name} ? 'Update' : 'Create'}}</Button>",
            "          </Group>",
            "        </form>",
            "      </Modal>",
            "    </div>",
            "  );",
            "};",
            "",
            f"export default {capitalized_name}List;",
        ])

        content = "\n".join(lines)
        filename = self.get_table_filename(entity_name, "component_suffix")
        self.write_to_file(self.directories["components_dir"], filename, content)

    def generate_store(self):
        """
        Generate the Redux store configuration.
        """
        lines = [
            "// redux/store.ts",
            "import { createStore, combineReducers } from 'redux';",
            "import { createReducer } from 'redux-orm';",
            "import orm from '@/redux/orm';",
        ]

        for table in self.tables:
            table_name = table.name.lower()
            reducer_name = table_name.capitalize() + "Reducer"
            lines.append(f"import {{ {reducer_name} }} from '@/redux/reducers/{table_name}Reducer';")

        lines.extend([
            "",
            "const rootReducer = combineReducers({",
            "    orm: createReducer(orm, (action, session) => {",
        ])

        for table in self.tables:
            table_name = table.name.lower()
            lines.append(f"        {table_name}Reducer(action, session.{table_name.capitalize()}, session);")

        lines.extend([
            "    }),",
            "    // Additional reducers can be added here",
            "});",
            "",
            "const store = createStore(rootReducer);",
            "export default store;",
        ])

        content = "\n".join(lines)
        filename = self.get_table_filename("store", "store_suffix")
        self.write_to_file(self.directories["store_dir"], filename, content)

    def process_table(self, table):
        """Process each table to generate required files and collect relationships."""
        vcprint(verbose=True, data=f"[MATRIX GENERATOR] Writing amazing code for {table.name}", color="blue")
        self.generate_types()
        #self.generate_types_new()
        self.generate_model(table)
        self.generate_slice(table)
        self.generate_middleware(table)
        self.generate_action_creators(table)
        self.generate_service(table)
        self.generate_reducer(table)
        self.generate_selectors(table)
        self.generate_component(table)

    def generate_code(self):
        """Main method to initiate code generation for all tables."""
        try:
            vcprint(verbose=True, data="[MATRIX TYPESCRIPT CODE GENERATOR] Initializing... ", color="green")

            for table in self.tables:
                self.process_table(table)
            self.finalize_code_generation()
        except Exception as e:
            print(f"Error during code generation: {str(e)}")
            raise

    def finalize_code_generation(self):
        """Finalize code generation by creating indexes and the store."""
        self.generate_index()
        self.generate_model_index()
        vcprint(verbose=True, data="[MATRIX TYPESCRIPT CODE GENERATOR] Code generation complete!", color="green")


def geterate_typescript_redux():
    try:
        generator = CodeGenerator()
        generator.generate_code()
    except Exception as e:
        print(f"Code generation failed: {str(e)}")


if __name__ == "__main__":
    geterate_typescript_redux()
