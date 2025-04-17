import os
from psycopg2.extras import RealDictCursor
from psycopg2 import pool
from dotenv import load_dotenv
from matrx_utils.common import vcprint
from matrx_utils.database.utils.sql_utils import sql_param_to_psycopg2

connection_pool = None

database_project = {
    "supabase_automation_matrix": {
        "host": os.environ.get("SUPABASE_MATRIX_HOST"),
        "port": os.environ.get("SUPABASE_MATRIX_PORT"),
        "database_name": os.environ.get("SUPABASE_MATRIX_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_MATRIX_USER"),
        "password": os.environ.get("SUPABASE_MATRIX_PASSWORD"),
    },
    "supabase_ai-matrix": {
        "host": os.environ.get("SUPABASE_AI_MATRIX_HOST"),
        "port": os.environ.get("SUPABASE_AI_MATRIX_PORT"),
        "database_name": os.environ.get("SUPABASE_AI_MATRIX_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_AI_MATRIX_USER"),
        "password": os.environ.get("SUPABASE_AI_MATRIX_PASSWORD"),
    },
    "supabase_sample_matrix": {
        "host": os.environ.get("SUPABASE_SAMPLE_MATRIX_HOST"),
        "port": os.environ.get("SUPABASE_SAMPLE_MATRIX_PORT"),
        "database_name": os.environ.get("SUPABASE_SAMPLE_MATRIX_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_SAMPLE_MATRIX_USER"),
        "password": os.environ.get("SUPABASE_SAMPLE_MATRIX_PASSWORD"),
    },
    "supabase_matrix_django": {  # Fixed capitalization
        "host": os.environ.get("SUPABASE_MATRIX_DJANGO_HOST"),
        "port": os.environ.get("SUPABASE_MATRIX_DJANGO_PORT"),
        "database_name": os.environ.get("SUPABASE_MATRIX_DJANGO_DATABASE_NAME"),
        "user": os.environ.get("SUPABASE_MATRIX_DJANGO_USER"),
        "password": os.environ.get("SUPABASE_MATRIX_DJANGO_PASSWORD"),
    },
}


valid_projects = database_project.keys()


def init_connection_details(config_name):
    global connection_pool

    if connection_pool is None:
        load_dotenv()

        try:
            config = database_project[config_name]
        except KeyError:
            raise KeyError(f"Configuration '{config_name}' not found in database_project")

        vcprint(f"\n[Matrx ORM] Using configuration for: {config_name}\n", color="green")

        db_host = config.get("host")
        db_port = config.get("port")
        db_name = config.get("database_name")
        db_user = config.get("user")
        db_password = config.get("password")

        if not all([db_host, db_port, db_name, db_user, db_password]):
            raise ValueError(f"Incomplete database configuration for '{config_name}'. " "Please check your environment variables.")

        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

        vcprint(f"\n[Matrx ORM] Connection String:\n{connection_string}\n", color="green")

        connection_pool = pool.SimpleConnectionPool(1, 10, dsn=connection_string, sslmode="require")


def get_postgres_connection(
    database_project="this_will_cause_error_specify_the_database",
):
    init_connection_details(database_project)
    conn = connection_pool.getconn()
    return conn


def execute_sql_query(query, params=None, database_project="this_will_cause_error_specify_the_database"):
    """
    Executes a SQL query and returns the results as a list of dictionaries.
    """
    conn = get_postgres_connection(database_project)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if params and isinstance(params, dict):
                query, params = sql_param_to_psycopg2(query, params)
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        connection_pool.putconn(conn)


def execute_sql_file(filename, params=None, database_project="this_will_cause_error_specify_the_database"):
    """
    Executes a SQL query from a file and returns the results.
    """
    sql_dir = os.path.join(os.path.dirname(__file__), "sql")
    with open(os.path.join(sql_dir, filename), "r") as sql_file:
        query = sql_file.read()

    if params:
        query, params = sql_param_to_psycopg2(query, params)

    vcprint(f"Executing query:\n{query}\n", color="green")
    vcprint(f"With params: {params}\n", color="green")

    return execute_sql_query(query, params, database_project)
