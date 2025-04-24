from database.client.postgres_connection import execute_sql_query


def get_table_columns(schema, table_name, is_view):
    """Retrieves column information for a given table or view."""
    query = """
    SELECT 
        c.column_name, 
        c.data_type, 
        c.is_nullable, 
        c.column_default,
        array_agg(DISTINCT e.enumlabel ORDER BY e.enumlabel) AS options,
        pg_type.typname AS enum_type,
        CASE WHEN %s THEN false ELSE bool_or(tc.constraint_type = 'PRIMARY KEY') END AS is_primary_key,
        fk_info.foreign_table,
        fk_info.foreign_column,
        pgd.description, 
        string_agg(DISTINCT ic.indexname, ', ') AS indexname,
        cc.check_clause
    FROM 
        information_schema.columns c
    LEFT JOIN pg_type ON c.udt_name = pg_type.typname
    LEFT JOIN pg_enum e ON e.enumtypid = pg_type.oid
    LEFT JOIN information_schema.key_column_usage kcu
        ON c.table_name = kcu.table_name AND c.column_name = kcu.column_name
    LEFT JOIN information_schema.table_constraints tc
        ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = c.table_schema
    LEFT JOIN (
        SELECT 
            kcu.table_name AS local_table,
            kcu.column_name AS local_column,
            ccu.table_name AS foreign_table,
            ccu.column_name AS foreign_column
        FROM 
            information_schema.key_column_usage kcu
        JOIN information_schema.constraint_column_usage ccu 
            ON kcu.constraint_name = ccu.constraint_name
        JOIN information_schema.table_constraints tc 
            ON tc.constraint_name = kcu.constraint_name AND tc.constraint_type = 'FOREIGN KEY'
    ) AS fk_info
        ON c.table_name = fk_info.local_table AND c.column_name = fk_info.local_column
    LEFT JOIN pg_catalog.pg_description pgd
        ON pgd.objoid = (SELECT oid FROM pg_class WHERE relname = c.table_name AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = c.table_schema))
        AND pgd.objsubid = c.ordinal_position
    LEFT JOIN (
        SELECT
            i.relname AS indexname,
            a.attname AS column_name,
            t.relname AS table_name
        FROM
            pg_class t
        JOIN pg_index ix ON t.oid = ix.indrelid
        JOIN pg_class i ON i.oid = ix.indexrelid
        JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
    ) ic
        ON ic.table_name = c.table_name::text AND ic.column_name = c.column_name
    LEFT JOIN (
        SELECT
            constraint_name,
            check_clause
        FROM
            information_schema.check_constraints
    ) cc
        ON cc.constraint_name = tc.constraint_name
    WHERE 
        c.table_schema = %s AND c.table_name = %s
    GROUP BY 
        c.column_name, c.data_type, c.is_nullable, c.column_default, pg_type.typname, 
        fk_info.foreign_table, fk_info.foreign_column, pgd.description, cc.check_clause, c.ordinal_position
    ORDER BY 
        c.ordinal_position;
    """
    return execute_sql_query(query, (is_view, schema, table_name))


if __name__ == "__main__":
    from common import vcprint

    schema = "public"
    table = "registered_function"
    is_view = False

    results = get_table_columns(schema=schema, table_name=table, is_view=is_view)

    vcprint(data=results, title="Table Columns", pretty=True, verbose=True, color="blue")
