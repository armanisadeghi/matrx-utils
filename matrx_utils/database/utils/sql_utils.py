import re
import os
from matrx_utils import print_link
import json
import datetime


def clean_default_value(default_value, data_type):
    """
    Clean up the default value by removing type casts and converting to appropriate types.
    """
    if default_value is None:
        return None

    cleaned_value = re.sub(r"::[\w\s]+", "", default_value)

    if cleaned_value.startswith("'") and cleaned_value.endswith("'"):
        return cleaned_value.strip("'")
    if data_type == "integer" or data_type == "smallint":
        try:
            return int(cleaned_value)
        except ValueError:
            return cleaned_value
    elif data_type == "boolean":
        return cleaned_value.lower() == "true"
    return cleaned_value


# def save_to_json(data, dir_override=None, filename_override=None, save_to_local_data=False):
#     if save_to_local_data:
#         directory = os.path.join(BASE_DIR, "code_generator/local_data/current_sql_data")
#     else:
#         directory = dir_override if dir_override else os.path.join(TEMP_DIR, "code_generator/sql_queries")
#
#     if not os.path.exists(directory):
#         os.makedirs(directory)
#
#     filename = filename_override if filename_override else f"db_schema_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
#     filepath = os.path.join(directory, filename)
#
#     with open(filepath, "w") as json_file:
#         json.dump(data, json_file, indent=4)
#
#     print_link(filepath)
#     return filepath


def sql_param_to_psycopg2(sql, params):
    named_params = {k: v for k, v in params.items()}

    def replace_named_param(match):
        key = match.group(1)
        return f"%({key})s"

    modified_sql = re.sub(r":(\w+)", replace_named_param, sql)
    return modified_sql, named_params
