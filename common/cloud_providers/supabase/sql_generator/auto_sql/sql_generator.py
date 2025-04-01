import json
import os
import random
from datetime import datetime
from aidream.settings import BASE_DIR, TEMP_DIR
# from common.supabase.async_supabase_crud import AsyncSupabaseClient
from supabase import create_client, Client

from common import print_link, vcprint, pretty_print
from uuid import uuid4

verbose = False



class SQLProcedureGenerator:
    def __init__(self, schema_data=None):
        url: str = os.environ.get("SUPABASE_MATRIX_URL")
        key: str = os.environ.get("SUPABASE_MATRIX_KEY")
        supabase: Client = create_client(url, key)
        self.client = supabase
        if self.client:
            print("Supabase client initialized")
            self.initialized = True

        self.table_name = schema_data.get('table_name')

        # Execute the RPC call and get the schema
        schema = self.client.rpc("get_database_schema_json").execute()
        schema_dict = vars(schema)
        data = schema_dict.get('data', [])
        vcprint(verbose=verbose, pretty=True, data=data, title="Table Names", color='green')
        tables = data.get('tables', [])
        vcprint(verbose=verbose, pretty=True, data=tables, title="Table Names", color='cyan')

        self.schema = next((table for table in tables if table.get('table_name') == self.table_name), None)
        vcprint(verbose=verbose, pretty=True, data=self.schema, title="Table Names", color='blue')

        self.table_structure = self.schema.get('schema', [])

        self.inbound_foreign_keys = self.schema.get('inbound_foreign_keys', [])
        vcprint(verbose=verbose, pretty=True, data=self.inbound_foreign_keys, title="Inbound Foreign Keys", color='green')

        self.outbound_foreign_keys = self.schema.get('outbound_foreign_keys', [])
        vcprint(verbose=verbose, pretty=True, data=self.outbound_foreign_keys, title="Outbound Foreign Keys", color='cyan')

        self.columns = {col['column_name']: col for col in self.table_structure}
        self._prepare_all_values()
        self.drop_statements = {}
        self.core_procedures = {}
        self.test_statements = {}

    def _prepare_all_values(self):
        self.drop_parameters = []
        self.create_parameters = []
        self.required_parameters = []
        self.optional_parameters = []
        self.columns_list = []
        self.values_list = []  # p_list
        self.camel_list = []
        self.return_columns_list = []
        self.test_values = []
        self.test_arguments = []
        self.non_required_test_arguments = []
        self.set_clause = []
        self.camel_test_required = []
        self.camel_test_optional = []

        self.primary_key = None

        for column_name, column in self.columns.items():
            param_name = f"p_{column_name}"
            camel_name = column_name.split('_')[0] + ''.join(word.capitalize() for word in column_name.split('_')[1:])
            data_type = column['data_type']
            is_required = column['is_required']
            options = column.get('options', None)
            is_primary_key = column.get('is_primary_key', False)
            default_value = column.get('default_value', None)




            if is_primary_key:
                self.primary_key = column_name

            self.columns_list.append(f'"{column_name}"') # Normal Values (snake_case)
            self.values_list.append(param_name)  # p_list
            self.camel_list.append(camel_name) # Camel Case
            self.return_columns_list.append(f'  "{column_name}" {data_type}')
            self.drop_parameters.append(f"{param_name} '{data_type}'")

            if not is_primary_key:
                self.set_clause.append(f'"{column_name}" = EXCLUDED."{column_name}"')

            random_time = datetime.now().strftime("%M%S")

            if is_required:
                vcprint(verbose=verbose, data=f"'{column_name}' is required.", color='blue')
                self.required_parameters.append(f"{param_name} '{data_type}'")

                if data_type in ['text', 'character varying']:
                    test_value = f"Sample{column_name}{random_time}"
                    self.test_values.append(f"'{test_value}'")
                    self.test_arguments.append(f"{param_name} := '{test_value}'")
                    self.camel_test_required.append(f"'{camel_name}': '{test_value}'")
                    vcprint(verbose=verbose, data=f"  - Data Type is {data_type}.", color='green')

                elif data_type == 'uuid':
                    uuid_value = uuid4()
                    self.test_values.append(f"'{uuid_value}'")
                    self.test_arguments.append(f"{param_name} := '{uuid_value}'")
                    self.camel_test_required.append(f"'{camel_name}': '{uuid_value}'")
                    vcprint(verbose=verbose, data=f"  - Data Type is {data_type}. Assigned: {uuid_value}", color='green')

                elif data_type == 'bigint':
                    random_value = random.randint(5, 500)
                    self.test_values.append(f"{random_value}")
                    self.test_arguments.append(f"{param_name} := {random_value}")
                    self.camel_test_required.append(f"'{camel_name}': '{random_value}'")

                    vcprint(verbose=verbose, data=f"  - Data Type is {data_type}. Assigned: {random_value}", color='green')

                elif data_type.startswith('jsonb'):
                    random_key = random.choice(["alpha", "beta", "gamma"])
                    json_value = f"jsonb_build_object('{random_key}', '{random_key}{random_time}')"
                    self.test_values.append(json_value)
                    self.test_arguments.append(f"{param_name} := {json_value}")
                    self.camel_test_required.append(f"'{camel_name}': '{json_value}'")
                    vcprint(verbose=verbose, data=f"  - Data Type is {data_type}. Assigned: {random_key}{random_time}", color='green')

                elif data_type.endswith('[]'):
                    random_key = random.choice(["alpha", "beta", "gamma"])
                    array_value = f"ARRAY[jsonb_build_object('{random_key}', '{random_key}{random_time}')]::jsonb[]"
                    self.test_values.append(array_value)
                    self.test_arguments.append(f"{param_name} := {array_value}")
                    self.camel_test_required.append(f"'{camel_name}': '{array_value}'")
                    vcprint(verbose=verbose, data=f"  - Data Type is {data_type}. Assigned: {random_key}{random_time}", color='green')

                elif options:
                    option_value = options[0]
                    self.test_values.append(f"'{option_value}'")
                    self.test_arguments.append(f"{param_name} := '{option_value}'")
                    self.camel_test_required.append(f"'{camel_name}': '{option_value}'")
                    vcprint(verbose=verbose, data=f"  - Column has options: '{option_value}' selected.", color='green')

                else:
                    self.test_values.append("NULL")
                    self.test_arguments.append(f"{param_name} := NULL")
                    self.camel_test_required.append(f"'{camel_name}': 'NULL'")
                    vcprint(verbose=verbose, data=f"  - Else was triggered.", color='red')

            else:
                self.optional_parameters.append(f"{param_name} {data_type} DEFAULT NULL")
                ending = f'::{data_type}'
                if data_type in ['text', 'character varying']:
                    non_req_value = f"NonReq{column_name}{random_time}"
                    self.non_required_test_arguments.append(f"{param_name} := '{non_req_value}'{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_value}"')

                elif data_type == 'uuid':
                    non_req_uuid = uuid4()
                    self.non_required_test_arguments.append(f"{param_name} := '{non_req_uuid}'{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_uuid}"')
                elif data_type == 'smallint':
                    non_req_random_value = random.randint(22, 67)
                    self.non_required_test_arguments.append(f"{param_name} := {non_req_random_value}{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_random_value}"')
                elif data_type == 'bigint':
                    non_req_random_value = random.randint(1000, 10000)
                    self.non_required_test_arguments.append(f"{param_name} := {non_req_random_value}{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_random_value}"')
                elif data_type == 'bigint':
                    non_req_random_value = random.randint(1000, 10000)
                    self.non_required_test_arguments.append(f"{param_name} := {non_req_random_value}{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_random_value}"')
                elif data_type == ('jsonb[]'):
                    non_req_random_key = random.choice(["delta", "epsilon", "zeta"])
                    non_req_array_value = f"array[jsonb_build_object('{non_req_random_key}', '{non_req_random_key}{random_time}')]"
                    self.non_required_test_arguments.append(f"{param_name} := {non_req_array_value}{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_array_value}"')
                elif data_type == ('jsonb'):
                    non_req_random_key = random.choice(["delta", "epsilon", "zeta"])
                    non_req_json_value = json.dumps({
                                                        non_req_random_key: f"{non_req_random_key}{random_time}"})
                    self.non_required_test_arguments.append(f"{param_name} := '{non_req_json_value}'{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_json_value}"')

                elif data_type == 'boolean':
                    non_req_random_bool = random.choice([True, False])
                    self.non_required_test_arguments.append(f"{param_name} := {non_req_random_bool}{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": "{non_req_random_bool}"')


                elif options:
                    non_req_option_value = options[-1]
                    self.non_required_test_arguments.append(f"{param_name} := '{non_req_option_value}'{ending}")
                    self.camel_test_optional.append(f'"{camel_name}": {non_req_option_value}')
                else:
                    self.non_required_test_arguments.append(f"{param_name} := NULL")
                    self.camel_test_optional.append(f'"{camel_name}": "NULL"')

        self.create_parameters = self.required_parameters + self.optional_parameters
        self.formatted_drop_parameters = ',\n  '.join(self.drop_parameters)
        self.formatted_create_parameters = ',\n  '.join(self.create_parameters)
        self.formatted_columns = ',\n  '.join(self.columns_list)
        self.formatted_values = ',\n  '.join(self.values_list)
        self.formatted_return_query = ',\n    '.join([f'inserted_row."{col}"' for col in self.columns.keys()])
        self.formatted_test_values = ',\n  '.join(self.test_values)
        self.formatted_test_arguments = ',\n  '.join(self.test_arguments)
        self.formatted_non_required_test_arguments = ',\n  '.join(self.non_required_test_arguments)
        self.select_return_columns, self.select_columns = self._prepare_columns_for_select()
        self.formatted_set_clause = ',\n    '.join(self.set_clause)
        self.camel_tests_all = ','.join(self.camel_test_required + self.camel_test_optional)
        self.camel_tests_all_json = json.dumps(self.camel_tests_all)

    def _prepare_columns_for_select(self):
        return_columns = []
        select_columns = []

        for column_name, column in self.columns.items():
            data_type = column['data_type']
            return_columns.append(f'  "{column_name}" {data_type}')
            select_columns.append(f"    p.{column_name}")

        return ",\n".join(return_columns), ",\n".join(select_columns)

    def _find_primary_key(self):
        for column in self.table_structure:
            if column.get('is_primary_key', False):
                return column['column_name']
        return None

    def generate_db_to_frontend_conversion(self):
        function_name = f"convert_{self.table_name}_fields"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}({self.table_name}[]);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  input_rows {self.table_name}[]
) RETURNS json AS $$
DECLARE
  result json[];
  row {self.table_name};
BEGIN
  IF array_length(input_rows, 1) IS NULL THEN
    RETURN '[]'::json;
  END IF;

  FOREACH row IN ARRAY input_rows
  LOOP
    result := array_append(result, json_build_object(
      {',\n      '.join([f'"{camel}", row.{snake}' for camel, snake in zip(self.camel_list, self.columns_list)])}
    ));
  END LOOP;

  RETURN array_to_json(result);
END;
$$ LANGUAGE plpgsql;
"""

        # Test Statement
        test_statement = f"""
-- Test the conversion function
SELECT public.{function_name}(ARRAY[(
  {self.formatted_test_values}
)::{self.table_name}]);
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_frontend_to_db_conversion(self):
        function_name = f"convert_frontend_to_db_fields_{self.table_name}"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(json);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  input_json json
) RETURNS TABLE (
  {self.formatted_create_parameters}
) AS $$
BEGIN
  RETURN QUERY SELECT
    {',\n    '.join([f"(CASE WHEN input_json->'{camel}' IS NULL THEN NULL ELSE (input_json->>'{camel}')::{col['data_type']} END) AS {p_name}"
                     for camel, p_name, col in zip(self.camel_list, self.values_list, self.columns.values())])}
  ;
END;
$$ LANGUAGE plpgsql;
"""

        test_statement = f"""
-- Test the conversion function
SELECT * FROM public.{function_name}(
  '{self.camel_tests_all_json}'
);
"""

        # Store parts in respective dictionaries
        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        # Combine parts for the return value
        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_select_procedure(self):
        function_name = f"fetch_all_{self.table_name}"

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}();\n\n"

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

    def generate_fetch_all_id_name_procedure(self):
        function_name = f"fetch_all_id_name_{self.table_name}"

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}();\n\n"

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}()
RETURNS TABLE (
    "id" uuid,
    "name" character varying
) LANGUAGE plpgsql AS $function$
BEGIN
  RETURN QUERY
  SELECT
    p.id,
    p.name
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

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}(\n  {self.columns[self.primary_key]['data_type']}\n);\n\n"

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
    p.{self.primary_key} = record_id;
END;
$function$;
"""

        test_statement = f"SELECT * FROM public.{function_name}();"

        self.drop_statements[function_name] = drop_statement
        self.core_procedures[function_name] = core_procedure
        self.test_statements[function_name] = test_statement

        return f"{drop_statement}\n\n{core_procedure}\n\n{test_statement}"

    def generate_select_paginated_by_name_procedure(self):
        function_name = f"fetch_paginated_by_name_{self.table_name}"
        name_column = 'name'  # Make sure this is the correct column name for sorting

        if name_column not in self.columns:
            raise ValueError(f"Column '{name_column}' is not defined for table {self.table_name}")

        drop_statement = f"DROP FUNCTION IF EXISTS public.{function_name}(text, int, int);"

        core_procedure = f"""
    CREATE OR REPLACE FUNCTION public.{function_name}(
      search_name text,
      limit_val int,
      offset_val int
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
        p.{name_column} ILIKE '%' || search_name || '%'
      ORDER BY
        p.{name_column}
      LIMIT limit_val OFFSET offset_val;
    END;
    $function$;
    """

        test_statement = f"SELECT * FROM public.{function_name}('ENTER-NAME-HERE', 10, 0);"

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

    def generate_upsert_procedure_new(self):
        function_name = f"upsert_{self.table_name}"
        conversion_function_name = f"convert_frontend_to_db_fields_{self.table_name}"
        convert_to_frontend_function_name = f"convert_{self.table_name}_fields"

        drop_statement = f"""
DROP FUNCTION IF EXISTS public.{function_name}(json);
"""

        core_procedure = f"""
CREATE OR REPLACE FUNCTION public.{function_name}(
  input_json json
) RETURNS json
LANGUAGE plpgsql AS $function$
DECLARE
  converted_fields record;
  upserted_row public.{self.table_name}%ROWTYPE;
BEGIN
  SELECT * INTO converted_fields FROM public.{conversion_function_name}(input_json);

  INSERT INTO public.{self.table_name} (
    {self.formatted_columns}
  ) VALUES (
    {', \n'.join([f"converted_fields.p_{col}" for col in self.columns.keys()])}
  )
  ON CONFLICT ("{self.primary_key}") DO UPDATE
  SET
    {self.formatted_set_clause}
  RETURNING * INTO upserted_row;

  RETURN public.{convert_to_frontend_function_name}(ARRAY[upserted_row]);
END;
$function$;
"""

        # Test Statement
        test_statement = f"""
-- Test inserting a new record
SELECT public.{function_name}(
  '{{"id": "{uuid4()}", "name": "upserted_function", "modulePath": "upserted_module_path", "className": "UpsertedClass", "description": "Upserted description", "returnBroker": "{uuid4()}"}}'::json
);

-- Test updating an existing record (replace the ID with a valid one from your database)
SELECT public.{function_name}(
  '{{"id": "REPLACE_WITH_EXISTING_ID", "name": "updated_function", "modulePath": "updated_module_path", "className": "UpdatedClass", "description": "Updated description", "returnBroker": "{uuid4()}"}}'::json
);
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
) RETURNS SETOF jsonb AS $$
DECLARE
  sql_query text;
BEGIN
  sql_query := format('
    SELECT to_jsonb(t)
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
  '{self.table_name}', 1, 5
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


    def sql_output_orchestrator(self):
        """
        Orchestrate the SQL output by combining drop statements, core procedures, and tests.
        """
        drop_output = self.drop_procedure_output_handler()
        core_output = self.core_procedure_output_handler()
        test_output = self.test_procedure_output_handler()

        return f"{drop_output}\n\n{core_output}\n\n{test_output}"

    def drop_procedure_output_handler(self):
        """
        Generate the output for drop statements.
        """
        print(f"\n-- Drop Statements For {self.table_name}--------------------------------------------\n\n")
        print("".join(self.drop_statements.values()))
        print("\n")

    def core_procedure_output_handler(self):
        """
        Generate the output for core procedures.
        """
        print(f"-- Core Procedures For {self.table_name} --------------------------------------------\n\n")
        print("\n".join(self.core_procedures.values()))
        print("\n")

    def test_procedure_output_handler(self):
        # Ordered list of operations to execute
        operation_order = [
            "fetch_all",
            "add_one",
            "delete_one",
            "update_one",
            "upsert",
            "fetch_by_id",
            "delete_one",
            "fetch_filtered",
            "fetch_with_children",
            "fetch_all_with_children",
            "fetch_paginated",
            "delete_one"
        ]

        # Convert the table name to lowercase for consistent key construction
        table_name_lower = self.table_name.lower()

        print(f"-- Test Procedures For {self.table_name} --------------------------------------------\n\n")

        # Iterate over the operation order
        for operation in operation_order:
            # Construct the key for table-specific operations
            if operation in ["add_one", "fetch_by_id", "fetch_all", "upsert"]:
                key = f"{operation}_{table_name_lower}"
            else:
                key = operation

            # Check if the key exists in test_statements and print the corresponding statement
            if key in self.test_statements:
                print(self.test_statements[key])
            else:
                # Print a message if the operation is not defined
                print(f"Operation '{operation}' not defined for table '{self.table_name}'.")


    def print_sql_statements(self):
        """
        Print all SQL statements in the required order.
        """
        self.drop_procedure_output_handler()

        self.core_procedure_output_handler()

        self.test_procedure_output_handler()

        print("-" * 80)

    def extract_schema_info(self):
        column_names = list(self.columns.keys())
        return {
            "table_name": self.table_name,
            "columns": column_names,
            "primary_key": self.primary_key,
            "inbound_foreign_keys": self.inbound_foreign_keys,
            "outbound_foreign_keys": self.outbound_foreign_keys
        }

    def load_schema(self, schema_data):
        schema_file = schema_data.get('schema_file', None)
        table_schema_path = schema_data.get('table_schema_path', None)

        if schema_file:
            full_schema_path = os.path.join(BASE_DIR, schema_file)

            with open(full_schema_path, 'r') as file:
                full_schema = json.load(file)
            for table in full_schema.get('tables', []):
                if table['table_name'] == target_table_name:
                    return table
            raise ValueError(f"Table {target_table_name} not found in full schema.")

        if table_schema_path:
            table_schema_path = os.path.join(BASE_DIR, f"common/utils/auto_sql/{target_table_name}.json")
            with open(table_schema_path, 'r') as file:
                return json.load(file)

        else:
            raise ValueError(f"Invalid schema source: {schema_data}")

    @staticmethod
    def generate_all_procedures(schema_data):
        sql_generator = SQLProcedureGenerator(schema_data)
        select_sql_output = sql_generator.generate_select_procedure()
        select_id_name_output = sql_generator.generate_fetch_all_id_name_procedure()
        select_by_id_sql_output = sql_generator.generate_select_by_id_procedure()
        insert_sql_output = sql_generator.generate_insert_procedure()
        upsert_sql_output = sql_generator.generate_upsert_procedure()
        delete_sql_output = sql_generator.generate_delete_one_procedure()
        update_sql_output = sql_generator.generate_update_one_procedure()
        fetch_paginated_output = sql_generator.generate_fetch_paginated_procedure()
        fetch_filtered_output = sql_generator.generate_fetch_filtered_procedure()
        fetch_with_children_output = sql_generator.generate_fetch_with_children_procedure()
        fetch_all_with_children_output = sql_generator.generate_fetch_all_with_children_procedure()
        fetch_with_parent_output = sql_generator.generate_fetch_with_parent_procedure()
        fetch_all_with_parent_output = sql_generator.generate_fetch_all_with_parent_procedure()
        upsert_new = sql_generator.generate_upsert_procedure_new()
        generate_frontend_to_db_conversion = sql_generator.generate_frontend_to_db_conversion()
        generate_db_to_frontend_conversion = sql_generator.generate_db_to_frontend_conversion()



        sql_generator.print_sql_statements()

        return target_table_name, (
                insert_sql_output + '\n' +
                select_sql_output + '\n' +
                select_by_id_sql_output + '\n' +
                select_id_name_output + '\n' +
                upsert_sql_output + '\n' +
                delete_sql_output + '\n' +
                update_sql_output + '\n' +
                fetch_paginated_output + '\n' +
                fetch_filtered_output + '\n' +
                fetch_with_children_output + '\n' +
                fetch_all_with_children_output + '\n' +
                fetch_with_parent_output + '\n' +
                upsert_new + '\n' +
                fetch_all_with_parent_output + '\n' +
                generate_frontend_to_db_conversion + '\n' +
                generate_db_to_frontend_conversion + '\n' +
                "-- End of SQL Procedures"
        )

    @staticmethod
    def save_output_to_file(output, table_name):
        date_time = datetime.now().strftime("%y%m%d%H%M%S")
        save_path = os.path.join(TEMP_DIR, 'sql_data', f"{table_name}_procedures_{date_time}.sql")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as file:
            file.write(output)
        return save_path

    @staticmethod
    def generate_and_save_procedures(schema_data):
        table_name, output = SQLProcedureGenerator.generate_all_procedures(schema_data)
        save_path = SQLProcedureGenerator.save_output_to_file(output, table_name)
        print(f"SQL functions for table '{table_name}' have been generated and saved to {save_path}.")
        print_link(save_path)


if __name__ == "__main__":
    local_schema_file = r'common/utils/auto_sql/schemas/automation_matrix_schema.json'
    target_table_name = "registered_function"
    schema_data = {
        "source": "live",
        "table_name": target_table_name,
        "schema_file": local_schema_file
    }

    SQLProcedureGenerator.generate_and_save_procedures(schema_data)

''' For Later:
CREATE OR REPLACE FUNCTION public.fetch_child_side_mtm_with_relations(
  p_id uuid
) RETURNS jsonb AS $$
DECLARE
  result jsonb;
BEGIN
  -- Fetch the main record with its parent relations
  WITH main_record AS (
    SELECT to_jsonb(csmm) AS result
    FROM child_side_many_to_many csmm
    WHERE csmm.id = p_id
  ),
  child_relation AS (
    SELECT to_jsonb(cs) AS child_sample
    FROM child_sample cs
    JOIN main_record mr ON cs.id = (mr.result->>'child')::uuid
  ),
  side_relation AS (
    SELECT to_jsonb(st) AS side_table
    FROM side_table st
    JOIN main_record mr ON p.id = (mr.result->>'side')::uuid
  )
  SELECT 
    jsonb_build_object(
      'child_side_many_to_many', mr.result,
      'relations', jsonb_build_object(
        'child_sample', COALESCE(cr.child_sample, 'null'::jsonb),
        'side_table', COALESCE(sr.side_table, 'null'::jsonb)
      )
    ) AS result
  INTO result
  FROM main_record mr
  LEFT JOIN child_relation cr ON true
  LEFT JOIN side_relation sr ON true;

  RETURN result;
END;
$$ LANGUAGE plpgsql;

-- Test the function
SELECT public.fetch_child_side_mtm_with_relations('some-uuid-here');






'''
