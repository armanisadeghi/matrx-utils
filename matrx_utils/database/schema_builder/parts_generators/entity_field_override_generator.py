from matrx_utils.database.constants import get_default_component_props
from collections import OrderedDict
import re
import json
from copy import deepcopy


def merge_component_props(overrides=None):
    """
    Merges provided overrides with the default componentProps while retaining order.
    Returns a TypeScript-friendly string.
    """
    props_without_required_entry = get_default_component_props()
    props_without_required_entry.pop("required", None)  # Avoid KeyError if missing

    merged_props = deepcopy(props_without_required_entry)

    if overrides:  # Ensure overrides is not None
        merged_props.update(overrides)  # Apply overrides

    # Ensure "required" is always last in the object
    merged_props["required"] = False

    # Convert to an OrderedDict to maintain key order
    ordered_props = OrderedDict(merged_props)

    # Convert to a formatted TypeScript object string
    formatted_props = json.dumps(ordered_props, indent=4)

    # Remove quotes from keys to match TypeScript syntax
    formatted_props = re.sub(r'"(\w+)"\s*:', r"\1:", formatted_props)

    return formatted_props


def format_ts_object(ts_object_str):
    """
    Formats a JSON-like string to remove quotes from keys for TypeScript compatibility.
    Ensures TypeScript style object notation.
    """
    return re.sub(r'"(\w+)"\s*:', r"\1:", ts_object_str)


def generate_typescript_field_overrides(entity_name, overrides):
    """
    Generates a TypeScript field overrides object for a given entity.
    If no overrides exist, returns an empty object.
    """
    if not overrides:
        return f"const {entity_name}FieldOverrides: AllFieldOverrides = {{}};"

    ts_template = f"const {entity_name}FieldOverrides: AllFieldOverrides = {{\n"

    for field, value in overrides.items():
        if isinstance(value, str):
            # Handle string-based field overrides (non-componentProps)
            formatted_value = format_ts_object(value)
            ts_template += f"    {field}: {formatted_value},\n"
        elif isinstance(value, dict):
            # Handle componentProps while keeping other field properties
            component_props_override = value.get("componentProps", {})
            merged_component_props = merge_component_props(component_props_override) if component_props_override else None

            # Start field object
            ts_template += f"    {field}: {{\n"

            # Add other field properties (excluding componentProps)
            for key, val in value.items():
                if key != "componentProps":
                    ts_template += f"        {key}: {json.dumps(val)},\n"

            # Add merged componentProps if it exists
            if merged_component_props:
                ts_template += f"        componentProps: {merged_component_props},\n"

            # Close field object
            ts_template += f"    }},\n"

    ts_template += "};\n"
    return ts_template


def generate_full_typescript_file(entity_names, system_overrides):
    """
    Generates the entire TypeScript file as a string, including all entity field overrides
    and the final `ENTITY_FIELD_OVERRIDES` export.
    """
    entity_overrides_blocks = "\n\n".join(generate_typescript_field_overrides(name, system_overrides.get(name, {})) for name in entity_names)

    entity_overrides_list = "\n".join(f"    {name}: {name}FieldOverrides," for name in entity_names)

    entity_overrides_export = f"""
export const ENTITY_FIELD_OVERRIDES: AllEntityFieldOverrides = {{
{entity_overrides_list}
}};
"""

    return entity_overrides_blocks + "\n\n" + entity_overrides_export


# Example Usage
if __name__ == "__main__":
    SYSTEM_OVERRIDES_FIELDS = {
        "dataInputComponent": {"options": {"componentProps": {"subComponent": "optionsManager"}}},
        "aiSettings": {
            "temperature": {
                "defaultComponent": "SPECIAL",
                "componentProps": {
                    "subComponent": "SLIDER",
                    "className": "w-full",
                    "min": 0,
                    "max": 2,
                    "step": 0.01,
                    "numberType": "real",
                },
            }
        },
        "messageTemplate": {
            "role": """{
                isDisplayField: true
            }""",
            "type": """{
                isDisplayField: false
            }""",
        },
    }

    entity_names = [
        "dataInputComponent",
        "aiSettings",
        "messageTemplate",
        "broker",  # No overrides, should generate an empty object
        "unknownEntity",  # Completely unknown entity, should generate an empty object
    ]

    ts_code = generate_full_typescript_file(entity_names, SYSTEM_OVERRIDES_FIELDS)
    print(ts_code)  # Prints the generated TypeScript file content
