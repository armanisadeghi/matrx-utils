# database/sql_queries/queries.py
from typing import Dict, List, Union, Optional, Any, TypedDict

class QueryParam(TypedDict):
    """Type definition for a query parameter"""
    name: str
    required: bool
    description: str
    type: str  # 'string', 'integer', 'float', 'boolean', 'uuid', etc.
    default: Optional[Any]  # Default value if optional

class SQLQuery(TypedDict):
    """Type definition for a SQL query"""
    query: str
    params: List[QueryParam]
    database: str
    description: str
    example: Optional[str]  # Example usage
    executor_type: Optional[str]  # 'standard', 'transaction', or 'batch'


# Example query definition
LATEST_COMPILED_RECIPE_QUERY = """
SELECT cr.*
FROM public.compiled_recipe cr
JOIN public.recipe r ON r.id = cr.recipe_id
WHERE cr.recipe_id = %(recipe_id)s
AND cr.version = r.version
"""

GET_LATEST_COMPILED_RECIPE: SQLQuery = {
    "query": LATEST_COMPILED_RECIPE_QUERY,
    "params": [
        {
            "name": "recipe_id",
            "required": True,
            "description": "UUID of the recipe",
            "type": "uuid",
            "default": None
        }
    ],
    "database": "supabase_automation_matrix",
    "description": "Get the latest compiled recipe version for a given recipe ID",
    "example": "execute_standard_query('get_latest_compiled_recipe', {'recipe_id': '15a11c3d-f037-4f2b-9e22-fe88e68d75e1'})",
    "executor_type": "standard"
}

# Add another example query with optional parameters
GET_RECIPES_BY_STATUS_QUERY = """
SELECT r.*
FROM public.recipe r
WHERE (%(status)s IS NULL OR r.status = %(status)s)
ORDER BY r.created_at DESC
LIMIT %(limit)s
"""

GET_RECIPES_BY_STATUS: SQLQuery = {
    "query": GET_RECIPES_BY_STATUS_QUERY,
    "params": [
        {
            "name": "status",
            "required": False,
            "description": "Filter recipes by status (active, archived, draft)",
            "type": "string",
            "default": None
        },
        {
            "name": "limit",
            "required": False,
            "description": "Maximum number of recipes to return",
            "type": "integer",
            "default": 100
        }
    ],
    "database": "supabase_automation_matrix",
    "description": "Get recipes filtered by status, with optional pagination",
    "example": "execute_standard_query('get_recipes_by_status', {'status': 'active', 'limit': 50})",
    "executor_type": "standard"
}


GET_LATEST_SCRAPED_PAGES_QUERY = """
WITH latest_pages AS (
    SELECT DISTINCT ON (page_name) *
    FROM public.scrape_parsed_page
    WHERE page_name = ANY(%(page_names)s)
    AND (expires_at IS NULL OR expires_at > NOW())
    AND scraped_at IS NOT NULL
    ORDER BY page_name, scraped_at DESC
)
SELECT * FROM latest_pages
ORDER BY scraped_at DESC
"""

GET_LATEST_SCRAPED_PAGES: SQLQuery = {
    "query": GET_LATEST_SCRAPED_PAGES_QUERY,
    "params": [
        {
            "name": "page_names",
            "required": True,
            "description": "List of page names to retrieve",
            "type": "string[]",
            "default": None
        }
    ],
    "database": "supabase_automation_matrix",
    "description": "Get the latest non-expired scraped pages for a list of page names, sorted by scraped_at descending",
    "example": "execute_standard_query('get_latest_scraped_pages', {'page_names': ['home-page', 'about-page', 'contact-page']})",
    "executor_type": "standard"
}


# Registry of all available queries
SQL_QUERIES: Dict[str, SQLQuery] = {
    "get_latest_compiled_recipe": GET_LATEST_COMPILED_RECIPE,
    "get_recipes_by_status": GET_RECIPES_BY_STATUS,
    "get_latest_scraped_pages": GET_LATEST_SCRAPED_PAGES,
    # Add more queries here
}
