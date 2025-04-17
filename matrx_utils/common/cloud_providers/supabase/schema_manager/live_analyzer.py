import cmd
import os
import traceback
from colorama import Fore, Style
from tabulate import tabulate
import networkx as nx
import matplotlib.pyplot as plt
from io import BytesIO
import base64

from common.supabase.schema_manager.schema_manager import SchemaManager


class SchemaAnalyzer(cmd.Cmd):
    intro = "Schema Analyzer Shell. Type help or ? to list commands.\n"
    prompt = f"{Fore.GREEN}[Schema Analyzer]{Style.RESET_ALL} "

    def __init__(self, schema_manager):
        super().__init__()
        self.schema_manager = schema_manager
        self.print_intro()

    def print_intro(self):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'=' * 60}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}Schema Analyzer Shell")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 60}\n")

        num_tables = len(self.schema_manager.tables)
        print(f"{Fore.GREEN}Number of Tables loaded: {Style.BRIGHT}{num_tables}")

        print(f"\n{Fore.MAGENTA}Available commands:")
        self.print_commands()

        print(f"\n{Fore.BLUE}Additional Information:")
        print(f"{Fore.BLUE}- Use 'help <command>' for more details on a specific command")
        print(f"{Fore.BLUE}- Use 'cls' to see the full menu again\n")

    def print_commands(self):
        commands = [
            ("load", "Load the schema"),
            ("initialize", "Initialize the schema"),
            ("schema", "Print the raw schema in a pretty format"),
            ("tables", "List all available tables with details"),
            ("view <table_name>", "View details of a specific table"),
            ("view_column <table_name> <column_name>", "View details of a specific column"),
            ("options <table_name> <column_name>", "View options for a specific column"),
            ("relationships", "Visualize relationships between tables"),
            ("cls", "Clear the screen"),
            ("exit", "Exit the analyzer"),
            ("help", "Show available commands"),
        ]
        for cmd, desc in commands:
            print(f"{Fore.YELLOW}  {cmd:<30}{Fore.WHITE}{desc}")

    def do_schema(self, arg):
        """Print the raw schema in a pretty format"""
        schema = self.schema_manager.get_raw_schema()
        if schema:
            print(schema)
        else:
            print(f"{Fore.RED}Schema not loaded. Use 'load' to load the schema.")

    def do_load(self, arg):
        """Load the schema"""
        self.schema_manager.load_schema()

    def do_initialize(self, arg):
        """Initialize the schema"""
        self.schema_manager.initialize()
    def do_tables(self, arg):
        """List all available tables with details"""
        try:
            if self.schema_manager.tables:
                summary = self.schema_manager.get_tables_summary()
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
            details = self.schema_manager.get_table_details(table_name)
            if not details:
                print(f"{Fore.RED}Table '{table_name}' not found.")
                return

            print(f"\n{Fore.CYAN}Table: {Fore.YELLOW}{table_name}")

            # Display column details
            print(f"\n{Fore.CYAN}Columns:")
            print(tabulate(details["columns"], headers="keys", tablefmt="grid"))

            # Display foreign key information
            print(f"\n{Fore.CYAN}Foreign Keys:")
            if details["inbound_foreign_keys"]:
                print(f"{Fore.WHITE}Inbound: {details['inbound_foreign_keys']}")
            else:
                print(f"{Fore.WHITE}No inbound foreign keys")

            if details["outbound_foreign_keys"]:
                print(f"{Fore.WHITE}Outbound: {details['outbound_foreign_keys']}")
            else:
                print(f"{Fore.WHITE}No outbound foreign keys")

            # Prompt for viewing options
            columns_with_options = [col["Column"] for col in details["columns"] if col["Has Options"] == "Yes"]
            if columns_with_options:
                print(f"\n{Fore.YELLOW}Columns with options: {', '.join(columns_with_options)}")
                print(f"{Fore.WHITE}Use 'view_column {table_name} <column_name>' to view options for a specific column.")
        except Exception as e:
            print(f"{Fore.RED}Error viewing table details: {e}")

    def do_view_column(self, arg):
        """View details of a specific column: view_column <table_name> <column_name>"""
        args = arg.split()
        if len(args) != 2:
            print(f"{Fore.RED}Please provide both table name and column name.")
            return
        table_name, column_name = args
        try:
            column_details = self.schema_manager.get_column_details(table_name, column_name)
            if not column_details:
                print(f"{Fore.RED}Column '{column_name}' not found in table '{table_name}'.")
                return

            print(f"\n{Fore.CYAN}Column: {Fore.YELLOW}{column_name} in Table: {Fore.YELLOW}{table_name}")
            print(tabulate(column_details.items(), headers=["Attribute", "Value"], tablefmt="grid"))
        except Exception as e:
            print(f"{Fore.RED}Error viewing column details: {e}")

    def do_options(self, arg):
        """View options for a specific column: options <table_name> <column_name>"""
        args = arg.split()
        if len(args) != 2:
            print(f"{Fore.RED}Please provide both table name and column name.")
            return
        table_name, column_name = args
        try:
            column_details = self.schema_manager.get_column_details(table_name, column_name)
            if not column_details:
                print(f"{Fore.RED}Column '{column_name}' not found in table '{table_name}'.")
                return
            if column_details['options']:
                print(f"\n{Fore.CYAN}Options for column '{column_name}' in table '{table_name}':")
                for option in column_details['options']:
                    print(f"{Fore.WHITE}- {option}")
            else:
                print(f"{Fore.YELLOW}No options available for column '{column_name}' in table '{table_name}'.")
        except Exception as e:
            print(f"{Fore.RED}Error viewing column options: {e}")

    def do_relationships(self, arg):
        """Visualize relationships between tables"""
        try:
            G = self.schema_manager.get_relationships_graph()
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

    def do_exit(self, arg):
        """Exit the analyzer"""
        print("Exiting")
        return True

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
                self.stdout.write(str(self.intro)+"\n")
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

if __name__ == '__main__':
    schema_manager = SchemaManager()
    analyzer = SchemaAnalyzer(schema_manager)
    analyzer.cmdloop()
