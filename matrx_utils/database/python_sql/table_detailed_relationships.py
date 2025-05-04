# matrx_utils\database\python_sql\table_detailed_relationships.py
from matrx_utils.database.client.postgres_connection import execute_sql_query


verbose = False
debug = False
info = True


def get_table_relationships(schema, database_project):
    """
    Executes the SQL query to fetch relationship information for all tables in the specified schema.

    Parameters:
        schema (str): The schema name for which to fetch table relationships.
        database_project (str): The name of the database configuration to use for the connection

    Returns:
        List of dictionaries with table relationship data including relationship types.
    """

    print("get_table_relationships called with", database_project)

    query = """
    WITH fk_info AS (
        SELECT
            tc.table_schema,
            tc.constraint_name,
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            -- Check for unique constraints and primary keys
            EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc2
                WHERE tc2.table_schema = tc.table_schema
                  AND tc2.table_name = tc.table_name
                  AND tc2.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
                  AND tc2.constraint_name IN (
                      SELECT constraint_name
                      FROM information_schema.key_column_usage
                      WHERE table_schema = tc.table_schema
                        AND table_name = tc.table_name
                        AND column_name = kcu.column_name
                  )
            ) AS has_unique_constraint,
            EXISTS (
                SELECT 1
                FROM information_schema.table_constraints tc2
                WHERE tc2.table_schema = tc.table_schema
                  AND tc2.table_name = ccu.table_name
                  AND tc2.constraint_type IN ('PRIMARY KEY', 'UNIQUE')
                  AND tc2.constraint_name IN (
                      SELECT constraint_name
                      FROM information_schema.key_column_usage
                      WHERE table_schema = tc.table_schema
                        AND table_name = ccu.table_name
                        AND column_name = ccu.column_name
                  )
            ) AS referenced_has_unique_constraint,
            -- Check for junction tables (many-to-many)
            (
                SELECT COUNT(*)
                FROM information_schema.table_constraints tc2
                WHERE tc2.table_schema = tc.table_schema
                  AND tc2.table_name = tc.table_name
                  AND tc2.constraint_type = 'FOREIGN KEY'
            ) > 1 AS is_junction_table
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
                'foreign_column', fk.foreign_column_name,
                'relationship_type', 
                CASE 
                    WHEN fk.foreign_table_name = at.table_name THEN 'self-referential'
                    WHEN fk.is_junction_table THEN 'many-to-many'
                    WHEN fk.has_unique_constraint AND fk.referenced_has_unique_constraint THEN 'one-to-one'
                    WHEN NOT fk.has_unique_constraint THEN 'many-to-one'
                    WHEN fk.has_unique_constraint THEN 'one-to-many'
                    ELSE 'undefined'
                END
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


def analyze_junction_tables(schema, database_project, additional_schemas=None):
    """
    Analyzes junction tables to identify the tables they connect and additional fields they contain.
    Also determines the relationship types between tables.
    """
    schemas = [schema]
    if additional_schemas:
        schemas.extend(additional_schemas)

    query = """
    WITH junction_candidates AS (
        SELECT 
            tc.table_schema,
            tc.table_name,
            COUNT(*) as fk_count
        FROM 
            information_schema.table_constraints tc
        WHERE 
            tc.table_schema = ANY(%s::text[])
            AND tc.constraint_type = 'FOREIGN KEY'
        GROUP BY 
            tc.table_schema, tc.table_name
        HAVING 
            COUNT(*) >= 2
    ),
    foreign_key_details AS (
        SELECT DISTINCT
            tc.table_schema,
            tc.table_name,
            kcu.column_name as fk_column,
            ccu.table_schema as referenced_schema,
            ccu.table_name as referenced_table,
            ccu.column_name as referenced_column,
            EXISTS (
                SELECT 1 
                FROM information_schema.table_constraints uc
                JOIN information_schema.key_column_usage kcu2 
                    ON uc.constraint_name = kcu2.constraint_name
                WHERE uc.table_schema = tc.table_schema 
                    AND uc.table_name = tc.table_name
                    AND uc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
                    AND kcu2.column_name = kcu.column_name
            ) as has_unique_constraint,
            EXISTS (
                SELECT 1 
                FROM information_schema.table_constraints uc
                JOIN information_schema.key_column_usage kcu2 
                    ON uc.constraint_name = kcu2.constraint_name
                WHERE uc.table_schema = ccu.table_schema 
                    AND uc.table_name = ccu.table_name
                    AND uc.constraint_type IN ('UNIQUE', 'PRIMARY KEY')
                    AND kcu2.column_name = ccu.column_name
            ) as referenced_has_unique_constraint
        FROM 
            information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu
                ON ccu.constraint_name = tc.constraint_name
        WHERE 
            tc.table_schema = ANY(%s::text[])
            AND tc.constraint_type = 'FOREIGN KEY'
    ),
    primary_key_columns AS (
        SELECT 
            kcu.table_schema,
            kcu.table_name,
            kcu.column_name as pk_column
        FROM 
            information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu 
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
        WHERE 
            tc.table_schema = ANY(%s::text[])
            AND tc.constraint_type = 'PRIMARY KEY'
    ),
    additional_columns AS (
        SELECT 
            c.table_schema,
            c.table_name,
            array_agg(DISTINCT c.column_name ORDER BY c.column_name) as additional_fields
        FROM 
            information_schema.columns c
            JOIN junction_candidates jc 
                ON c.table_name = jc.table_name 
                AND c.table_schema = jc.table_schema
            LEFT JOIN foreign_key_details fkd 
                ON c.table_name = fkd.table_name 
                AND c.table_schema = fkd.table_schema
                AND c.column_name = fkd.fk_column
            LEFT JOIN primary_key_columns pkc
                ON c.table_name = pkc.table_name
                AND c.table_schema = pkc.table_schema
                AND c.column_name = pkc.pk_column
        WHERE 
            c.table_schema = ANY(%s::text[])
            AND fkd.fk_column IS NULL
            AND pkc.pk_column IS NULL
        GROUP BY 
            c.table_schema, c.table_name
    )
    SELECT 
        jc.table_schema,
        jc.table_name,
        json_agg(
            json_build_object(
                'table', fkd.table_name,
                'table_pks', (
                    SELECT array_agg(DISTINCT pkc_table.pk_column)
                    FROM primary_key_columns pkc_table
                    WHERE pkc_table.table_schema = fkd.table_schema
                    AND pkc_table.table_name = fkd.table_name
                ),
                'related_table', fkd.referenced_table,
                'related_pks', (
                    SELECT array_agg(DISTINCT pkc_related.pk_column)
                    FROM primary_key_columns pkc_related
                    WHERE pkc_related.table_schema = fkd.referenced_schema
                    AND pkc_related.table_name = fkd.referenced_table
                ),
                'related_schema', fkd.referenced_schema,
                'connecting_column', fkd.fk_column,
                'referenced_column', fkd.referenced_column,
                'relationship_type',
                CASE 
                    WHEN fkd.referenced_table = fkd.table_name THEN 'self-referential'
                    WHEN jc.fk_count >= 2 THEN 'many-to-many'
                    WHEN fkd.has_unique_constraint AND fkd.referenced_has_unique_constraint THEN 'one-to-one'
                    WHEN NOT fkd.has_unique_constraint THEN 'many-to-one'
                    WHEN fkd.has_unique_constraint THEN 'one-to-many'
                    ELSE 'undefined'
                END
            )
        ) as connected_tables,
        COALESCE(ac.additional_fields, ARRAY[]::text[]) as additional_fields,
        array_agg(DISTINCT pkc.pk_column) FILTER (WHERE pkc.pk_column IS NOT NULL) as primary_keys
    FROM 
        junction_candidates jc
        JOIN foreign_key_details fkd 
            ON jc.table_name = fkd.table_name 
            AND jc.table_schema = fkd.table_schema
        LEFT JOIN additional_columns ac 
            ON jc.table_name = ac.table_name 
            AND jc.table_schema = ac.table_schema
    LEFT JOIN primary_key_columns pkc
            ON jc.table_name = pkc.table_name 
            AND jc.table_schema = pkc.table_schema
    GROUP BY 
        jc.table_schema, jc.table_name, ac.additional_fields;
    """

    results = execute_sql_query(query, (schemas, schemas, schemas, schemas), database_project)

    # Transform the results into a more readable format
    analyzed_junctions = {}
    all_relationships = []
    for row in results:
        table_name = row["table_name"]

        # Convert PostgreSQL array string to Python list
        additional_fields = row["additional_fields"]
        if isinstance(additional_fields, str):
            # Remove the curly braces and split the string
            additional_fields = additional_fields.strip("{}").split(",")
            # Remove any empty strings
            additional_fields = [field for field in additional_fields if field]

        # Convert PostgreSQL array of primary keys to Python list
        primary_keys = row["primary_keys"]
        if isinstance(primary_keys, str):
            primary_keys = primary_keys.strip("{}").split(",")
            primary_keys = [key.strip() for key in primary_keys if key.strip()]

        analyzed_junctions[table_name] = {
            "schema": row["table_schema"],
            "connected_tables": row["connected_tables"],
            "additional_fields": additional_fields,
            "primary_keys": primary_keys,
        }

        # Extract relationships from connected_tables and add to all_relationships
        if row["connected_tables"]:
            for relationship in row["connected_tables"]:
                # Create a copy of the relationship and add the additional_fields
                relationship_with_fields = relationship.copy()
                relationship_with_fields["table_additional_fields"] = additional_fields
                all_relationships.append(relationship_with_fields)

    return analyzed_junctions, all_relationships


def analyze_relationships(results):
    """
    Analyzes the relationship data and provides a summary for each table.

    Parameters:
        results (list): The results from get_table_relationships

    Returns:
        dict: A summary of relationships by table
    """
    summary = {}

    relationship_types = {
        "self-referential": set(),
        "many-to-many": set(),
        "one-to-one": set(),
        "many-to-one": set(),
        "one-to-many": set(),
        "undefined": set(),
        "inverse_references": set(),
    }

    for table_data in results:
        table_name = table_data["table_name"]
        summary[table_name] = {
            "self-referential": [],
            "many-to-many": [],
            "one-to-one": [],
            "many-to-one": [],
            "one-to-many": [],
            "undefined": [],
            "inverse_references": [],
        }

        # Process foreign keys
        if table_data["foreign_keys"]:
            for related_table, details in table_data["foreign_keys"].items():
                if related_table != "self_reference":
                    rel_type = details["relationship_type"]
                    summary[table_name][rel_type].append(related_table)
                    relationship_types[rel_type].add(f"{table_name} → {related_table}")

        # Process referenced_by
        if table_data["referenced_by"]:
            for related_table in table_data["referenced_by"].keys():
                summary[table_name]["inverse_references"].append(related_table)
                relationship_types["inverse_references"].add(f"{related_table} → {table_name}")

    # Print summary
    if verbose:
        print("\n=== Database Relationship Analysis ===\n")

    if verbose:
        print("Overall Statistics:")
        for rel_type, relationships in relationship_types.items():
            if relationships:
                print(f"\n{rel_type.upper()} Relationships ({len(relationships)}):")
            for rel in sorted(relationships):
                print(f"  {rel}")

    if verbose:
        print("\n\nPer-Table Analysis:")
        for table_name, rels in summary.items():
            print(f"\n{table_name}:")
            for rel_type, tables in rels.items():
                if tables:
                    print(f"  {rel_type}:")
                    for related_table in sorted(tables):
                        print(f"    → {related_table}")

    return summary


def analyze_many_to_many_relationships(all_relationships_list):
    # First pass - group relationships by joining table
    joined_relationships = {}
    for relationship in all_relationships_list:
        joining_table = relationship["table"]

        if joining_table not in joined_relationships:
            # Initialize the entry for this joining table
            joined_relationships[joining_table] = {
                "joiningEntity": {
                    "tableName": joining_table,
                    "primaryKeyFields": relationship["table_pks"],
                    "additionalFields": relationship["table_additional_fields"],
                    "referenceFields": {},  # Dictionary to store field mappings
                },
                "relatedEntities": {},  # Dictionary to store related entities
            }

        # Generate a unique index for this relationship
        rel_index = len(joined_relationships[joining_table]["relatedEntities"]) + 1

        # Add this relationship's info
        joined_relationships[joining_table]["relatedEntities"][f"rel_{rel_index}"] = {
            "tableName": relationship["related_table"],
            "referenceField": relationship["referenced_column"],
            "primaryKeyFields": relationship["related_pks"],
        }
        # Store the reference field with the same index
        joined_relationships[joining_table]["joiningEntity"]["referenceFields"][f"rel_{rel_index}_field"] = relationship["connecting_column"]

    # Convert to final format with dynamic number of relationships
    final_relationships = []
    for joining_table, data in joined_relationships.items():
        relationship_count = len(data["relatedEntities"])

        final_rel = {
            "joiningEntity": {
                "tableName": data["joiningEntity"]["tableName"],
                "referenceFields": data["joiningEntity"]["referenceFields"],
                "relationshipCount": relationship_count,
                "primaryKeyFields": data["joiningEntity"]["primaryKeyFields"],
                "additionalFields": data["joiningEntity"]["additionalFields"],
            },
            "relationships": data["relatedEntities"],
        }
        final_relationships.append(final_rel)

        # Log information about the number of relationships
        if verbose:
            print(f"Table {joining_table} has {relationship_count} relationships")

    return final_relationships


if __name__ == "__main__":
    from common import vcprint

    schema = "public"
    database_project = "supabase_automation_matrix"
    additional_schemas = ["auth"]

    relationships = get_table_relationships(schema=schema, database_project=database_project)
    junction_analysis, all_relationships_list = analyze_junction_tables(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
    )

    vcprint(
        data=relationships,
        title="Table Relationships",
        pretty=True,
        verbose=True,
        color="green",
    )

    # New analysis output
    analysis = analyze_relationships(relationships)
    vcprint(
        data=analysis,
        title="Relationship Analysis",
        pretty=True,
        verbose=True,
        color="yellow",
    )

    vcprint(
        data=junction_analysis,
        title="Junction Table Analysis",
        pretty=True,
        verbose=True,
        color="green",
    )

    vcprint(
        data=all_relationships_list,
        title="All Relationships List",
        pretty=True,
        verbose=True,
        color="blue",
    )

    many_to_many_relationships = analyze_many_to_many_relationships(all_relationships_list)
    vcprint(
        data=many_to_many_relationships,
        title="Many-to-Many Relationships",
        pretty=True,
        verbose=True,
        color="yellow",
    )
