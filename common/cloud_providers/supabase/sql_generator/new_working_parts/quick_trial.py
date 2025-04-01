import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from psycopg2.extras import NamedTupleCursor
from collections import namedtuple

# Load environment variables from .env file
load_dotenv()

# Retrieve connection details from environment variables
db_host = os.environ.get("SUPABASE_MATRIX_HOST")
db_port = os.environ.get("SUPABASE_MATRIX_PORT")
db_name = os.environ.get("SUPABASE_MATRIX_DATABASE_NAME")
db_user = os.environ.get("SUPABASE_MATRIX_USER")
db_password = os.environ.get("SUPABASE_MATRIX_PASSWORD")

# Construct the connection string
connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

ForeignKey = namedtuple('ForeignKey', [
    'table_schema', 'constraint_name', 'table_name', 'column_name',
    'foreign_table_schema', 'foreign_table_name', 'foreign_column_name'
])


def get_foreign_keys(schema='public'):
    print(f"Retrieving foreign key information for schema: {schema}")
    sql_query = sql.SQL("""
    SELECT
        tc.table_schema, 
        tc.constraint_name, 
        tc.table_name, 
        kcu.column_name, 
        ccu.table_schema AS foreign_table_schema,
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = %s;
    """)

    try:
        with psycopg2.connect(connection_string, sslmode='require') as connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(sql_query, (schema,))
                result = [ForeignKey(*row) for row in cursor.fetchall()]
        return result
    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None


# Get foreign keys
fk_info = get_foreign_keys()

if fk_info:
    print("\nForeign key information:")
    for fk in fk_info:
        print(f"\nConstraint: {fk.constraint_name}")
        print(f"From: {fk.table_schema}.{fk.table_name}.{fk.column_name}")
        print(f"To: {fk.foreign_table_schema}.{fk.foreign_table_name}.{fk.foreign_column_name}")
else:
    print("Unable to retrieve foreign key information.")
