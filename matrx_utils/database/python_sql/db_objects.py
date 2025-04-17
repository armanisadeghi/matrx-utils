from matrx_utils.database.client.postgres_connection import execute_sql_query
from collections import defaultdict
from matrx_utils.database.python_sql.table_typescript_relationship import get_ts_object

verbose = False
debug = False
info = True


def get_full_db_objects(schema, database_project):
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
            CASE 
                WHEN c.relkind = 'r' THEN c.reltuples::bigint
                ELSE NULL
            END AS estimated_row_count,
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
            END AS index_count,
            CASE
                WHEN c.relkind = 'v' THEN pg_get_viewdef(c.oid)
                ELSE NULL
            END AS view_definition
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
        WHERE n.nspname = %s AND c.relkind IN ('r', 'v')
    )
    SELECT 
        od.*,
        (
            SELECT json_agg(json_build_object(
                'name', a.attname,
                'position', a.attnum,
                'full_type', pg_catalog.format_type(a.atttypid, a.atttypmod),
                'base_type', t.typname,
                'nullable', NOT a.attnotnull,
                'default', pg_get_expr(d.adbin, d.adrelid),
                'comment', col_description(a.attrelid, a.attnum)
            ) ORDER BY a.attnum)
            FROM pg_attribute a
            LEFT JOIN pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
            LEFT JOIN pg_type t ON a.atttypid = t.oid
            WHERE a.attrelid = od.oid AND a.attnum > 0 AND NOT a.attisdropped
        ) AS columns,
        CASE
            WHEN od.type = 'table' THEN (
                SELECT json_agg(json_build_object(
                    'name', a.attname,
                    'position', a.attnum,
                    'full_type', pg_catalog.format_type(a.atttypid, a.atttypmod),
                    'base_type', t.typname,
                    'domain_type', CASE WHEN t.typtype = 'd' THEN t.typname ELSE NULL END,
                    'enum_labels', CASE WHEN t.typtype = 'e' THEN (SELECT array_agg(enumlabel) FROM pg_enum WHERE enumtypid = t.oid) ELSE NULL END,
                    'is_array', a.attndims > 0,
                    'nullable', NOT a.attnotnull,
                    'default', pg_get_expr(d.adbin, d.adrelid),
                    'character_maximum_length', CASE 
                        WHEN a.atttypid = 1043 AND a.atttypmod > 0 THEN a.atttypmod - 4
                        WHEN a.atttypid = 1043 AND a.atttypmod = -1 THEN NULL
                        WHEN a.atttypid = 25 THEN NULL
                        ELSE NULL 
                    END,
                    'numeric_precision', CASE WHEN a.atttypid = 1700 THEN information_schema._pg_numeric_precision(a.atttypid, a.atttypmod) ELSE NULL END,
                    'numeric_scale', CASE WHEN a.atttypid = 1700 THEN information_schema._pg_numeric_scale(a.atttypid, a.atttypmod) ELSE NULL END,
                    'collation', CASE WHEN a.attcollation <> t.typcollation THEN col.collname ELSE NULL END,
                    'is_identity', a.attidentity <> '',
                    'is_generated', a.attgenerated <> '',
                    'is_primary_key', EXISTS (
                        SELECT 1 FROM pg_constraint p
                        WHERE p.conrelid = a.attrelid AND p.contype = 'p' AND p.conkey @> ARRAY[a.attnum]
                    ),
                    'is_unique', EXISTS (
                        SELECT 1 FROM pg_constraint u
                        WHERE u.conrelid = a.attrelid AND u.contype = 'u' AND u.conkey @> ARRAY[a.attnum]
                    ),
                    'has_index', EXISTS (
                        SELECT 1 
                        FROM pg_index i
                        JOIN unnest(i.indkey) AS key ON key = a.attnum
                        WHERE i.indrelid = a.attrelid AND i.indisprimary = false
                    ),
                    'check_constraints', (
                        SELECT array_agg(pg_get_constraintdef(con.oid))
                        FROM pg_constraint con
                        WHERE con.conrelid = a.attrelid AND con.contype = 'c' AND con.conkey @> ARRAY[a.attnum]
                    ),
                    'foreign_key_reference', (
                        SELECT json_build_object(
                            'table', (SELECT relname FROM pg_class WHERE oid = fk.confrelid),
                            'column', (
                                SELECT attname 
                                FROM pg_attribute ref_att 
                                WHERE ref_att.attrelid = fk.confrelid 
                                AND ref_att.attnum = fk.confkey[array_position(fk.conkey, a.attnum)]
                                AND NOT ref_att.attisdropped
                            )
                        )
                        FROM pg_constraint fk
                        WHERE fk.conrelid = a.attrelid 
                        AND fk.contype = 'f' 
                        AND array_position(fk.conkey, a.attnum) IS NOT NULL
                        LIMIT 1
                    ),
                    'comment', col_description(a.attrelid, a.attnum),
                    'table_name', c.relname
                ) ORDER BY a.attnum)
                FROM pg_attribute a
                LEFT JOIN pg_attrdef d ON (a.attrelid, a.attnum) = (d.adrelid, d.adnum)
                LEFT JOIN pg_type t ON a.atttypid = t.oid
                LEFT JOIN pg_collation col ON col.oid = a.attcollation
                LEFT JOIN pg_class c ON c.oid = a.attrelid
                WHERE a.attrelid = od.oid AND a.attnum > 0 AND NOT a.attisdropped
            )
            ELSE NULL
        END AS table_columns
    FROM object_details od
    ORDER BY od.name;
    """
    return execute_sql_query(query, (schema,), database_project)


def get_db_objects(schema, database_project):
    """
    Retrieves database objects and merges them with TypeScript relationships.
    Also collects base types of columns that have enum labels.

    Args:
        schema (str): Schema name.
        database_project (str): Name of the database project to add.

    Returns:
        tuple: (processed_objects, full_relationships, full_junction_analysis, all_enum_base_types)
               where all_enum_base_types is a set of base types that have enum labels
    """
    if info:
        print("get_db_objects called with", database_project)

    # Retrieve the raw database objects
    objects = get_full_db_objects(schema, database_project)

    ts_objects, full_relationships, full_junction_analysis, overview_analysis = get_ts_object(schema, database_project, additional_schemas=["auth"])

    # Define the fields relevant for views
    relevant_view_fields = {
        "oid",
        "name",
        "type",
        "schema",
        "database",
        "owner",
        "size_bytes",
        "description",
        "columns",
        "view_definition",
    }

    # Set to collect base types that have enum labels
    all_enum_base_types = set()

    processed_objects = []
    for obj in objects:
        # Add database_project to the top-level object
        obj["database_project"] = database_project
        obj["unique_table_id"] = f"{database_project}:{obj['schema']}:{obj['name']}"

        # Process columns if they exist
        if "columns" in obj and obj["columns"]:
            for column in obj["columns"]:
                column["database_project"] = database_project

        # Process table_columns if they exist
        if "table_columns" in obj and obj["table_columns"]:
            for column in obj["table_columns"]:
                column["database_project"] = database_project
                column["unique_column_id"] = f"{database_project}:{obj['schema']}:{obj['name']}:{column['name']}"

                # Check for enum labels and collect base types
                enum_labels = column.get("enum_labels")
                base_type = column.get("base_type")
                # Check if enum_labels exists and is not None/empty
                if enum_labels and enum_labels != "None" and base_type and base_type != "None":
                    # If enum_labels is a string representation of a list, we still want to capture the base_type
                    all_enum_base_types.add(base_type)

        # Merge TypeScript relationships if the table name matches
        table_name = obj.get("name")
        if table_name in ts_objects:
            obj["junction_analysis_ts"] = ts_objects[table_name]

        # For views, keep only the relevant fields
        if obj["type"] == "view":
            processed_obj = {k: v for k, v in obj.items() if k in relevant_view_fields}
        else:
            processed_obj = obj

        # Append the processed object to the result list
        processed_objects.append(processed_obj)

    return (
        processed_objects,
        full_relationships,
        full_junction_analysis,
        all_enum_base_types,
        overview_analysis,
    )


# Mapping of database types to React components
component_mapping = {
    "uuid": "TextInput (readOnly)",
    "character varying(255)": "TextInput",
    "character varying(50)": "TextInput",
    "character varying": "TextInput",
    "text": "Textarea",
    "boolean": "Checkbox",
    "jsonb": "JsonEditor",
    "json": "JsonEditor",
    "bigint": "NumberInput",
    "data_type": "Select",
    "data_source": "Select",
    "data_destination": "Select",
    "smallint": "NumberInput",
    "cognition_matrices": "CustomComponent",
    "destination_component": "Select",
    "real": "NumberInput (decimal)",
    "integer": "NumberInput",
    "timestamp with time zone": "DateTimePicker",
    "uuid[]": "MultiSelect (readOnly)",
    "recipe_status": "Select",
    "jsonb[]": "JsonEditor (array)",
    "broker_role": "Select",
    "function_role": "Select",
    "model_role": "Select",
}


def map_datatypes_to_components(datatypes):
    result = {}
    for datatype, count in datatypes.items():
        if datatype in component_mapping:
            result[datatype] = component_mapping[datatype]
        else:
            result[datatype] = "UnknownComponent"  # Handle unknown types
    return result


def extract_unique_values_and_counts(db_objects_tuple, fields="*"):
    """
    Extracts unique values and their counts for the specified fields from the objects' table columns.

    Args:
    - db_objects_tuple (tuple): Tuple containing (processed_objects, full_relationships, full_junction_analysis)
    - fields (list or str): List of fields for which to extract unique values and counts.
                           If '*' is passed, all fields will be extracted.

    Returns:
    - dict: A dictionary where keys are the field names and values are dictionaries of unique values and their counts.
    """
    # Initialize a dictionary to hold the results for each field
    unique_values_count = defaultdict(lambda: defaultdict(int))

    # Extract the objects from the tuple (first element contains the objects)
    objects = db_objects_tuple[0] if isinstance(db_objects_tuple, tuple) else db_objects_tuple

    # Iterate over the database objects
    for obj in objects:
        # Ensure we process only tables with `table_columns`
        if obj.get("table_columns"):
            for column in obj["table_columns"]:
                # If fields is '*' (all fields), extract all available fields in the column
                if fields == "*":
                    for field, value in column.items():
                        # Convert non-hashable types like dicts or lists to strings
                        if isinstance(value, (dict, list)):
                            value = str(value)
                        unique_values_count[field][value] += 1
                else:
                    # Otherwise, only extract the specified fields
                    for field in fields:
                        if field in column:
                            value = column[field]
                            # Convert non-hashable types like dicts or lists to strings
                            if isinstance(value, (dict, list)):
                                value = str(value)
                            unique_values_count[field][value] += 1

    # Convert defaultdicts back to regular dictionaries for easier usage
    result = {field: dict(value_count) for field, value_count in unique_values_count.items()}

    return result


if __name__ == "__main__":
    from common import vcprint

    schema = "public"
    database_project = "supabase_automation_matrix"
    # results = get_db_objects(schema=schema, database_project=database_project)

    # vcprint(data=results, title='Database Objects', pretty=True, verbose=True, color='blue')

    # # Example 1: Specify the fields you're interested in
    # fields_to_extract = ['full_type', 'base_type', 'is_array', 'nullable', 'default', 'is_primary_key',
    #                      'character_maximum_length']
    # unique_values_and_counts_specific = extract_unique_values_and_counts(results, fields_to_extract)
    # vcprint(data=unique_values_and_counts_specific, title='Unique Values and Counts for Selected Fields', pretty=True,
    #         verbose=True, color='green')

    # # Example 2: Get all unique values and counts for all fields
    # unique_values_and_counts_all = extract_unique_values_and_counts(results, '*')
    # vcprint(data=unique_values_and_counts_all, title='Unique Values and Counts for All Fields', pretty=True,
    #         verbose=True, color='blue')

    # full_type = unique_values_and_counts_specific['full_type']

    # # Generate the mapping of datatypes to React components
    # mapped_components = map_datatypes_to_components(full_type)
    # vcprint(data=mapped_components, title='Mapped Components', pretty=True, verbose=True, color='magenta')

    (
        processed_objects,
        full_relationships,
        full_junction_analysis,
        all_enum_base_types,
        overview_analysis,
    ) = get_db_objects(schema=schema, database_project=database_project)

    vcprint(
        data=processed_objects,
        title="Processed Objects",
        pretty=True,
        verbose=True,
        color="blue",
    )
    # vcprint(data=full_relationships, title='Full Relationships', pretty=True, verbose=True, color='green')
    # vcprint(data=full_junction_analysis, title='Full Junction Analysis', pretty=True, verbose=True, color='yellow')
    # vcprint(data=all_enum_base_types, title='All Enum Base Types', pretty=True, verbose=True, color='red')
    # vcprint(data=overview_analysis, title='Overview Analysis', pretty=True, verbose=True, color='purple')
