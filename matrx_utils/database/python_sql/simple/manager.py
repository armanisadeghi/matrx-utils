# matrx_utils\database\python_sql\simple\manager.py
from common import vcprint
from database.python_sql.db_objects import get_objects
from database.python_sql.table_relationships import get_table_relationships


class SchemaManager:
    def __init__(self, database="postgres", schema="public"):
        self.database = database
        self.schema = schema
        self.objects = {}
        self.table_relationships = {}
        self.tables = {}
        self.views = {}
        self.columns = {}
        self.initialized = False

    def initialize(self):
        """Orchestrates the initialization of the SchemaManager."""
        self.load_objects()
        self.load_table_relationships()
        self.set_tables()
        self.set_views()
        self.set_columns()
        self.initialized = True

    def load_objects(self):
        """Loads all database objects (tables and views) into the manager."""
        object_data = get_objects(self.schema)
        # Store all objects in a dictionary for quick access
        self.objects = {obj["name"]: obj for obj in object_data}

    def load_table_relationships(self):
        """Loads table relationships like foreign keys and references."""
        relationship_data = get_table_relationships(self.schema)
        # Structure table relationships into a dictionary keyed by table name
        self.table_relationships = {rel["table_name"]: rel for rel in relationship_data}

    def set_tables(self):
        """Populates the tables dictionary with table-specific details and relationships."""
        # Filter out objects that are tables
        self.tables = {name: obj for name, obj in self.objects.items() if obj["type"] == "table"}

        # Incorporate relationship information into each table
        for table_name, table in self.tables.items():
            relationships = self.table_relationships.get(table_name, {})
            table["foreign_keys"] = relationships.get("foreign_keys", {})
            table["referenced_by"] = relationships.get("referenced_by", {})

    def set_views(self):
        """Populates the views dictionary with view-specific details."""
        # Filter out objects that are views
        self.views = {name: obj for name, obj in self.objects.items() if obj["type"] == "view"}

    def set_columns(self):
        """Populates the columns dictionary with column details for each table and view."""
        self.columns = {}
        # Iterate through tables and views to collect column information
        for name, obj in {**self.tables, **self.views}.items():
            # Columns are already in the 'columns' key of each object
            self.columns[name] = obj.get("columns", [])

    def get_table(self, table_name):
        """Retrieves details about a specific table."""
        return self.tables.get(table_name)

    def get_view(self, view_name):
        """Retrieves details about a specific view."""
        return self.views.get(view_name)

    def get_column(self, table_name, column_name):
        """Retrieves details about a specific column in a table or view."""
        if table_name in self.columns:
            for column in self.columns[table_name]:
                if column["name"] == column_name:
                    return column
        return None

    def get_foreign_keys(self, table_name):
        """Returns the foreign keys for a given table."""
        table = self.get_table(table_name)
        if table:
            return table.get("foreign_keys", {})
        return {}

    def get_references(self, table_name):
        """Returns the tables that reference a given table."""
        table = self.get_table(table_name)
        if table:
            return table.get("referenced_by", {})
        return {}


# Example usage
if __name__ == "__main__":
    schema_manager = SchemaManager(schema="public")
    schema_manager.initialize()

    # Access tables, views, columns, and relationships as needed
    vcprint(schema_manager.tables, title="Tables", pretty=True, color="blue")
    vcprint(schema_manager.views, title="Views", pretty=True, color="green")
    vcprint(schema_manager.columns, title="Columns", pretty=True, color="magenta")

    # Example: Get foreign keys for a specific table
    vcprint(
        schema_manager.get_foreign_keys("flashcard_history"),
        title="Foreign Keys for Flashcard History",
        pretty=True,
        color="cyan",
    )

    # Example: Get references to a specific table
    vcprint(
        schema_manager.get_references("flashcard_sets"),
        title="Tables Referencing Flashcard Sets",
        pretty=True,
        color="yellow",
    )
