# procedures/base_procedure.py








class BaseProcedure:
    def __init__(self, table_name, columns, primary_key):
        self.table_name = table_name
        self.columns = columns
        self.primary_key = primary_key
        self.select_columns = ",\n".join([f'  "{col}"' for col in columns.keys()])
        self.select_return_columns = ",\n".join([f'  "{col}" {col_type}' for col, col_type in columns.items()])

    def generate_procedure(self):
        raise NotImplementedError("Subclasses must implement this method")

    def generate_test_statement(self):
        raise NotImplementedError("Subclasses must implement this method")

    def generate_drop_statement(self, function_name):
        return f"DROP FUNCTION IF EXISTS public.{function_name}();"


    def generate_select_procedure(self):
        function_name = f"fetch_all_{self.table_name}"

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}();"

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}()
RETURNS TABLE (
{self.select_return_columns}
) LANGUAGE plpgsql AS $function$
BEGIN
  RETURN QUERY
  SELECT
{self.select_columns}
  FROM
    public.{self.table_name} st;
END;
$function$;
"""

        test_statement = f"SELECT * FROM public.{function_name}();"

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_select_by_id_procedure(self):
        function_name = f"fetch_by_id_{self.table_name}"
        if not self.primary_key:
            raise ValueError(f"No primary key defined for table {self.table_name}")

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}({self.columns[self.primary_key]['data_type']});"

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  record_id {self.columns[self.primary_key]['data_type']}
) RETURNS TABLE (
{self.select_return_columns}
) LANGUAGE plpgsql AS $function$
BEGIN
  RETURN QUERY
  SELECT
{self.select_columns}
  FROM
    public.{self.table_name} st
  WHERE
    st.{self.primary_key} = record_id;
END;
$function$;
"""

        test_statement = f"SELECT * FROM public.{function_name}('ENTER-ID-HERE');"

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_insert_procedure(self):
        function_name = f"add_one_{self.table_name}"

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}(\n  {self.formatted_drop_parameters}\n);"

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  {self.formatted_create_parameters}
) RETURNS TABLE (
  {',\n  '.join(self.return_columns_list)}
) LANGUAGE plpgsql AS $function$
DECLARE
  inserted_row public.{self.table_name}%ROWTYPE;
BEGIN
  INSERT INTO public.{self.table_name} (
  {self.formatted_columns}
  ) VALUES (
  {self.formatted_values}
  ) RETURNING * INTO inserted_row;

  RETURN QUERY
  SELECT
    {self.formatted_return_query};
END;
$function$;
"""

        test_statement = f"SELECT * FROM public.{function_name}(\n  {self.formatted_test_arguments}\n);"

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_upsert_procedure(self):
        function_name = f"upsert_{self.table_name}"

        upsert_test_arguments = ', '.join(filter(None, [self.formatted_test_arguments, self.formatted_non_required_test_arguments]))
        add_function_name = f"add_one_{self.table_name}"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  {self.formatted_drop_parameters}
);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  {self.formatted_create_parameters}
) RETURNS void
LANGUAGE plpgsql AS $function$
BEGIN
  INSERT INTO public.{self.table_name} (
    {', '.join(self.columns_list)}
  ) VALUES (
    {', '.join(self.values_list)}
  )
  ON CONFLICT ("{self.primary_key}") DO UPDATE
  SET
    {self.formatted_set_clause};
END;
$function$;
"""

        # Test Statement
        test_statement = f"""
SELECT * FROM public.{add_function_name}(
  {self.formatted_test_arguments}
);

SELECT public.{function_name}(
  {upsert_test_arguments}
);

SELECT * FROM public.{self.table_name}
WHERE "{self.primary_key}" = {self.test_values[0]};
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_delete_one_procedure(self):
        """
        Generate SQL for a stored procedure to delete a record by primary key.
        """
        function_name = "delete_one"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']}
);
"""

        # Core Procedure
        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']}
) RETURNS void AS $$
DECLARE
  sql_query text;
BEGIN
  sql_query := format('DELETE FROM %I WHERE "{self.primary_key}" = $1', p_table_name);
  EXECUTE sql_query USING p_id;
END;
$$ LANGUAGE plpgsql;
"""

        # Test Statement
        test_statement = f"""
SELECT public.{function_name}(
  '{self.table_name}',
  {self.test_values[0]}
);

SELECT * FROM {self.table_name} WHERE "{self.primary_key}" = {self.test_values[0]};
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_update_one_procedure(self):
        """
        Generate SQL for a stored procedure to update a record using JSONB data.
        """
        function_name = "update_one"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']},
  p_data jsonb
);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']},
  p_data jsonb
) RETURNS void AS $$
DECLARE
  sql_query text;
  update_parts text := '';
  column_name text;
  column_type text;
BEGIN
  FOR column_name, column_type IN 
    SELECT a.attname, t.typname
    FROM pg_attribute a
    JOIN pg_class c ON a.attrelid = c.oid
    JOIN pg_namespace n ON c.relnamespace = n.oid
    JOIN pg_type t ON a.atttypid = t.oid
    WHERE n.nspname = 'public'
      AND c.relname = p_table_name
      AND a.attnum > 0
      AND NOT a.attisdropped
  LOOP
    IF p_data ? column_name THEN
      IF column_type = 'jsonb' THEN
        update_parts := update_parts || format('%I = $1->%L, ', column_name, column_name);
      ELSIF column_type IN ('text', 'varchar', 'char', 'uuid') THEN
        update_parts := update_parts || format('%I = ($1->>%L)::%I, ', column_name, column_name, column_type);
      ELSE
        -- For other types (including enums), we cast to text first, then to the target type
        update_parts := update_parts || format('%I = ($1->>%L)::%I::%I, ', column_name, column_name, 'text', column_type);
      END IF;
    END IF;
  END LOOP;

  update_parts := rtrim(update_parts, ', ');

  sql_query := format('UPDATE %I SET %s WHERE "{self.primary_key}" = $2', p_table_name, update_parts);

  EXECUTE sql_query USING p_data, p_id;
END;
$$ LANGUAGE plpgsql;
"""

        # Test Statement
        test_statement = f"""
SELECT public.{function_name}(
  '{self.table_name}',
  {self.test_values[0]},
  '{{"name": "Updated Name", "name": "partial_page"}}'::jsonb
);

-- Verify the update
SELECT * FROM {self.table_name} WHERE "{self.primary_key}" = {self.test_values[0]};
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_fetch_paginated_procedure(self):
        """
        Generate SQL for a stored procedure to fetch records with pagination.
        """
        function_name = "fetch_paginated"

        # Drop Statement
        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text,
  p_page integer,
  p_page_size integer
);
"""

        # Core Procedure
        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text,
  p_page integer,
  p_page_size integer
) RETURNS TABLE (
  result jsonb
) AS $$
DECLARE
  sql_query text;
BEGIN
  sql_query := format('
    SELECT jsonb_agg(t) AS result
    FROM (
      SELECT *
      FROM %I
      ORDER BY "{self.primary_key}"
      LIMIT $1
      OFFSET $2
    ) t', p_table_name);

  RETURN QUERY EXECUTE sql_query USING p_page_size, (p_page - 1) * p_page_size;
END;
$$ LANGUAGE plpgsql;
"""

        test_statement = f"""
SELECT * FROM public.{function_name}(
  '{self.table_name}', 1, 3
);
"""

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_fetch_filtered_procedure(self):
        """
        Generate SQL for a stored procedure to fetch records based on filter criteria in JSONB format.
        """
        function_name = "fetch_filtered"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text,
  p_filter_criteria jsonb
);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text,
  p_filter_criteria jsonb
) RETURNS TABLE (
  result jsonb
) AS $$
DECLARE
  sql_query text;
  where_clause text := '';
  key text;
  value jsonb;
BEGIN
  FOR key, value IN SELECT * FROM jsonb_each(p_filter_criteria) LOOP
    where_clause := where_clause || format('%I = %L AND ', key, value#>>'{{}}');
  END LOOP;

  where_clause := rtrim(where_clause, 'AND ');

  sql_query := format('
    SELECT jsonb_agg(t) AS result
    FROM (
      SELECT *
      FROM %I
      WHERE %s
      ORDER BY "{self.primary_key}"
    ) t', p_table_name, where_clause);

  RETURN QUERY EXECUTE sql_query;
END;
$$ LANGUAGE plpgsql;
"""

        test_statement = f"""
SELECT * FROM public.{function_name}(
  '{self.table_name}', '{{"type": "full_page"}}'::jsonb
);
"""

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_fetch_with_children_procedure(self):
        """
        Generate SQL for a stored procedure to fetch a record with its children records.
        """
        function_name = "fetch_with_children"

        child_select_statements = "-- NEED-A-SOLUTION-FOR-THIS-PART THIS IS SUPPOSED TO BE SOME NESTED OBJECT FOR THE CHILDREN."  # self._prepare_child_select_statements()

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']}
);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']}
) RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  -- Fetch the main record
  EXECUTE format('
    SELECT to_jsonb(t) AS result
    FROM %I t
    WHERE "{self.primary_key}" = $1
  ', p_table_name)
  INTO result
  USING p_id;

  {child_select_statements}

  RETURN result;
END;
$$ LANGUAGE plpgsql;
"""

        # Test Statement
        test_statement = f"""
SELECT public.{function_name}('{self.table_name}', {self.test_values[0]});
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_fetch_all_with_children_procedure(self):
        """
        Generate SQL for a stored procedure to fetch all records with their children records.
        """
        function_name = "fetch_all_with_children"

        # Drop Statement
        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text
);
"""

        # Core Procedure
        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text
) RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  -- Fetch all main records
  EXECUTE format('
    WITH main_records AS (
      SELECT {self.primary_key}
      FROM %I
    )
    SELECT jsonb_agg(
      public.fetch_with_children($1, mr.{self.primary_key})
    ) AS result
    FROM main_records mr
  ', p_table_name)
  INTO result
  USING p_table_name;

  RETURN result;
END;
$$ LANGUAGE plpgsql;
"""

        # Test Statement
        test_statement = f"""
SELECT public.{function_name}('{self.table_name}');
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_fetch_with_parent_procedure(self):
        """
        Generate SQL for a stored procedure to fetch a record with its parent record.
        """
        function_name = "fetch_with_parent"

        if not self.primary_key:
            return ""

        if self.outbound_foreign_keys:
            parent_fk = next((fk for fk in self.outbound_foreign_keys if fk['foreign_key_column'] == self.primary_key), None)

        else:
            return "-- No parent so no need for this function."

        parent_table = parent_fk['referenced_table']
        parent_column = parent_fk['referenced_column']

        # Drop Statement
        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']}
);
"""

        # Core Procedure
        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text,
  p_id {self.columns[self.primary_key]['data_type']}
) RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  -- Fetch the main record with its parent
  EXECUTE format('
    WITH main_record AS (
      SELECT to_jsonb(c) AS result
      FROM %I c
      WHERE c.{self.primary_key} = $1
    )
    SELECT jsonb_set(
      mr.result,
      ''{{parent}}'',
      COALESCE(to_jsonb(p), ''null'')
    ) AS result
    FROM main_record mr
    LEFT JOIN {parent_table} p ON p.{parent_column} = (mr.result->>''{self.primary_key}'')::uuid
  ', p_table_name)
  INTO result
  USING p_id;

  RETURN result;
END;
$$ LANGUAGE plpgsql;
"""

        # Test Statement
        test_statement = f"""
SELECT public.{function_name}('{self.table_name}', {self.test_values[0]});
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_fetch_all_with_parent_procedure(self):
        """
        Generate SQL for a stored procedure to fetch all records with their parent records.
        """
        function_name = "fetch_all_with_parent"

        if self.outbound_foreign_keys:
            parent_fk = next((fk for fk in self.outbound_foreign_keys if fk['foreign_key_column'] == self.primary_key), None)

        else:
            return "-- No parent so no need for this function."

        parent_table = parent_fk['referenced_table']
        parent_column = parent_fk['referenced_column']

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(
  p_table_name text
);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  p_table_name text
) RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  -- Fetch all records with their parents
  EXECUTE format('
    WITH main_records AS (
      SELECT to_jsonb(c) AS result
      FROM %I c
    )
    SELECT jsonb_agg(
      jsonb_set(
        mr.result,
        ''{{parent}}'',
        COALESCE(to_jsonb(p), ''null'')
      )
    ) AS result
    FROM main_records mr
    LEFT JOIN {parent_table} p ON p.{parent_column} = (mr.result->>''{self.primary_key}'')::uuid
  ', p_table_name)
  INTO result;

  RETURN result;
END;
$$ LANGUAGE plpgsql;
"""

        test_statement = f"""
SELECT public.{function_name}('{self.table_name}');
"""

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def _prepare_child_select_statements(self):
        """
        Prepare SQL statements to fetch child records for each inbound foreign key.
        """
        child_select_statements = []

        for fk in self.inbound_foreign_keys:
            child_table = fk['foreign_key_column']
            referenced_column = fk['referenced_column']
            constraint_name = fk['constraint_name']

            child_select_statement = f"""
      -- Fetch {child_table} records
      WITH {child_table}_records AS (
        SELECT to_jsonb(c) AS {child_table}
        FROM {constraint_name} c
        WHERE c.{referenced_column} = p_id
      )
      SELECT jsonb_set(
        result,
        '{{{child_table}}}',
        COALESCE((SELECT jsonb_agg({child_table}) FROM {child_table}_records), '[]'::jsonb)
      ) INTO result;
    """
            child_select_statements.append(child_select_statement)

        return "\n".join(child_select_statements)

    def _prepare_columns_for_select(self):
        return_columns = []
        select_columns = []

        for column_name, column in self.columns.items():
            data_type = column['data_type']
            return_columns.append(f'  "{column_name}" {data_type}')
            select_columns.append(f"    st.{column_name}")

        return ",\n".join(return_columns), ",\n".join(select_columns)

    def _find_primary_key(self):
        for column in self.table_structure:
            if column.get('is_primary_key', False):
                return column['column_name']
        return None
