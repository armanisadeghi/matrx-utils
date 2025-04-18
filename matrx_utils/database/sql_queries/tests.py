import os
from matrx_utils.common import vcprint
from matrx_utils.database.sql_queries.executor import execute_standard_query, list_available_queries, get_query_details


def get_latest_compiled_recipe_version(recipe_id: str):
    """Get the latest compiled recipe version for a given recipe ID"""
    results = execute_standard_query("get_latest_compiled_recipe", {"recipe_id": recipe_id})

    if not results:
        return None

    result_dict = dict(results[0])
    compiled_recipe = result_dict.pop("compiled_recipe", {})
    return {**result_dict, **compiled_recipe, "recipe_type": "compiled"}



if __name__ == "__main__":
    os.system("cls")
    # Example: List all available queries
    all_queries = list_available_queries()
    vcprint(all_queries, title="Available Queries", color="blue")

    # Example: Get details about a specific query
    details = get_query_details("get_latest_compiled_recipe")
    vcprint(details, title="Query Details", color="green")

    # Example: Execute a query
    results = execute_standard_query("get_latest_compiled_recipe", {"recipe_id": "15a11c3d-f037-4f2b-9e22-fe88e68d75e1"})
    vcprint(results, title="Results", color="green")
