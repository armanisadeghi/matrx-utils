import json
from pathlib import Path
from core import BASE_DIR
from common import vcprint


def get_unique_values(file_path: str, entries_to_get: list) -> dict:
    unique_values = {entry: set() for entry in entries_to_get}
    with open(file_path, 'r') as f:
        data = json.load(f)

    for top_key, top_value in data.items():
        print(top_key)
        entity_fields = top_value.get("entityFields", {})

        for field_name, field_attributes in entity_fields.items():
            for entry in entries_to_get:
                value = field_attributes.get(entry)
                if isinstance(value, (str, int, float)):
                    unique_values[entry].add(value)

    return unique_values


if __name__ == '__main__':
    json_file_path = Path(BASE_DIR) / 'temp/code_generator/initialSchemas.json'
    entries_to_get = ['dataType', 'defaultComponent', 'structure']
    unique_values = get_unique_values(json_file_path, entries_to_get)

    for entry, values in unique_values.items():
        vcprint(values, f"Unique values for {entry}:", pretty=True, color="blue")
