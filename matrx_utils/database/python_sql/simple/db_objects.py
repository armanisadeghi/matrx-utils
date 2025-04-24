from database.client.postgres_connection import execute_sql_query


def get_db_objects(schema="public"):
    """
    Retrieves comprehensive information about tables and views in the specified schema.
    """
    query = """
    WITH object_details AS (
        SELECT 
            c.oid,
            c.relname AS name,
            CASE 
                WHEN c.relkind = 'r' THEN 'table'
                WHEN c.relkind = 'v' THEN 'view'
                ELSE c.relkind::text
            END AS type,
            n.nspname AS schema,
            current_database() AS database,
            pg_get_userbyid(c.relowner) AS owner,
            CASE 
                WHEN c.relkind = 'r' THEN pg_table_size(c.oid)
                WHEN c.relkind = 'v' THEN pg_relation_size(c.oid)
            END AS size_bytes,
            CASE 
                WHEN c.relkind = 'r' THEN pg_indexes_size(c.oid)
                ELSE NULL
            END AS index_size_bytes,
            CASE 
                WHEN c.relkind = 'r' THEN pg_stat_get_live_tuples(c.oid)
                ELSE NULL
            END AS rows,
            CASE 
                WHEN c.relkind = 'r' THEN s.last_vacuum AT TIME ZONE 'UTC'
                ELSE NULL
            END AS last_vacuum,
            CASE 
                WHEN c.relkind = 'r' THEN s.last_analyze AT TIME ZONE 'UTC'
                ELSE NULL
            END AS last_analyze,
            obj_description(c.oid, 'pg_class') AS description,
            c.reltuples::bigint AS estimated_row_count,
            CASE 
                WHEN c.relkind = 'r' THEN pg_total_relation_size(c.oid)
                ELSE NULL
            END AS total_bytes,
            CASE
                WHEN c.relkind = 'r' THEN EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conrelid = c.oid AND contype = 'p'
                )
                ELSE NULL
            END AS has_primary_key,
            CASE
                WHEN c.relkind = 'r' THEN (
                    SELECT COUNT(*) FROM pg_index i
                    WHERE i.indrelid = c.oid AND i.indisprimary = false
                )
                ELSE NULL
            END AS index_count
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
        WHERE n.nspname = %s AND c.relkind IN ('r', 'v')
    )
    SELECT 
        od.*,
        CASE 
            WHEN od.type = 'table' THEN (
                SELECT json_agg(json_build_object(
                    'name', a.attname,
                    'type', pg_catalog.format_type(a.atttypid, a.atttypmod),
                    'nullable', NOT a.attnotnull,
                    'default', pg_get_expr(d.adbin, d.adrelid)
                ))
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
                WHERE a.attrelid = od.oid AND a.attnum > 0 AND NOT a.attisdropped
            )
            ELSE NULL
        END AS columns
    FROM object_details od
    ORDER BY od.name;
    """
    return execute_sql_query(query, (schema,))


if __name__ == "__main__":
    from common import vcprint

    schema = "public"

    results = get_db_objects(schema=schema)

    vcprint(data=results, title="Database Objects", pretty=True, verbose=True, color="blue")
