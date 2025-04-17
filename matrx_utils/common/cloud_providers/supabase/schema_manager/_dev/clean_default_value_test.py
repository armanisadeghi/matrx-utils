def clean_default_value(value):
    """
    Cleans up the given default value by removing PostgreSQL type casts and
    converting it to an appropriate default value.
    """
    # If the value is a boolean string, return it as is
    if value == "True" or value == "False":
        return value

    # Remove PostgreSQL type casts from strings
    if isinstance(value, str):
        if '::' in value:
            value = value.split('::')[0]
        # Strip the single quotes from the string value
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

    # Attempt to convert the cleaned value to an integer if possible
    try:
        # Return the integer representation if conversion is successful
        return int(value)
    except ValueError:
        # If conversion fails, return the cleaned string value
        return value

# Example usage:
default_values = [
    "'{\"host\": \"ame\"}'::jsonb",
    "'draft'::recipe_status",
    "True",
    "'primary_model'::model_role",
    "False",
    "'none'::data_source",
    "'1'::smallint",
    "gen_random_uuid()",
    "'str'::data_type",
    "'[]'::jsonb"
]

cleaned_values = [clean_default_value(value) for value in default_values]
print(cleaned_values)  # Output: ['{"host": "ame"}', 'draft', 'True', 'primary_model', 'False', 'none', 1, 'gen_random_uuid()', 'str', '[]']
