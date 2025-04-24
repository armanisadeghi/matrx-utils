# Get the base data first
from database.python_sql.complete_relationship_analysis_pandas import (
    get_comprehensive_analysis,
    ColumnBase,
    TableBase,
)
import json

from common.utils.file_handlers.code_hanlder import CodeHandler
from common.utils.data_handlers.data_transformer import DataTransformer
from common import vcprint
from database.python_sql.db_objects import get_db_objects
from database.python_sql.table_relationships import get_table_relationships

verbose = True

utils = DataTransformer()


def get_default_component_props():
    return {
        "subComponent": "default",
        "variant": "default",
        "section": "default",
        "placeholder": "default",
        "size": "default",
        "textSize": "default",
        "textColor": "default",
        "rows": "default",
        "animation": "default",
        "fullWidthValue": "default",
        "fullWidth": "default",
        "disabled": "default",
        "className": "default",
        "type": "default",
        "onChange": "default",
        "onBlur": "default",
        "formatString": "default",
        "min": "default",
        "max": "default",
        "step": "default",
        "numberType": "default",
        "options": "default",
    }


analysis_results = get_comprehensive_analysis(schema="public", database_project="supabase_automation_matrix")


# Now your custom classes can extend and use this data:
class Column(ColumnBase):
    def __init__(self, base_column: ColumnBase):
        # Copy all attributes from the base column
        self.__dict__.update(base_column.__dict__)

        # Add your custom initialization
        self.utils = utils
        self.initialize_code_generation()
        # ... rest of your custom initialization


class Table(TableBase):
    def __init__(self, base_table: TableBase):
        # Copy all attributes from the base table
        self.__dict__.update(base_table.__dict__)

        # Convert the base columns to your custom Column class
        self.columns = {name: Column(col) for name, col in base_table.columns.items()}

        # Add your custom initialization
        self.utils = utils
        self.identify_display_column()
        # ... rest of your custom initialization


# Update SchemaManager to use the analysis results:
class SchemaManager:
    def __init__(
        self,
        database="postgres",
        schema="public",
        database_project="supabase_automation_matrix",
    ):
        self.utils = utils
        self.database = database
        self.database_project = database_project

        # Get the base analysis first
        self.base_analysis = get_comprehensive_analysis(schema=schema, database_project=database_project)

        # Create your schema with the analyzed data
        self.schema = Schema(name=schema, database_project=database_project)
        self.initialized = False
        self.verbose = True
        self.debug = False

    def initialize(self):
        """Orchestrates the initialization of the SchemaManager."""
        self.load_objects()
        self.load_table_relationships()
        self.initialized = True

    def load_objects(self):
        """Loads all database objects using the base analysis"""
        for table_name, base_table in self.base_analysis.items():
            table = Table(base_table)
            self.schema.add_table(table)
