from database.client.postgres_connection import execute_sql_query


def get_table_relationships(schema, database_project):
    print("get_table_relationships called with", database_project)

    query = """
    WITH fk_info AS (
        SELECT
            tc.table_schema,
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
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
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = %s
    ),
    all_tables AS (
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type = 'BASE TABLE'
    )
    SELECT
        at.table_name,
        (SELECT json_object_agg(
            CASE 
                WHEN fk.foreign_table_name = at.table_name THEN 'self_reference'
                ELSE fk.foreign_table_name 
            END,
            json_build_object(
                'constraint_name', fk.constraint_name,
                'column', fk.column_name,
                'foreign_column', fk.foreign_column_name
            )
        )
        FROM fk_info fk
        WHERE fk.table_name = at.table_name) AS foreign_keys,
        (SELECT json_object_agg(
            fk2.table_name,
            json_build_object(
                'constraint_name', fk2.constraint_name,
                'column', fk2.column_name,
                'foreign_column', fk2.foreign_column_name
            )
        )
        FROM fk_info fk2
        WHERE fk2.foreign_table_name = at.table_name) AS referenced_by
    FROM all_tables at;
    """
    return execute_sql_query(query, (schema, schema), database_project)


if __name__ == "__main__":
    from common import vcprint

    schema = "public"
    database_project = "supabase_automation_matrix"

    results = get_table_relationships(schema=schema, database_project=database_project)

    vcprint(
        data=results,
        title="Table Relationships",
        pretty=True,
        verbose=True,
        color="blue",
    )
