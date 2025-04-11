from database.python_sql.table_relationships import get_table_relationships


def get_table_relationships_data(schema="public"):
    """
    Retrieves relationship information for all tables in the specified schema.

    Returns a dictionary where each key is a table name, and the value is another dictionary
    containing 'foreign_keys', 'referenced_by', and 'many_to_many' relationships.
    """
    # Fetch raw table relationships from the database
    results = get_table_relationships(schema)

    relationships = {}
    for row in results:
        table_name = row["table_name"]
        relationships[table_name] = {
            "foreign_keys": row["foreign_keys"] or {},
            "referenced_by": row["referenced_by"] or {},
            "many_to_many": [],
        }

    # Detect many-to-many relationship tables
    for table_name, rel_info in relationships.items():
        if len(rel_info["foreign_keys"]) == 2:
            related_tables = list(rel_info["foreign_keys"].keys())
            is_many_to_many = True
            for related_table in related_tables:
                if related_table not in relationships:
                    is_many_to_many = False
                    break
                if table_name not in relationships[related_table]["referenced_by"]:
                    is_many_to_many = False
                    break

            if is_many_to_many:
                for related_table in related_tables:
                    relationships[related_table]["many_to_many"].append(
                        {
                            "junction_table": table_name,
                            "related_table": related_tables[1] if related_tables[0] == related_table else related_tables[0],
                        }
                    )

    return relationships


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
