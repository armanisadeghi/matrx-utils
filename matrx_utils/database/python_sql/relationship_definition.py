# matrx_utils\database\python_sql\relationship_definition.py
import re
import json
from aidream.settings import TEMP_DIR
import os

from database.python_sql.table_detailed_relationships import (
    get_table_relationships,
    analyze_junction_tables,
    analyze_relationships,
)


def snake_to_camel(snake_str):
    """
    Convert a snake_case string to camelCase.
    """
    components = snake_str.split("_")
    return components[0] + "".join(x.capitalize() for x in components[1:])


def convert_keys_to_camel_case(data):
    """
    Recursively convert all keys and string values in a dictionary or list from snake_case to camelCase.
    """
    if isinstance(data, dict):
        return {snake_to_camel(key): convert_keys_to_camel_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_keys_to_camel_case(item) for item in data]
    elif isinstance(data, str):
        return snake_to_camel(data)
    else:
        return data


def get_relationship_definitions(all_relationships_list):
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
        print(f"Table {joining_table} has {relationship_count} relationships")

    # Convert all keys and nested keys to camelCase
    return convert_keys_to_camel_case(final_relationships)


def flatten_relationships(relationships):
    """
    Flatten the nested relationships structure into a flat dictionary format,
    replacing numeric suffixes with words (One, Two, etc.).
    """
    suffix_mapping = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five"}

    flat_structure = []

    for relationship in relationships:
        joining_entity = relationship["joiningEntity"]
        relationships_data = relationship["relationships"]

        # Base structure with joining table details
        flat_entry = {
            "joiningTable": joining_entity["tableName"],
            "relationshipCount": joining_entity["relationshipCount"],
            "additionalFields": joining_entity["additionalFields"],
            "joiningTablePks": joining_entity["primaryKeyFields"],
        }

        # Add fields for each relationship dynamically
        for idx in range(1, int(joining_entity["relationshipCount"]) + 1):
            # Determine the suffix (One, Two, etc.) or fallback to a number
            suffix = suffix_mapping.get(idx, str(idx))
            rel_key = f"rel{idx}"  # Original relationship key
            ref_field_key = f"rel{idx}Field"  # Original reference field key

            # Create keys using the suffix
            flat_entry[f"ReferenceField{suffix}"] = joining_entity["referenceFields"][ref_field_key]
            flat_entry[f"entity{suffix}"] = relationships_data[rel_key]["tableName"]
            flat_entry[f"entity{suffix}Field"] = relationships_data[rel_key]["referenceField"]
            flat_entry[f"entity{suffix}Pks"] = relationships_data[rel_key]["primaryKeyFields"]

        flat_structure.append(flat_entry)

    return flat_structure


def get_relationship_definition_type():
    """
    Returns the TypeScript type definition as a string.
    """
    return """import { EntityAnyFieldKey, EntityKeys } from "@/types";

export type RelationshipDefinition = {
    joiningTable: EntityKeys;
    relationshipCount: number;
    additionalFields: EntityAnyFieldKey<EntityKeys>[];
    joiningTablePks: EntityAnyFieldKey<EntityKeys>[];
    ReferenceFieldOne: EntityAnyFieldKey<EntityKeys>;
    entityOne: EntityKeys;
    entityOneField: EntityAnyFieldKey<EntityKeys>;
    entityOnePks: EntityAnyFieldKey<EntityKeys>[];
    ReferenceFieldTwo?: EntityAnyFieldKey<EntityKeys>;
    entityTwo?: EntityKeys;
    entityTwoField?: EntityAnyFieldKey<EntityKeys>;
    entityTwoPks?: EntityAnyFieldKey<EntityKeys>[];
    ReferenceFieldThree?: EntityAnyFieldKey<EntityKeys>;
    entityThree?: EntityKeys;
    entityThreeField?: EntityAnyFieldKey<EntityKeys>;
    entityThreePks?: EntityAnyFieldKey<EntityKeys>[];
    ReferenceFieldFour?: EntityAnyFieldKey<EntityKeys>;
    entityFour?: EntityKeys;
    entityFourField?: EntityAnyFieldKey<EntityKeys>;
    entityFourPks?: EntityAnyFieldKey<EntityKeys>[];
};"""


def convert_to_typescript(data):
    """
    Convert a list of dictionaries into a string containing TypeScript constants,
    prefixed with the TypeScript type definition.
    """
    # Get the TypeScript type definition
    type_definition = get_relationship_definition_type()

    # Initialize the constants list
    type_name = "RelationshipDefinition"
    ts_constants = []

    for entry in data:
        constant_name = f"{entry['joiningTable']}RelationshipDefinition"

        # Build the TypeScript object dynamically from the entry
        ts_object_fields = []
        for key, value in entry.items():
            # Convert Python values to TypeScript-friendly syntax
            if isinstance(value, list):
                # Treat list elements as strings if not already wrapped
                value_str = "[" + ", ".join(f"{v}" if not isinstance(v, str) else f'"{v}"' for v in value) + "]"
            elif isinstance(value, str):
                value_str = f'"{value}"'  # Wrap string values in quotes
            else:
                value_str = str(value)  # Leave other values as-is

            # Append each field in "key: value" format
            ts_object_fields.append(f"    {key}: {value_str}")

        # Combine all fields into a single TypeScript object
        ts_object = "{\n" + ",\n".join(ts_object_fields) + "\n}"

        # Create the full TypeScript constant
        ts_constant = f"const {constant_name}: {type_name} = {ts_object};\n"
        ts_constants.append(ts_constant)

    # Combine the type definition with the generated constants
    return type_definition + "\n\n" + "\n".join(ts_constants)


def save_to_file(content, relative_path):
    """
    Save the given content to a file in the specified directory under TEMP_DIR.
    """
    file_path = os.path.join(TEMP_DIR, relative_path)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, "w") as file:
        file.write(content)

    print_link(file_path)


if __name__ == "__main__":
    from common import vcprint, print_link

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

    many_to_many_relationships = get_relationship_definitions(all_relationships_list)
    vcprint(
        data=many_to_many_relationships,
        title="Many-to-Many Relationships",
        pretty=True,
        verbose=True,
        color="yellow",
    )

    flat_relationships = flatten_relationships(many_to_many_relationships)
    vcprint(
        data=flat_relationships,
        title="Flat Relationships",
        pretty=True,
        verbose=True,
        color="green",
    )

    ts_content = convert_to_typescript(flat_relationships)

    # Save the string to a file
    relative_path = "code_generator/code/relationships.ts"
    save_to_file(ts_content, relative_path)
