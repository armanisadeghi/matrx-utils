# common/supabase/supabase_client.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

from core import BASE_DIR, TEMP_DIR
from common import vcprint

db_host = None
db_port = None
db_name = None
db_user = None
db_password = None
url = None
key = None
connection_string = None

# A global variable to hold the single instance of the Supabase client
_supabase_instance = None


def init_connection_details():
    global db_host, db_port, db_name, db_user, db_password, url, key, connection_string

    if db_host is None:  # Only load if not already loaded
        load_dotenv()

        db_host = os.environ.get("SUPABASE_MATRIX_HOST")
        db_port = os.environ.get("SUPABASE_MATRIX_PORT")
        db_name = os.environ.get("SUPABASE_MATRIX_DATABASE_NAME")
        db_user = os.environ.get("SUPABASE_MATRIX_USER")
        db_password = os.environ.get("SUPABASE_MATRIX_PASSWORD")
        url = os.environ.get("SUPABASE_MATRIX_URL")
        key = os.environ.get("SUPABASE_MATRIX_KEY")

        connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def get_supabase_client():
    global _supabase_instance

    # If the Supabase client instance is already created, return it
    if _supabase_instance is None:
        vcprint("get_supabase_client creating === NEW === Supabase client (You should never see this twice)", color="yellow")
        init_connection_details()
        _supabase_instance = create_client(url, key)

    return _supabase_instance


def get_postgres_connection():
    """
    Returns a connection to the PostgreSQL database.
    """
    init_connection_details()
    return psycopg2.connect(connection_string, sslmode='require')


def execute_sql_query(query, params=None):
    """
    Executes a SQL query and returns the results as a list of dictionaries.
    """
    with get_postgres_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def execute_sql_command(command, params=None):
    """
    Executes a SQL command (INSERT, UPDATE, DELETE) and returns the number of affected rows.
    """
    with get_postgres_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(command, params)
            conn.commit()
            return cur.rowcount


if __name__ == "__main__":
    init_connection_details()  # Initialize when running the script directly
    supabase = get_supabase_client()
    print(supabase)
    postgres_conn = get_postgres_connection()
    print(postgres_conn)
