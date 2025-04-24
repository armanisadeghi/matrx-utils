from matrx_utils.database.python_sql.table_detailed_relationships import (
    get_table_relationships,
    analyze_junction_tables,
    analyze_relationships,
)

verbose = False
debug = False
info = True


def transform_relationships_for_typescript(relationships_data, junction_analysis):
    """
    Transforms database relationship data into a TypeScript-compatible format.

    Args:
        relationships_data (list): Output from get_table_relationships function
        junction_analysis (dict): Output from analyze_junction_tables function

    Returns:
        dict: Structured relationship map matching TypeScript interface
    """
    relationship_map = {}

    # Process each table and its relationships
    for table_data in relationships_data:
        table_name = table_data["table_name"]
        relationship_map[table_name] = {"relationships": {}}

        # Process foreign keys (outgoing relationships)
        if table_data["foreign_keys"]:
            for related_table, details in table_data["foreign_keys"].items():
                if related_table == "self_reference":
                    continue

                relationship_type = details["relationship_type"]

                # Initialize the related table array if it doesn't exist
                if related_table not in relationship_map[table_name]["relationships"]:
                    relationship_map[table_name]["relationships"][related_table] = []

                relationship = {
                    "type": relationship_type,
                    "localField": details["column"],
                    "foreignField": details["foreign_column"],
                }

                # Handle many-to-many relationships
                if relationship_type == "many-to-many":
                    # Find the junction table
                    junction_table = None
                    junction_details = None

                    for jt_name, jt_info in junction_analysis.items():
                        connected_tables = [table["related_table"] for table in jt_info["connected_tables"]]
                        if table_name in connected_tables and related_table in connected_tables:
                            junction_table = jt_name
                            junction_details = jt_info
                            break

                    if junction_table and junction_details:
                        # Find the specific fields in the junction table
                        source_field = None
                        target_field = None

                        for conn in junction_details["connected_tables"]:
                            if conn["related_table"] == table_name:
                                source_field = conn["connecting_column"]
                            elif conn["related_table"] == related_table:
                                target_field = conn["connecting_column"]

                        if source_field and target_field:
                            relationship["throughEntity"] = junction_table
                            relationship["junctionFields"] = {
                                "sourceField": source_field,
                                "targetField": target_field,
                            }

                relationship_map[table_name]["relationships"][related_table].append(relationship)

        # Process referenced_by (incoming relationships)
        if table_data["referenced_by"]:
            for related_table, details in table_data["referenced_by"].items():
                # Skip if we've already processed this relationship
                if related_table in relationship_map[table_name]["relationships"] and any(
                    r["localField"] == details["foreign_column"] for r in relationship_map[table_name]["relationships"][related_table]
                ):
                    continue

                # Initialize the related table array if it doesn't exist
                if related_table not in relationship_map[table_name]["relationships"]:
                    relationship_map[table_name]["relationships"][related_table] = []

                # Determine the relationship type based on constraints
                relationship_type = "one-to-many"  # Default type for incoming references

                relationship = {
                    "type": relationship_type,
                    "localField": details["foreign_column"],
                    "foreignField": details["column"],
                }

                relationship_map[table_name]["relationships"][related_table].append(relationship)

    return relationship_map


def get_ts_object(
    schema="public",
    database_project="supabase_automation_matrix",
    additional_schemas=["auth"],
):
    relationships = get_table_relationships(schema=schema, database_project=database_project)
    junction_analysis, all_relationships = analyze_junction_tables(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
    )
    overview_analysis = analyze_relationships(relationships)

    return (
        transform_relationships_for_typescript(relationships, junction_analysis),
        relationships,
        junction_analysis,
        overview_analysis,
    )


if __name__ == "__main__":
    # Example usage
    schema = "public"
    database_project = "supabase_automation_matrix"
    additional_schemas = ["auth"]

    # Get the relationships data
    relationships = get_table_relationships(schema=schema, database_project=database_project)

    # Get junction table analysis
    junction_analysis, all_relationships = analyze_junction_tables(
        schema=schema,
        database_project=database_project,
        additional_schemas=additional_schemas,
    )

    # Transform the data
    typescript_structure = transform_relationships_for_typescript(relationships, junction_analysis)

    overview_analysis = analyze_relationships(relationships)

    # You can now use vcprint or json.dumps to view the result
    from matrx_utils import vcprint

    vcprint(
        data=overview_analysis,
        title="Relationship Overview Analysis",
        pretty=True,
        verbose=True,
        color="yellow",
    )

    vcprint(
        data=typescript_structure,
        title="TypeScript Relationship Map",
        pretty=True,
        verbose=True,
        color="cyan",
    )
    vcprint(
        data=relationships,
        title="Relationships Data",
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
