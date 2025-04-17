import os
from urllib.parse import urlparse

import psycopg2
from supabase import create_client, Client
from dotenv import load_dotenv

from common import pretty_print, vcprint

load_dotenv()


def get_supabase_client():
    url = os.environ.get("SUPABASE_MATRIX_URL")
    key = os.environ.get("SUPABASE_MATRIX_KEY")
    supabase: Client = create_client(url, key)
    return supabase


def get_db_connection():
    """Establish a direct connection to the database using psycopg2."""
    db_url = os.environ.get("SUPABASE_DATABASE_URL")
    result = urlparse(db_url)

    # Create a dictionary with connection parameters
    connection_params = {
        "dbname": "postgres",  # Remove leading '/' from the path
        "user": "postgres.txzxabzwovsujtloxrus",
        "password": "Aa26261385$",
        "host": "aws-0-us-west-1.pooler.supabase.com",
        "port": "6543",
    }

    conn = psycopg2.connect(**connection_params)
    return conn


def get_all_recipes():
    supabase = get_supabase_client()
    response = supabase.table("recipe").select("*").execute()
    return response


def get_recipe_by_id(recipe_id):
    supabase = get_supabase_client()
    response = supabase.table("recipe").select("*").eq("id", recipe_id).execute()
    return response


def create_recipe(recipe_data):
    supabase = get_supabase_client()
    response = supabase.table("recipe").insert(recipe_data).execute()
    return response


def update_recipe(recipe_id, recipe_data):
    supabase = get_supabase_client()
    response = supabase.table("recipe").update(recipe_data).eq("id", recipe_id).execute()
    return response


def delete_recipe(recipe_id):
    supabase = get_supabase_client()
    response = supabase.table("recipe").delete().eq("id", recipe_id).execute()
    return response


def fetch_paginated(table_name, page, page_size):
    supabase = get_supabase_client()
    response = supabase.rpc("fetch_paginated", {
        "p_table_name": table_name,
        "p_page": page,
        "p_page_size": page_size
    }).execute()
    return response


def fetch_filtered(table_name, filters):
    supabase = get_supabase_client()
    # Correct parameter names as per the stored procedure definition
    response = supabase.rpc("fetch_filtered", {
        "p_table_name": table_name,
        "p_filter_criteria": filters
    }).execute()
    return response


def fetch_with_children(table_name, record_id):
    supabase = get_supabase_client()
    # Correct parameter names as per the stored procedure definition
    response = supabase.rpc("fetch_with_children", {
        "p_table_name": table_name,
        "p_record_id": record_id
    }).execute()
    return response


def fetch_all_with_children(table_name):
    supabase = get_supabase_client()
    # Correct parameter names as per the stored procedure definition
    response = supabase.rpc("fetch_all_with_children", {
        "p_table_name": table_name
    }).execute()
    return response


def fetch_paginated_direct(table_name, page, page_size):
    supabase = get_supabase_client()
    start = (page - 1) * page_size
    end = start + page_size - 1
    response = supabase.table(table_name).select("*").range(start, end).execute()
    return response


def fetch_filtered_direct(table_name, filters):
    supabase = get_supabase_client()
    query = supabase.table(table_name).select("*")
    for key, value in filters.items():
        query = query.eq(key, value)
    response = query.execute()
    return response


def fetch_all_with_children_direct(table_name, child_table_name, foreign_key):
    supabase = get_supabase_client()
    parent_response = supabase.table(table_name).select("*").execute()
    child_response = supabase.table(child_table_name).select("*").execute()

    # Assuming child records need to be linked to parent records by a foreign key
    children_dict = {}
    for child in child_response.data:
        parent_id = child[foreign_key]
        if parent_id not in children_dict:
            children_dict[parent_id] = []
        children_dict[parent_id].append(child)

    # Combine parent and child data
    combined_data = []
    for parent in parent_response.data:
        parent_id = parent["id"]
        parent["children"] = children_dict.get(parent_id, [])
        combined_data.append(parent)

    return combined_data


def fetch_with_children_direct(table_name, record_id, child_table_name, foreign_key):
    supabase = get_supabase_client()
    parent_response = supabase.table(table_name).select("*").eq("id", record_id).execute()
    child_response = supabase.table(child_table_name).select("*").eq(foreign_key, record_id).execute()
    return {
        "parent": parent_response,
        "children": child_response}


def get_child_tables_with_fk_to(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query the information schema to find all foreign key constraints pointing to the specified table
    query = """
        SELECT
            tc.table_name AS child_table,
            kcu.column_name AS fk_column,
            ccu.table_name AS parent_table,
            ccu.column_name AS pk_column
        FROM 
            information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
        WHERE 
            ccu.table_name = %s 
            AND tc.constraint_type = 'FOREIGN KEY';
    """

    # Execute the query and get the response
    cursor.execute(query, (table_name,))
    records = cursor.fetchall()

    # Process the results to create a list of child tables and their foreign keys
    child_tables = {}
    for record in records:
        child_table = record[0]
        fk_column = record[1]
        if child_table not in child_tables:
            child_tables[child_table] = []
        child_tables[child_table].append(fk_column)

    # Close the connection
    cursor.close()
    conn.close()

    return child_tables


def simple_test():
    recipes = get_all_recipes()
    pretty_print(recipes)

    recipe_id = "e708eaf5-2c06-411f-9384-976ff85a6e24"
    recipe = get_recipe_by_id(recipe_id)
    pretty_print(recipe)

    new_recipe = {
        "name": "New Recipe",
        "description": "This Armani's new recipe."
    }
    created_recipe = create_recipe(new_recipe)
    pretty_print(created_recipe)

    updated_recipe = {
        "name": "Updated Recipe",
        "description": "This Armani's new recipe updated."
    }
    update_response = update_recipe(recipe_id, updated_recipe)
    pretty_print(update_response)

    paginated_response = fetch_paginated("recipe", 1, 5)
    pretty_print(paginated_response)

    filters = {
        "name": "New Recipe"
    }
    filtered_response = fetch_filtered("recipe", filters)
    pretty_print(filtered_response)

    record_id = "a0c28430-d8b0-465a-8c20-139c830c3e95"
    with_children_response = fetch_with_children("recipe", record_id)
    pretty_print(with_children_response)

    all_with_children_response = fetch_all_with_children("recipe")
    pretty_print(all_with_children_response)


def fetch_all_by_column_value(table, column, value):
    supabase = get_supabase_client()
    response = supabase.table(table).select("*").eq(column, value).execute()
    if hasattr(response, 'data'):
        data = response.data
    else:
        data = []

    return data

def get_compiled_recipe_by_id(compiled_id):
    data = fetch_all_by_column_value(
        table='compiled_recipe',
        column='id',
        value=compiled_id
    )
    compiled_recipe = data[0]
    return compiled_recipe

def get_compiled_recipe_by_recipe_id(recipe_id):
    data = fetch_all_by_column_value(
        table='compiled_recipe',
        column='recipe_id',
        value=recipe_id
    )
    return data


def get_compiled_recipe_by_recipe_id_highest_version(recipe_id):
    data = fetch_all_by_column_value(
        table='compiled_recipe',
        column='recipe_id',
        value=recipe_id
    )
    latest_version = max(data, key=lambda x: x['version']) if data else None
    return latest_version

def get_latest_compiled_recipe_version_inefficient(recipe_id):
    supabase = get_supabase_client()
    response = supabase.table("recipe").select("version").eq("id", recipe_id).single().execute()
    data = response.data
    version_number = data['version'] if data else None

    second_response = supabase.table("compiled_recipe").select("*").eq("recipe_id", recipe_id).eq("version", version_number).single().execute()
    compiled_recipe = second_response.data

    return compiled_recipe

def get_latest_compiled_recipe_version(recipe_id):
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            # Single query using a subquery
            query = """
                SELECT cr.*
                FROM compiled_recipe cr
                WHERE cr.recipe_id = %s
                AND cr.version = (SELECT version FROM recipe WHERE id = %s)
            """
            cur.execute(query, (recipe_id, recipe_id))
            result = cur.fetchone()
            return result
    finally:
        conn.close()



def main_direct():
    # filters = {"name": "New Recipe"}

    recipe_id = "d6020535-9f8a-4300-ae1c-d1ea8d35c1a5"
    recipe = get_recipe_by_id(recipe_id)
    vcprint(recipe, pretty=True, title="Recipe", color="cyan")


    # print("\nUsing Direct Query Versions:")
    # paginated_response_direct = fetch_paginated_direct("recipe", 1, 5)
    # vcprint(verbose=True, pretty=True, data=paginated_response_direct, title="Paginated Response Direct", color="blue")
    #
    # filtered_response_direct = fetch_filtered_direct("recipe", filters)
    # vcprint(verbose=True, pretty=True, data=filtered_response_direct, title="Filtered Response Direct", color="green")

    # with_children_response_direct = fetch_with_children_direct("recipe", recipe_id, "recipe_children", "recipe_id")
    # vcprint(verbose=True, pretty=True, data=with_children_response_direct, title="With Children Response Direct", color="cyan")
    #
    # all_with_children_response_direct = fetch_all_with_children_direct("recipe", "recipe_children", "recipe_id")
    # vcprint(verbose=True, pretty=True, data=all_with_children_response_direct, title="All With Children Response Direct", color="blue")
    table_name = "recipe"
    # child_tables = get_child_tables_with_fk_to(table_name)
    # print("Child tables with foreign keys to:", table_name)
    # for table, fk_columns in child_tables.items():
    #     print(f"Table: {table}, Foreign Key Columns: {fk_columns}")





if __name__ == "__main__":
    # main_direct()
    table = "compiled_recipe"
    column = "recipe_id"
    value = "15a11c3d-f037-4f2b-9e22-fe88e68d75e1"

    # latest_version = get_compiled_recipe_by_recipe_id_highest_version(value)

    latest_version = get_latest_compiled_recipe_version(value)

    vcprint(latest_version, pretty=True, title="Latest Version Compiled Recipe", color="blue")
