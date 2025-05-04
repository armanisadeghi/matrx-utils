# matrx_utils\database\python_sql\direct_sql_execution\ai_sql_executor.py
import os
from typing import List, Dict, Any, Optional, Union, Tuple
from psycopg2.extras import RealDictCursor
from database.client.postgres_connection import execute_sql_query

class AIQueryTool:
    """
    A tool for AI models to execute SQL queries safely and get schema information.
    """

    def __init__(self, database_project: str):
        """
        Initialize the AI Query Tool with a specific database project.

        Args:
            database_project: The name of the database project to connect to
        """
        self.database_project = database_project

    def get_table_schema(self, table_name: str, schema_name: str = None) -> List[Dict[str, Any]]:
        """
        Get the schema information for a specific table.

        Args:
            table_name: The name of the table to inspect
            schema_name: Optional schema name (if not provided, will search in all schemas)

        Returns:
            A list of dictionaries containing column information
        """
        # First check if the table exists
        check_query = """
        SELECT
            table_schema,
            table_name
        FROM
            information_schema.tables
        WHERE
            table_name = %s
        """

        params = [table_name]
        if schema_name:
            check_query += " AND table_schema = %s"
            params.append(schema_name)

        table_exists = execute_sql_query(
            query=check_query,
            params=tuple(params),
            database_project=self.database_project
        )

        if not table_exists:
            print(f"Table {table_name} not found in the database.")
            return []

        # If table exists, get its schema using the first found schema
        found_schema = table_exists[0]['table_schema']
        print(f"Found table in schema: {found_schema}")

        query = """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM
            information_schema.columns
        WHERE
            table_name = %s
            AND table_schema = %s
        ORDER BY
            ordinal_position;
        """

        return execute_sql_query(
            query=query,
            params=(table_name, found_schema),
            database_project=self.database_project
        )

    def list_tables(self, schema_name: str = 'public') -> List[Dict[str, str]]:
        """
        List all tables in the specified schema.

        Args:
            schema_name: The schema to list tables from (default: 'public')

        Returns:
            A list of dictionaries containing table names
        """
        query = """
        SELECT
            table_name
        FROM
            information_schema.tables
        WHERE
            table_schema = %s
        ORDER BY
            table_name;
        """

        return execute_sql_query(
            query=query,
            params=(schema_name,),
            database_project=self.database_project
        )

    def list_schemas(self) -> List[Dict[str, str]]:
        """
        List all schemas in the database.

        Returns:
            A list of dictionaries containing schema names
        """
        query = """
        SELECT
            schema_name
        FROM
            information_schema.schemata
        WHERE
            schema_name NOT LIKE 'pg_%'
            AND schema_name != 'information_schema'
        ORDER BY
            schema_name;
        """

        return execute_sql_query(
            query=query,
            params=None,
            database_project=self.database_project
        )


    def execute_query(self, query: str, params: Optional[Union[Dict[str, Any], Tuple, List]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return the results.

        Args:
            query: The SQL query to execute
            params: Parameters to use in the query (optional)

        Returns:
            Results as a list of dictionaries
        """
        return execute_sql_query(
            query=query,
            params=params,
            database_project=self.database_project
        )

    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get sample data from a table.

        Args:
            table_name: The name of the table to sample
            limit: Maximum number of rows to return

        Returns:
            Sample data as a list of dictionaries
        """
        query = f"""
        SELECT * FROM {table_name} LIMIT %s;
        """

        return execute_sql_query(
            query=query,
            params=(limit,),
            database_project=self.database_project
        )

    def get_table_relationships(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get foreign key relationships for a table.

        Args:
            table_name: The name of the table to inspect

        Returns:
            A list of dictionaries containing relationship information
        """
        query = """
        SELECT
            tc.constraint_name,
            tc.table_name AS table_name,
            kcu.column_name,
            ccu.table_name AS referenced_table_name,
            ccu.column_name AS referenced_column_name
        FROM
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
        WHERE
            tc.constraint_type = 'FOREIGN KEY'
            AND (tc.table_name = %s OR ccu.table_name = %s);
        """

        return execute_sql_query(
            query=query,
            params=(table_name, table_name),
            database_project=self.database_project
        )

    def count_records(self, table_name: str, where_clause: Optional[str] = None,
                      params: Optional[Union[Dict[str, Any], Tuple, List]] = None) -> int:
        """
        Count records in a table, optionally with a where clause.

        Args:
            table_name: The name of the table to count records from
            where_clause: Optional WHERE clause (without the 'WHERE' keyword)
            params: Parameters to use in the where clause

        Returns:
            The count of records
        """
        if where_clause:
            query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {where_clause};"
        else:
            query = f"SELECT COUNT(*) as count FROM {table_name};"

        result = execute_sql_query(
            query=query,
            params=params,
            database_project=self.database_project
        )

        return result[0]['count'] if result else 0

# Factory function to create a query tool for a specific database
def create_ai_query_tool(database_project: str) -> AIQueryTool:
    """
    Create an AI Query Tool for a specific database project.

    Args:
        database_project: The name of the database project to connect to

    Returns:
        An initialized AIQueryTool instance
    """
    return AIQueryTool(database_project)
