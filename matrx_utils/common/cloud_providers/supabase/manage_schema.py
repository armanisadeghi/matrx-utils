# common/supabase/manage_schema.py
from common import pretty_print
from .supabase_client import get_supabase_client, execute_sql_query


def get_table_schema(table_name, schema='public'):
    """
    Retrieves the schema for a specific table, including column options for enums.
    """
    query = """
    SELECT 
        c.column_name, 
        c.data_type, 
        c.is_nullable, 
        c.column_default,
        pg_type.typname AS udt_name,  -- Get the user-defined type name for enum types
        array_agg(e.enumlabel ORDER BY e.enumsortorder) AS options -- Aggregate possible enum values if any
    FROM 
        information_schema.columns c
    LEFT JOIN pg_type ON c.udt_name = pg_type.typname
    LEFT JOIN pg_enum e ON e.enumtypid = pg_type.oid
    WHERE 
        c.table_schema = %s AND c.table_name = %s
    GROUP BY 
        c.column_name, c.data_type, c.is_nullable, c.column_default, pg_type.typname, c.ordinal_position
    ORDER BY 
        c.ordinal_position;
    """
    return execute_sql_query(query, (schema, table_name))


def get_all_tables(schema='public'):
    """
    Retrieves all tables in the specified schema.
    """
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = %s AND table_type = 'BASE TABLE'
    ORDER BY table_name;
    """
    return [table['table_name'] for table in execute_sql_query(query, (schema,))]


def get_foreign_keys(schema='public'):
    """
    Retrieves foreign key information for the specified schema.
    """
    query = """
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
    """
    return execute_sql_query(query, (schema,))


def get_primary_keys(schema='public'):
    """
    Retrieves primary key information for all tables in the specified schema.
    """
    query = """
    SELECT
        tc.table_schema, 
        tc.table_name, 
        kcu.column_name
    FROM 
        information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
    WHERE tc.constraint_type = 'PRIMARY KEY'
    AND tc.table_schema = %s
    ORDER BY tc.table_name, kcu.ordinal_position;
    """
    return execute_sql_query(query, (schema,))


def get_indexes(schema='public'):
    """
    Retrieves index information for all tables in the specified schema.
    """
    query = """
    SELECT
        schemaname AS schema_name,
        tablename AS table_name,
        indexname AS index_name,
        indexdef AS index_definition
    FROM
        pg_indexes
    WHERE
        schemaname = %s
    ORDER BY
        tablename,
        indexname;
    """
    return execute_sql_query(query, (schema,))


def get_full_schema(schema='public'):
    """
    Retrieves the full schema information including tables, columns, primary keys, foreign keys, and indexes.
    """
    tables = get_all_tables(schema)
    full_schema = {}

    for table in tables:
        full_schema[table] = {
            'columns': get_table_schema(table, schema),
            'primary_key': next((pk for pk in get_primary_keys(schema) if pk['table_name'] == table), None),
            'foreign_keys': [fk for fk in get_foreign_keys(schema) if fk['table_name'] == table],
            'indexes': [idx for idx in get_indexes(schema) if idx['table_name'] == table]
        }

    return full_schema


def print_schema_summary(schema='public'):
    """
    Prints a summary of the schema including tables, their columns, and relationships.
    """
    full_schema = get_full_schema(schema)

    for table, info in full_schema.items():
        print(f"\nTable: {table}")
        print("Columns:")
        for column in info['columns']:
            print(f"  - {column['column_name']} ({column['data_type']})")

        if info['primary_key']:
            print(f"Primary Key: {info['primary_key']['column_name']}")

        if info['foreign_keys']:
            print("Foreign Keys:")
            for fk in info['foreign_keys']:
                print(f"  - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}")

        if info['indexes']:
            print("Indexes:")
            for idx in info['indexes']:
                print(f"  - {idx['index_name']}")


# Example usage
if __name__ == "__main__":
    full_schema = get_full_schema()
    pretty_print(full_schema)
    #print_schema_summary()
