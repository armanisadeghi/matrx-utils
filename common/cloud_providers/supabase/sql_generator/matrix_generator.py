import os

from dotenv import load_dotenv

load_dotenv()

import random
import cmd
from typing import List, Dict
from datetime import datetime
from uuid import uuid4
from supabase import create_client, Client
from colorama import init, Fore, Back, Style
from aidream.settings import BASE_DIR, TEMP_DIR
import traceback
from tabulate import tabulate
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

init(autoreset=True)
import pprint
from colorama import init, Fore, Back, Style
from common import vcprint
from common.supabase.react.generate_redux_ts import geterate_typescript_redux

# from procedures.select_procedure import SelectProcedure
# from procedures.insert_procedure import InsertProcedure

verbose = True


class BaseColumnHandler:
    def __init__(self, column_name: str, is_required: bool):
        self.column_name = column_name
        self.is_required = is_required
        self.param_name = f"p_{column_name}"
        self.random_time = datetime.now().strftime("%M%S")

    def generate_test_value(self):
        raise NotImplementedError

    def generate_non_required_value(self):
        raise NotImplementedError

    def shared_values(self):
        function_name = f"add_one_{self.table_name}"

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}(\n  {self.formatted_drop_parameters}\n);"


class IntegerColumnHandler(BaseColumnHandler):
    def __init__(self, column_name: str, is_required: bool, min_value: int, max_value: int):
        super().__init__(column_name, is_required)
        self.min_value = min_value
        self.max_value = max_value

    def generate_test_value(self):
        random_value = random.randint(self.min_value, self.max_value)
        return f"{random_value}", f"{self.param_name} := {random_value}"

    def generate_non_required_value(self):
        non_req_random_value = random.randint(self.min_value, self.max_value)
        return f"{self.param_name} := {non_req_random_value}"


class SmallIntColumnHandler(IntegerColumnHandler):
    def __init__(self, column_name: str, is_required: bool):
        super().__init__(column_name, is_required, min_value=-32768, max_value=32767)


class IntColumnHandler(IntegerColumnHandler):
    def __init__(self, column_name: str, is_required: bool):
        super().__init__(column_name, is_required, min_value=-2147483648, max_value=2147483647)


class BigIntColumnHandler(IntegerColumnHandler):
    def __init__(self, column_name: str, is_required: bool):
        super().__init__(column_name, is_required, min_value=-9223372036854775808, max_value=9223372036854775807)


class TextColumnHandler(BaseColumnHandler):
    def generate_test_value(self):
        test_value = f"Sample{self.column_name}{self.random_time}"
        return f"'{test_value}'", f"{self.param_name} := '{test_value}'"

    def generate_non_required_value(self):
        non_req_value = f"NonReq{self.column_name}{self.random_time}"
        return f"{self.param_name} := '{non_req_value}'"


class UUIDColumnHandler(BaseColumnHandler):
    def generate_test_value(self):
        uuid_value = uuid4()
        return f"'{uuid_value}'", f"{self.param_name} := '{uuid_value}'"

    def generate_non_required_value(self):
        non_req_uuid = uuid4()
        return f"{self.param_name} := '{non_req_uuid}'"


class JSONBColumnHandler(BaseColumnHandler):
    def generate_test_value(self):
        random_key = random.choice(["alpha", "beta", "gamma"])
        json_value = f"jsonb_build_object('{random_key}', '{random_key}{self.random_time}')"
        return json_value, f"{self.param_name} := {json_value}"

    def generate_non_required_value(self):
        non_req_random_key = random.choice(["delta", "epsilon", "zeta"])
        non_req_json_value = f"jsonb_build_object('{non_req_random_key}', '{non_req_random_key}{self.random_time}')"
        return f"{self.param_name} := {non_req_json_value}"


class BooleanColumnHandler(BaseColumnHandler):
    def generate_test_value(self):
        random_bool = random.choice([True, False])
        return f"{random_bool}", f"{self.param_name} := {random_bool}"

    def generate_non_required_value(self):
        non_req_random_bool = random.choice([True, False])
        return f"{self.param_name} := {non_req_random_bool}"


class ColumnHandlerFactory:
    @staticmethod
    def get_handler(data_type: str, column_name: str, is_required: bool) -> BaseColumnHandler:
        if data_type in ['text', 'character varying']:
            return TextColumnHandler(column_name, is_required)
        elif data_type == 'uuid':
            return UUIDColumnHandler(column_name, is_required)
        elif data_type == 'bigint':
            return BigIntColumnHandler(column_name, is_required)
        elif data_type == 'integer':
            return IntColumnHandler(column_name, is_required)
        elif data_type == 'smallint':
            return SmallIntColumnHandler(column_name, is_required)
        elif data_type == 'jsonb':
            return JSONBColumnHandler(column_name, is_required)
        elif data_type == 'boolean':
            return BooleanColumnHandler(column_name, is_required)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")


class Column:
    def __init__(self, column_info: Dict):
        self.column_name = column_info['column_name']
        self.data_type = column_info['data_type']
        self.options = column_info.get('options', None)
        self.is_required = column_info['is_required']
        self.default_value = column_info.get('default_value', None)
        self.is_primary_key = column_info.get('is_primary_key', False)
        self.column_name_camel = self.to_camel_case(self.column_name)
        self.column_name_pascal = self.to_pascal_case(self.column_name)
        self.column_name_p = self.add_prefix(self.column_name)

    @staticmethod
    def to_camel_case(name: str) -> str:
        parts = name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    @staticmethod
    def to_pascal_case(name: str) -> str:
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)
    @staticmethod
    def add_prefix(name: str) -> str:
        return f"p_{name}"

    def __repr__(self):
        return f"Column({self.column_name}, {self.data_type}, PK={self.is_primary_key})"



class Table:
    def __init__(self, table_info: Dict):
        self.table_name = table_info['table_name']
        self.primary_key = table_info['primary_key']
        self.columns = [Column(col) for col in table_info['schema']]
        self.inbound_foreign_keys = table_info.get('inbound_foreign_keys', [])
        self.outbound_foreign_keys = table_info.get('outbound_foreign_keys', [])
        self.table_name_camel = self.to_camel_case(self.table_name)
        self.table_name_pascal = self.to_pascal_case(self.table_name)

    def __repr__(self):
        return f"Table({self.table_name}, Columns={len(self.columns)})"

    @staticmethod
    def to_camel_case(name: str) -> str:
        parts = name.split('_')
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])

    @staticmethod
    def to_pascal_case(name: str) -> str:
        parts = name.split('_')
        return ''.join(word.capitalize() for word in parts)

    def get_column_names(self) -> List[str]:
        return [column.column_name for column in self.columns]

    def get_common_values(self, function_core):
        full_function_name = f"public.{function_core}_{self.table_name}"
        test_function_name = f"SELECT * FROM public.{function_core}_{self.table_name}"
        create_statement = f"CREATE OR REPLACE FUNCTION {full_function_name}(\n  {self.formatted_create_parameters}\n)\nRETURNS TABLE (\n  {self.formatted_columns}\n) LANGUAGE plpgsql AS $function$"

    def get_full_function_name(self, function_core):
        return f"public.{function_core}_{self.table_name}"

    def get_full_test_function_name(self, function_core):
        return f"SELECT * FROM public.{function_core}_{self.table_name}"


class Schema:
    def __init__(self, tables_info: List[Dict]):
        if not isinstance(tables_info, list):
            raise ValueError("Expected tables_info to be a list of dictionaries")
        self.tables = [Table(table_info) for table_info in tables_info]

    def __repr__(self):
        return f"Schema(Tables={len(self.tables)})"

    def get_table_names(self) -> List[str]:
        return [table.table_name for table in self.tables]

    def find_table_by_name(self, name: str) -> Table:
        for table in self.tables:
            if table.table_name == name:
                return table
        raise ValueError(f"Table {name} not found in schema.")


class SQLProcedureGenerator:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_MATRIX_URL")
        key: str = os.environ.get("SUPABASE_MATRIX_KEY")
        supabase: Client = create_client(url, key)
        self.client = supabase
        self.schema = None
        self.tables = None

        # Initialize storage for processed information
        self.columns_list = []
        self.values_list = []
        self.return_columns_list = []
        self.drop_parameters = []
        self.set_clause = []
        self.required_parameters = []
        self.optional_parameters = []
        self.test_values = []
        self.test_arguments = []
        self.non_required_test_arguments = []
        self.primary_key = None
        self.drop_statements = {}
        self.core_procedures = {}
        self.test_statements = {}

    def load_cloud_schema(self):
        results = self.client.rpc("get_database_schema_json").execute()
        vcprint(data=results, title="get_database_schema_json", pretty=True, verbose=False, color="blue")

        # results = self.client.rpc("get_schema").execute()
        # vcprint(data=results, title="get_schema", color="green")

        schema_dict = vars(results)
        self.schema = schema_dict.get('data', {})

        # Extract tables from the schema
        tables_data = self.schema.get('tables', [])

        # Ensure the schema data is a list of dictionaries
        if isinstance(tables_data, list) and all(isinstance(item, dict) for item in tables_data):
            # Load tables into the Schema object
            self.tables = Schema(tables_data)
            print(f"Loaded tables: {self.tables}")
        else:
            raise ValueError("Tables data is not in the expected format (list of dictionaries).")

    def get_procedure_details(self):
        # Inspect get_database_schema_json
        result = self.client.table("pg_proc").select("prosrc").eq("proname", "get_database_schema_json").execute()
        print("get_database_schema_json definition:")
        print(result.data[0]['prosrc'] if result.data else "Function not found")

        # Inspect get_schema
        result = self.client.table("pg_proc").select("prosrc").eq("proname", "get_schema").execute()
        print("\nget_schema definition:")
        print(result.data[0]['prosrc'] if result.data else "Function not found")

    def print_raw_schema(self):
        pp = pprint.PrettyPrinter(indent=4, width=180)
        pp.pprint(self.schema)

    def fetch_table_data(self, table_name: str, limit: int = 10):
        try:
            result = self.client.table(table_name).select("*").limit(limit).execute()
            self.last_query_result = result.data
            return result.data
        except Exception as e:
            print(f"Error fetching data from {table_name}: {str(e)}")
            return None

    def execute_custom_query(self, query: str):
        try:
            result = self.client.rpc(query).execute()
            self.last_query_result = result.data
            return result.data
        except Exception as e:
            print(f"Error executing custom query: {str(e)}")
            return None

    def process_columns(self, columns: List[Column]):
        # Reset storage for each table
        self.columns_list = []
        self.values_list = []
        self.return_columns_list = []
        self.drop_parameters = []
        self.set_clause = []
        self.required_parameters = []
        self.optional_parameters = []
        self.test_values = []
        self.test_arguments = []
        self.non_required_test_arguments = []

        for column in columns:
            column_name = column.column_name
            data_type = column.data_type
            is_required = column.is_required
            options = column.options
            is_primary_key = column.is_primary_key
            param_name = f"p_{column_name}"

            # Handle primary key
            if is_primary_key:
                self.primary_key = column_name

            # Store column info
            self.columns_list.append(f'"{column_name}"')
            self.values_list.append(param_name)
            self.return_columns_list.append(f'  "{column_name}" {data_type}')
            self.drop_parameters.append(f"{param_name} {data_type}")

            # Prepare set clause for non-primary keys
            if not is_primary_key:
                self.set_clause.append(f'"{column_name}" = EXCLUDED."{column_name}"')

            # Use factory to get the appropriate handler
            handler = ColumnHandlerFactory.get_handler(data_type, column_name, is_required)

            if is_required:
                print(f"'{column_name}' is required.")
                test_value, test_argument = handler.generate_test_value()
                self.test_values.append(test_value)
                self.test_arguments.append(test_argument)
                self.required_parameters.append(f"{param_name} {data_type}")
            else:
                print(f"'{column_name}' is optional.")
                non_required_argument = handler.generate_non_required_value()
                self.optional_parameters.append(f"{param_name} {data_type} DEFAULT NULL")
                self.non_required_test_arguments.append(non_required_argument)

        # Prepare formatted strings
        self.create_parameters = self.required_parameters + self.optional_parameters
        self.formatted_drop_parameters = ',\n  '.join(self.drop_parameters)
        self.formatted_create_parameters = ',\n  '.join(self.create_parameters)
        self.formatted_columns = ',\n  '.join(self.columns_list)
        self.formatted_values = ',\n  '.join(self.values_list)
        self.formatted_return_query = ',\n    '.join([f'inserted_row."{col}"' for col in self.columns_list])
        self.formatted_test_values = ',\n  '.join(self.test_values)
        self.formatted_test_arguments = ',\n  '.join(self.test_arguments)
        self.formatted_non_required_test_arguments = ',\n  '.join(self.non_required_test_arguments)
        self.formatted_set_clause = ',\n    '.join(self.set_clause)

    def generate_select_procedure(self):
        select_procedure = SelectProcedure(self.table_name, self.columns, self.primary_key)
        return select_procedure.generate_procedure(), select_procedure.generate_test_statement()

    def generate_insert_procedure(self):
        insert_procedure = InsertProcedure(
            self.table_name,
            self.columns,
            self.primary_key,
            self.formatted_create_parameters,
            self.formatted_columns,
            self.formatted_values,
            self.return_columns_list,
            self.formatted_return_query,
            self.formatted_test_arguments
        )
        return insert_procedure.generate_procedure(), insert_procedure.generate_test_statement()

    def process_table(self, table_name: str):
        try:
            table = self.tables.find_table_by_name(table_name)
            print(f"Processing table '{table_name}'")
            self.process_columns(table.columns)
        except ValueError as e:
            print(str(e))

    def get_table_details(self, table_name: str) -> Dict:
        table = self.tables.find_table_by_name(table_name)
        details = {
            "columns": [],
            "inbound_foreign_keys": table.inbound_foreign_keys,
            "outbound_foreign_keys": table.outbound_foreign_keys
        }
        for column in table.columns:
            details["columns"].append({
                "Column": column.column_name,
                "Required": "Yes" if column.is_required else "No",
                "DataType": column.data_type,
                "Default": column.default_value if column.default_value else "None",
                "PK": "Yes" if column.is_primary_key else "No",
                "Has Options": "Yes" if column.options and column.options != "None" else "No"
            })
        return details

    def get_tables_summary(self) -> List[Dict]:
        summary = []
        for table in self.tables.tables:
            inbound_fk_count = len(table.inbound_foreign_keys) if table.inbound_foreign_keys and table.inbound_foreign_keys != "None" else 0
            outbound_fk_count = len(table.outbound_foreign_keys) if table.outbound_foreign_keys and table.outbound_foreign_keys != "None" else 0
            summary.append({
                "Table Name": table.table_name,
                "Primary Key": table.primary_key,
                "Column Count": len(table.columns),
                "Inbound FK Count": inbound_fk_count,
                "Outbound FK Count": outbound_fk_count
            })
        return summary

    def get_relationships_graph(self):
        G = nx.DiGraph()
        for table in self.tables.tables:
            G.add_node(table.table_name)
            if table.outbound_foreign_keys and table.outbound_foreign_keys != "None":
                for fk in table.outbound_foreign_keys:
                    G.add_edge(table.table_name, fk['referenced_table'], key=fk['column_name'])
        return G


class SQLProcedureGeneratorShell(cmd.Cmd):
    intro = "AI Matrix Engine SQL Procedure Generator Shell. Type help or ? to list commands.\n"
    prompt = f"{Fore.GREEN}[Matrix SQL Gen]{Style.RESET_ALL} "

    def __init__(self):
        super().__init__()
        self.generator = SQLProcedureGenerator()
        self.generator.load_cloud_schema()
        self.last_processed_table = None
        self.print_intro()

    def print_intro(self):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}AI Matrix Engine SQL Procedure Generator Shell")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}\n")

        num_tables = len(self.generator.tables.get_table_names())
        print(f"{Fore.GREEN}Number of Tables loaded: {Style.BRIGHT}{num_tables}")

        print(f"\n{Fore.MAGENTA}Available commands:")
        self.print_commands()

        print(f"\n{Fore.BLUE}Additional Information:")
        print(f"{Fore.BLUE}- Use 'help <command>' for more details on a specific command")
        print(f"{Fore.BLUE}- Use 'cls' to see the full menu again")
        print(f"{Fore.BLUE}- Tables are loaded from the cloud schema")
        print(f"{Fore.BLUE}- Processed table information is stored in memory\n")

    def print_commands(self):
        commands = [
            ("tables", "List all available tables with details"),
            ("view <table_name>", "View details of a specific table"),
            ("process <table_name>", "Process a specific table"),
            ("options <table_name> <column_name>", "View options for a specific column"),
            ("columns", "Show columns of the last processed table"),
            ("generate", "Generate SQL for the last processed table"),
            ("relationships", "Visualize relationships between tables"),
            ("schema", "Print the raw schema in a pretty format"),
            ("fetch <table_name> [limit]", "Fetch data from a table"),
            ("query <sql_query>", "Execute a custom SQL query"),
            ("last_result", "Print the result of the last query"),
            ("generate_redux", "Generate Redux ORM and a lot more from schema"),
            ("quit", "Exit the program"),
            ("help", "Show available commands"),
        ]
        for cmd, desc in commands:
            print(f"{Fore.YELLOW}  {cmd:<40}{Fore.WHITE}{desc}")

    def do_cls(self, arg):
        """Clear the screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
        self.print_intro()

    def do_schema(self, arg):
        """Print the raw schema in a pretty format"""
        self.generator.print_raw_schema()

    def do_process(self, arg):
        """Process a table: process_table <table_name>"""
        table_name = arg.strip()
        if not table_name:
            print(f"{Fore.RED}Please provide a table name.")
            return
        try:
            if table_name not in self.generator.tables.get_table_names():
                print(f"{Fore.RED}Error: Table '{table_name}' not found in schema.")
                return
            self.generator.process_table(table_name)
            self.last_processed_table = table_name
            print(f"{Fore.GREEN}Table '{table_name}' processed successfully.")
        except Exception as e:
            print(f"{Fore.RED}Error processing table: {e}")

    def cmdloop(self, intro=None):
        """Repeatedly issue a prompt, accept input, parse an initial prefix
        off the received input, and dispatch to action methods, passing them
        the remainder of the line as argument.
        """
        self.preloop()
        if self.use_rawinput and self.completekey:
            try:
                import readline
                self.old_completer = readline.get_completer()
                readline.set_completer(self.complete)
                readline.parse_and_bind(self.completekey + ": complete")
            except ImportError:
                pass
        try:
            if intro is not None:
                self.intro = intro
            if self.intro:
                self.stdout.write(str(self.intro) + "\n")
            stop = None
            while not stop:
                if self.cmdqueue:
                    line = self.cmdqueue.pop(0)
                else:
                    if self.use_rawinput:
                        try:
                            line = input(self.prompt)
                        except EOFError:
                            line = 'EOF'
                    else:
                        self.stdout.write(self.prompt)
                        self.stdout.flush()
                        line = self.stdin.readline()
                        if not len(line):
                            line = 'EOF'
                        else:
                            line = line.rstrip('\r\n')
                try:
                    line = self.precmd(line)
                    stop = self.onecmd(line)
                    stop = self.postcmd(stop, line)
                except Exception as e:
                    print(f"{Fore.RED}An error occurred: {str(e)}")
                    print(f"{Fore.YELLOW}Traceback:")
                    traceback.print_exc()
            self.postloop()
        finally:
            if self.use_rawinput and self.completekey:
                try:
                    import readline
                    readline.set_completer(self.old_completer)
                except ImportError:
                    pass

    def do_tables(self, arg):
        """List all available tables with details"""
        try:
            if self.generator.tables:
                summary = self.generator.get_tables_summary()
                print(f"\n{Fore.CYAN}Tables Summary:")
                print(tabulate(summary, headers="keys", tablefmt="fancy_grid", numalign="center"))
            else:
                print(f"{Fore.RED}No tables available. Make sure the schema is loaded.")
        except Exception as e:
            print(f"{Fore.RED}Error listing tables: {str(e)}")

    def do_view(self, arg):
        """View details of a specific table: view <table_name>"""
        table_name = arg.strip()
        if not table_name:
            print(f"{Fore.RED}Please provide a table name.")
            return
        try:
            details = self.generator.get_table_details(table_name)
            print(f"\n{Fore.CYAN}Table: {Fore.YELLOW}{table_name}")

            # Display column details
            print(f"\n{Fore.CYAN}Columns:")
            print(tabulate(details["columns"], headers="keys", tablefmt="grid"))

            # Display foreign key information
            print(f"\n{Fore.CYAN}Foreign Keys:")
            if details["inbound_foreign_keys"] and details["inbound_foreign_keys"] != "None":
                print(f"{Fore.WHITE}Inbound: {details['inbound_foreign_keys']}")
            else:
                print(f"{Fore.WHITE}No inbound foreign keys")

            if details["outbound_foreign_keys"] and details["outbound_foreign_keys"] != "None":
                print(f"{Fore.WHITE}Outbound: {details['outbound_foreign_keys']}")
            else:
                print(f"{Fore.WHITE}No outbound foreign keys")

            # Prompt for viewing options
            columns_with_options = [col["Column"] for col in details["columns"] if col["Has Options"] == "Yes"]
            if columns_with_options:
                print(f"\n{Fore.YELLOW}Columns with options: {', '.join(columns_with_options)}")
                print(f"{Fore.WHITE}Use 'options {table_name} <column_name>' to view options for a specific column.")
        except Exception as e:
            print(f"{Fore.RED}Error viewing table details: {e}")

    def do_relationships(self, arg):
        """Visualize relationships between tables"""
        try:
            G = self.generator.get_relationships_graph()
            if not G.edges():
                print(f"{Fore.YELLOW}No relationships found between tables.")
                return

            pos = nx.spring_layout(G)
            plt.figure(figsize=(12, 8))
            nx.draw(G, pos, with_labels=True, node_color='lightblue',
                    node_size=3000, font_size=8, font_weight='bold')

            edge_labels = nx.get_edge_attributes(G, 'key')
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)

            plt.title("Table Relationships", fontsize=16)

            img_buffer = BytesIO()
            plt.savefig(img_buffer, format='png')
            img_buffer.seek(0)

            img_str = base64.b64encode(img_buffer.getvalue()).decode()

            plt.close()

            print(f"{Fore.GREEN}Relationships graph generated.")
            print(f"{Fore.YELLOW}To view the graph, copy the following base64 string and decode it to a PNG image:")
            print(f"{Fore.WHITE}{img_str}")
        except Exception as e:
            print(f"{Fore.RED}Error generating relationships graph: {str(e)}")

    def do_options(self, arg):
        """View options for a specific column: options <table_name> <column_name>"""
        args = arg.split()
        if len(args) != 2:
            print(f"{Fore.RED}Please provide both table name and column name.")
            return
        table_name, column_name = args
        try:
            table = self.generator.tables.find_table_by_name(table_name)
            column = next((col for col in table.columns if col.column_name == column_name), None)
            if column is None:
                print(f"{Fore.RED}Column '{column_name}' not found in table '{table_name}'.")
                return
            if column.options and column.options != "None":
                print(f"\n{Fore.CYAN}Options for column '{column_name}' in table '{table_name}':")
                for option in column.options:
                    print(f"{Fore.WHITE}- {option}")
            else:
                print(f"{Fore.YELLOW}No options available for column '{column_name}' in table '{table_name}'.")
        except Exception as e:
            print(f"{Fore.RED}Error viewing column options: {e}")

    def do_columns(self, arg):
        """Show columns for a processed table"""
        if not self.generator.columns_list:
            print(f"{Fore.RED}No table has been processed yet. Use 'process_table' first.")
            return
        print(f"{Fore.CYAN}Processed columns:")
        for column in self.generator.columns_list:
            print(f"{Fore.WHITE}- {column}")

    def do_fetch(self, arg):
        """Fetch data from a table: fetch <table_name> [limit]"""
        args = arg.split()
        if not args:
            print(f"{Fore.RED}Please provide a table name.")
            return
        table_name = args[0]
        limit = int(args[1]) if len(args) > 1 else 10
        data = self.generator.fetch_table_data(table_name, limit)
        if data:
            print(f"{Fore.GREEN}Fetched {len(data)} rows from {table_name}:")
            print(tabulate(data, headers="keys", tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}No data fetched.")

    def do_query(self, arg):
        """Execute a custom SQL query"""
        if not arg:
            print(f"{Fore.RED}Please provide a SQL query.")
            return
        result = self.generator.execute_custom_query(arg)
        if result:
            print(f"{Fore.GREEN}Query executed successfully:")
            print(tabulate(result, headers="keys", tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}No results returned.")

    def do_last_result(self, arg):
        """Print the result of the last query"""
        if self.generator.last_query_result:
            print(f"{Fore.GREEN}Last query result:")
            print(tabulate(self.generator.last_query_result, headers="keys", tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}No previous query results available.")

    def do_custom_procedures(self, arg):
        """Print the result of the last query"""
        if self.generator.get_procedure_details():
            print(f"{Fore.GREEN}Last query result:")
            print(tabulate(self.generator.last_query_result, headers="keys", tablefmt="grid"))
        else:
            print(f"{Fore.YELLOW}No previous query results available.")

    def do_generate_redux(self, arg):
        geterate_typescript_redux()

    def do_generate_sql(self, arg):
        """Generate SQL procedure for the last processed table"""
        if not self.last_processed_table:
            print(f"{Fore.RED}No table has been processed yet. Use 'process_table' first.")
            return
        sql = self.generator.generate_sql_procedure(self.last_processed_table)
        print(f"{Fore.YELLOW}Generated SQL procedure for table '{self.last_processed_table}':")
        print(f"{Fore.WHITE}{sql}")

    def do_quit(self, arg):
        """Exit the program"""
        print(f"\n{Fore.YELLOW}Thank you for using SQL Procedure Generator. Goodbye!")
        return True

    def do_EOF(self, arg):
        """Exit on EOF (Ctrl+D)"""
        print()
        return self.do_quit(arg)


if __name__ == "__main__":
    intro = "You know Armani was here..."
    SQLProcedureGeneratorShell().cmdloop(intro)
