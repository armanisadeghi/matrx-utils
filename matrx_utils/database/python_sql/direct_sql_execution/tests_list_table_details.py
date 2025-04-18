import os
import sys
from typing import Dict, Any
import json

from matrx_utils.database.python_sql.direct_sql_execution.ai_sql_executor import create_ai_query_tool


def test_get_full_spectrum_position_schema():
    """
    Test to get the schema of the full_spectrum_position table.
    """
    database_name = "supabase_automation_matrix"

    query_tool = create_ai_query_tool(database_name)
    print("\n=== TEST: Getting Schema for full_spectrum_position Table ===\n")

    # First, let's list the available schemas to see what we have
    print("Available schemas:")
    schemas = query_tool.list_schemas()
    print(json.dumps(schemas, indent=2))
    print("\n" + "-" * 60 + "\n")

    # Try to find the table in any schema
    table_schema = query_tool.get_table_schema("full_spectrum_positions")

    if not table_schema:
        # If not found, let's list the available tables in various schemas
        print("Table not found. Listing available tables in common schemas:")
        common_schemas = ['public', 'auth', 'supabase_functions']

        for schema in common_schemas:
            tables = query_tool.list_tables(schema)
            print(f"\nTables in {schema} schema:")
            print(json.dumps(tables, indent=2))
    else:
        print("Table Schema for full_spectrum_position:")
        print(json.dumps(table_schema, indent=2))

    print("\n=== TEST COMPLETE ===\n")

if __name__ == "__main__":
    os.system("cls")
    test_get_full_spectrum_position_schema()
