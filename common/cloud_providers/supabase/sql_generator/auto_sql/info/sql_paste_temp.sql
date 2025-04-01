CREATE OR REPLACE FUNCTION public.get_database_schema_json()
RETURNS json AS $$
DECLARE
    result json;
BEGIN
    WITH
      all_tables AS (
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'  -- Adjust schema if needed
          AND table_type = 'BASE TABLE'
      ),
      table_schema AS (
        SELECT
          c.table_name,
          c.column_name,
          CASE
            WHEN c.data_type = 'ARRAY' THEN (
              SELECT regexp_replace(c.udt_name, '^_', '') || '[]'
            )
            WHEN c.data_type = 'USER-DEFINED' THEN c.udt_name
            ELSE c.data_type
          END AS data_type,
          CASE
            WHEN c.data_type = 'USER-DEFINED' THEN (
              SELECT json_agg(e.enumlabel)
              FROM pg_type t
              JOIN pg_enum e ON t.oid = e.enumtypid
              JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace
              WHERE t.typname = c.udt_name
            )
            ELSE NULL
          END AS options,
          c.is_nullable = 'NO' AS is_required,
          c.column_default
        FROM
          information_schema.columns c
        JOIN all_tables t ON c.table_name = t.table_name
      ),
      foreign_keys_to AS (
        SELECT
          tc.table_name,
          tc.constraint_name,
          kcu.column_name AS foreign_key_column,
          ccu.table_name AS referenced_table,
          ccu.column_name AS referenced_column
        FROM
          information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
        WHERE
          tc.constraint_type = 'FOREIGN KEY'
      ),
      foreign_keys_from AS (
        SELECT
          tc.table_name,
          tc.constraint_name,
          kcu.column_name AS foreign_key_column,
          ccu.table_name AS referenced_table,
          ccu.column_name AS referenced_column
        FROM
          information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
        WHERE
          tc.constraint_type = 'FOREIGN KEY'
      ),
      primary_keys AS (
        SELECT
          tc.table_name,
          kcu.column_name AS primary_key_column
        FROM
          information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
        WHERE
          tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_schema = 'public'  -- Adjust schema if needed
      )
    SELECT json_build_object(
      'table_names', (
        SELECT json_object_agg(
          t.table_name,
          json_build_object(
            'columns', (
              SELECT json_agg(ts.column_name)
              FROM table_schema ts
              WHERE ts.table_name = t.table_name
            ),
            'primary_key', (
              SELECT primary_key_column
              FROM primary_keys pk
              WHERE pk.table_name = t.table_name
            )
          )
        )
        FROM all_tables t
      ),
      'tables', (
        SELECT json_agg(
          json_build_object(
            'table_name', t.table_name,
            'primary_key', (
              SELECT primary_key_column
              FROM primary_keys pk
              WHERE pk.table_name = t.table_name
            ),
            'schema', (
              SELECT json_agg(json_build_object(
                'column_name', ts.column_name,
                'data_type', ts.data_type,
                'options', ts.options,
                'is_required', ts.is_required,
                'default_value', ts.column_default,
                'is_primary_key', (ts.column_name = pk.primary_key_column)
              ))
              FROM table_schema ts
              LEFT JOIN primary_keys pk ON pk.table_name = t.table_name
              WHERE ts.table_name = t.table_name
            ),
            'inbound_foreign_keys', (
              SELECT json_agg(json_build_object(
                'constraint_name', fkt.constraint_name,
                'foreign_key_column', fkt.foreign_key_column,
                'referenced_table', fkt.referenced_table,
                'referenced_column', fkt.referenced_column
              ))
              FROM foreign_keys_to fkt
              WHERE fkt.table_name = t.table_name
            ),
            'outbound_foreign_keys', (
              SELECT json_agg(json_build_object(
                'constraint_name', fkf.constraint_name,
                'foreign_key_column', fkf.foreign_key_column,
                'referenced_table', fkf.referenced_table,
                'referenced_column', fkf.referenced_column
              ))
              FROM foreign_keys_from fkf
              WHERE fkf.referenced_table = t.table_name
            )
          )
        )
        FROM all_tables t
      )
    ) INTO result;

    RETURN result;
END;
$$ LANGUAGE plpgsql;
