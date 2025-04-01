from database.client.postgres_connection import execute_sql_query


def get_all_tables(schema='public'):
    """Retrieves all table names in the specified schema."""
    query = """
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = %s
    ORDER BY table_name;
    """
    results = execute_sql_query(query, (schema,))
    return [row['table_name'] for row in results]


if __name__ == '__main__':
    from common import vcprint

    schema = 'public'

    results = get_all_tables(schema=schema)

    vcprint(data=results, title='All Tables', pretty=True, verbose=True, color='blue')
