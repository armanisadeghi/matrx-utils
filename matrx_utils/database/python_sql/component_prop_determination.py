import os
from database.python_sql.db_objects import (
    extract_unique_values_and_counts,
    get_db_objects,
)


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


def determine_component_details(database_results_object, fields_to_extract):
    vcprint(
        data=database_results_object,
        title="Database Objects",
        pretty=True,
        verbose=False,
        color="blue",
    )

    # Example 1: Specify the fields you're interested in
    unique_values_and_counts_specific = extract_unique_values_and_counts(database_results_object, fields_to_extract)
    vcprint(
        data=unique_values_and_counts_specific,
        title="Unique Values and Counts for Selected Fields",
        pretty=True,
        verbose=True,
        color="green",
    )

    # Example 2: Get all unique values and counts for all fields
    unique_values_and_counts_all = extract_unique_values_and_counts(database_results_object, "*")
    vcprint(
        data=unique_values_and_counts_all,
        title="Unique Values and Counts for All Fields",
        pretty=True,
        verbose=False,
        color="blue",
    )

    full_type = unique_values_and_counts_specific["full_type"]

    # Generate the mapping of datatypes to React components
    mapped_components = map_datatypes_to_components(full_type)

    vcprint(
        data=mapped_components,
        title="Mapped Components",
        pretty=True,
        verbose=False,
        color="magenta",
    )


fields_to_extract = [
    "full_type",
    "base_type",
    "is_array",
    "nullable",
    "default",
    "is_primary_key",
    "character_maximum_length",
    "enum_labels",
]


if __name__ == "__main__":
    from common import vcprint

    os.system("clear")
    schema = "public"
    database_project = "supabase_automation_matrix"
    results = get_db_objects(schema=schema, database_project=database_project)

    vcprint(data=results, title="Database Objects", pretty=True, verbose=False, color="blue")

    # Example 1: Specify the fields you're interested in
    fields_to_extract = [
        "full_type",
        "base_type",
        "is_array",
        "nullable",
        "default",
        "is_primary_key",
        "character_maximum_length",
        "enum_labels",
    ]
    unique_values_and_counts_specific = extract_unique_values_and_counts(results, fields_to_extract)
    vcprint(
        data=unique_values_and_counts_specific,
        title="Unique Values and Counts for Selected Fields",
        pretty=True,
        verbose=True,
        color="green",
    )

    # Example 2: Get all unique values and counts for all fields
    unique_values_and_counts_all = extract_unique_values_and_counts(results, "*")
    vcprint(
        data=unique_values_and_counts_all,
        title="Unique Values and Counts for All Fields",
        pretty=True,
        verbose=False,
        color="blue",
    )

    full_type = unique_values_and_counts_specific["full_type"]

    # Generate the mapping of datatypes to React components
    mapped_components = map_datatypes_to_components(full_type)

    vcprint(
        data=mapped_components,
        title="Mapped Components",
        pretty=True,
        verbose=False,
        color="magenta",
    )
