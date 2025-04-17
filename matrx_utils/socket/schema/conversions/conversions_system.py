import json
from typing import Any

from matrx_utils.socket.schema.conversions.conversion_registry import CUSTOM_CONVERSIONS


def convert_value(value: Any, expected_type: str, conversion: str = None):
    try:
        if conversion and conversion in CUSTOM_CONVERSIONS:
            return CUSTOM_CONVERSIONS[conversion](value)

        if value is None:
            return value

        # Standard type conversions
        if expected_type == "string":
            return str(value)
        elif expected_type == "integer":
            return int(value) if isinstance(value, (str, float)) and str(value).isdigit() else value
        elif expected_type == "float":
            return float(value) if isinstance(value, (str, int)) and str(value).replace(".", "", 1).isdigit() else value
        elif expected_type == "boolean":
            if isinstance(value, str):
                return value.lower() in ["true", "1"]
            return bool(value)
        elif expected_type == "array":
            return value if isinstance(value, list) else [value]
        elif expected_type == "object":
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
            return value
        return value
    except (ValueError, TypeError):
        return value
