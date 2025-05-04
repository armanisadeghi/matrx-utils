# matrx_utils\sql_queries\executor.py
import os
from typing import Dict, Any, List, Optional
from common.utils.fancy_prints import vcprint
from database.client.postgres_connection import execute_sql_query as db_execute_query
from database.client.postgres_connection import execute_transaction_query as db_execute_transaction_query
from database.client.postgres_connection import execute_batch_query as db_execute_batch_query
from database.sql_queries.queries import SQL_QUERIES as ORIGINAL_SQL_QUERIES
from user_data.user_tables_queries import USER_TABLE_QUERIES

MERGED_SQL_QUERIES: Dict[str, Any] = {
    **ORIGINAL_SQL_QUERIES,
    **USER_TABLE_QUERIES,
    # **OTHER_MODULE_QUERIES, # List others here as they are developed and don't fit one of the current categories
}

SQL_QUERIES = MERGED_SQL_QUERIES

def validate_params(query_name: str, params: Dict[str, Any]):
    """
    Validate parameters and return a clean parameter dictionary with defaults applied.
    Instead of raising errors for non-critical issues, this attempts to fix or adapt the input.
    """
    query_data = SQL_QUERIES[query_name]
    cleaned_params = {}
    # Apply default values for all parameters
    for param_def in query_data["params"]:
        param_name = param_def["name"]
        # If parameter is provided, use it
        if param_name in params:
            param_value = params[param_name]
            # Basic type conversion attempts when reasonable
            if param_def["type"] == "uuid" and not isinstance(param_value, str) and param_value is not None:
                try:
                    # Try to convert to string if possible
                    param_value = str(param_value)
                except:
                    # If we can't convert and it's required, we have to raise an error
                    if param_def["required"]:
                        raise TypeError(f"Parameter '{param_name}' must be convertible to a string for UUID")
                    else:
                        # Use default for optional params if conversion fails
                        param_value = param_def["default"]
            cleaned_params[param_name] = param_value
        # If parameter is not provided but required, raise error
        elif param_def["required"]:
            raise ValueError(f"Missing required parameter '{param_name}' for query '{query_name}'")
        # If parameter is not provided and optional, use default
        elif param_def["default"] is not None:
            cleaned_params[param_name] = param_def["default"]
    return cleaned_params


def execute_query(query_name: str, params: Optional[Dict[str, Any]] = None, batch_params: Optional[List[Dict[str, Any]]] = None, batch_size: int = 50):
    """
    Central function to execute a query using the appropriate executor based on its type.

    Args:
        query_name: Name of the query in SQL_QUERIES
        params: Parameters for standard/transaction execution (single row)
        batch_params: Parameters for batch execution (multiple rows)
        batch_size: Number of rows to process in each batch (for batch execution)
    """
    # Check if query exists
    if query_name not in SQL_QUERIES:
        available_queries = ", ".join(list_available_queries())
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")

    query_data = SQL_QUERIES[query_name]

    # Determine which executor to use
    executor_type = query_data.get("executor_type", "standard")

    # If batch_params is provided, use batch execution regardless of executor_type
    if batch_params and len(batch_params) > 0:
        return execute_batch_query(query_name, batch_params, batch_size)

    # Otherwise, use the specified executor type
    params = params or {}
    cleaned_params = validate_params(query_name, params)

    if executor_type == "transaction":
        return db_execute_transaction_query(
            query_data["query"],
            cleaned_params,
            query_data["database"]
        )
    elif executor_type == "batch":
        # If batch is specified but no batch_params, wrap the single params in a list
        return execute_batch_query(query_name, [cleaned_params], batch_size)
    else:  # Default to standard
        return db_execute_query(
            query_data["query"],
            cleaned_params,
            query_data["database"]
        )



# ===== Kept for backwards compatibility but all current definitions should be upated and this should be removed - # TODO: Jatin
def execute_standard_query(query_name: str, params: Optional[Dict[str, Any]] = None):
    """Execute a predefined SQL query by name with the given parameters."""
    params = params or {}
    # Check if query exists
    if query_name not in SQL_QUERIES:
        available_queries = ", ".join(list_available_queries())
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")
    query_data = SQL_QUERIES[query_name]
    # Clean and validate parameters
    cleaned_params = validate_params(query_name, params)
    # Execute the query
    return db_execute_query(
        query_data["query"],
        cleaned_params,
        query_data["database"]
    )

# ===== Kept for backwards compatibility but all current definitions should be upated and this should be removed - # TODO: Arman
def execute_transaction_query(query_name: str, params: Optional[Dict[str, Any]] = None):
    """Execute a predefined SQL query that requires transaction handling."""
    params = params or {}
    # Check if query exists
    if query_name not in SQL_QUERIES:
        available_queries = ", ".join(list_available_queries())
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")

    query_data = SQL_QUERIES[query_name]
    # Clean and validate parameters
    cleaned_params = validate_params(query_name, params)
    # Execute the query with transaction handling
    return db_execute_transaction_query(
        query_data["query"],
        cleaned_params,
        query_data["database"]
    )

def execute_batch_query(query_name: str, batch_params: List[Dict[str, Any]], batch_size: int = 50):
    """
    Execute a predefined SQL query using batch processing.

    Args:
        query_name: Name of the query in SQL_QUERIES
        batch_params: List of parameter dictionaries, one per row
        batch_size: Number of rows to process in each batch

    Returns:
        Combined results from all batches
    """
    # Check if query exists
    if query_name not in SQL_QUERIES:
        available_queries = ", ".join(list_available_queries())
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")

    query_data = SQL_QUERIES[query_name]

    # Validate each set of parameters in the batch
    validated_params = []
    for params in batch_params:
        validated_params.append(validate_params(query_name, params))

    # Execute the batch query
    return db_execute_batch_query(
        query_data["query"],
        validated_params,
        batch_size,
        query_data["database"]
    )

# Documentation-related functions
def list_available_queries():
    """Return a list of all available query names with short descriptions"""
    return [
        {
            "name": name,
            "description": SQL_QUERIES[name]["description"],
            "database": SQL_QUERIES[name]["database"]
        }
        for name in sorted(SQL_QUERIES.keys())
    ]

def get_query_details(query_name: str):
    """Get detailed information about a specific query"""
    if query_name not in SQL_QUERIES:
        available_queries = ", ".join([q["name"] for q in list_available_queries()])
        raise ValueError(f"Query '{query_name}' not found. Available queries: {available_queries}")
    query_data = SQL_QUERIES[query_name]
    # Return a more user-friendly representation
    return {
        "name": query_name,
        "description": query_data["description"],
        "parameters": [
            {
                "name": p["name"],
                "required": p["required"],
                "type": p["type"],
                "description": p["description"],
                "default": p["default"] if not p["required"] else None
            } for p in query_data["params"]
        ],
        "database": query_data["database"],
        "example": query_data.get("example"),
        "query": query_data["query"],  # Include actual SQL for reference
    }

def generate_documentation():
    """Generate markdown documentation for all available queries"""
    docs = ["# SQL Query Documentation\n\n"]
    for query_name in sorted(SQL_QUERIES.keys()):
        query_data = SQL_QUERIES[query_name]
        docs.append(f"## {query_name}\n")
        docs.append(f"{query_data['description']}\n")
        docs.append("### Parameters\n")
        for param in query_data["params"]:
            required = "Required" if param["required"] else f"Optional (default: {param['default']})"
            docs.append(f"- **{param['name']}** ({param['type']}): {param['description']} - {required}\n")
        docs.append(f"\n### Database\n{query_data['database']}\n")
        if query_data.get("example"):
            docs.append(f"\n### Example\n```python\n{query_data['example']}\n```\n")
        docs.append("\n### SQL Query\n```sql\n" + query_data["query"] + "\n```\n\n")
    return "".join(docs)



def display_help():
    """Display help information about the query system"""
    help_text = """
    SQL Query System
    ----------------
    Available Functions:
    - execute_standard_query(query_name, params)
      Execute a predefined SQL query with parameters
    - list_available_queries()
      Get a list of all available queries with descriptions
    - get_query_details(query_name)
      Get detailed information about a specific query
    - generate_documentation()
      Generate markdown documentation for all queries
    - display_help()
      Show this help message
    Example:
    result = execute_standard_query("get_latest_compiled_recipe", {"recipe_id": "15a11c3d-f037-4f2b-9e22-fe88e68d75e1"})
    """
    return help_text
