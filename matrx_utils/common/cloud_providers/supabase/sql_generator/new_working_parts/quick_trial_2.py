import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

db_host = os.environ.get("SUPABASE_MATRIX_HOST")
db_port = os.environ.get("SUPABASE_MATRIX_PORT")
db_name = os.environ.get("SUPABASE_MATRIX_DATABASE_NAME")
db_user = os.environ.get("SUPABASE_MATRIX_USER")
db_password = os.environ.get("SUPABASE_MATRIX_PASSWORD")

connection_string = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

def get_foreign_keys():
    print("Retrieving foreign key information:")
    sql_query = """
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
    WHERE tc.constraint_type = 'FOREIGN KEY';
    """
    try:
        # Connect to the PostgreSQL database using psycopg2
        connection = psycopg2.connect(connection_string, sslmode='require')
        cursor = connection.cursor()
        cursor.execute(sql_query)
        result = cursor.fetchall()
        cursor.close()
        connection.close()
        return result
    except Exception as e:
        print(f"Error retrieving foreign keys: {str(e)}")
        return None

# Get foreign keys
fk_info = get_foreign_keys()

if fk_info:
    print("\nForeign key information:")
    for fk in fk_info:
        print(f"\nConstraint: {fk[1]}")
        print(f"From: {fk[0]}.{fk[2]}.{fk[3]}")
        print(f"To: {fk[4]}.{fk[5]}.{fk[6]}")
else:
    print("Unable to retrieve foreign key information.")
