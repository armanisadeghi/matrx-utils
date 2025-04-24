import json
from uuid import UUID
from enum import Enum
import datetime
from dataclasses import is_dataclass, asdict
import types
from decimal import Decimal
# No ORM imports at the top level

LOCAL_DEBUG = False

def _convert_recursive(data):
    """
    Recursive helper function to convert nested data structures into basic
    Python types (dict, list, str, int, float, bool, None), including
    parsing of embedded JSON strings.
    """
    # Moved imports inside to handle potential circular dependencies or runtime availability
    from matrx_utils.database.orm.core.fields import Field
    from matrx_utils.database.orm.core.extended import BaseDTO
    from matrx_utils.database.orm.core.base import Model
    # Import psycopg2 types if needed for specific checks, otherwise handle via str()
    try:
        # Example: If you need to explicitly handle RealDictRow
        from psycopg2.extras import RealDictRow
        HAS_PSYCOPG2 = True
    except ImportError:
        HAS_PSYCOPG2 = False
        RealDictRow = None # Define it as None if not available

    # 1. Handle specific complex object types first -> convert to dict/list/value
    #    The recursive call will then handle the contents.

    # Handle dataclasses (must come before generic hasattr checks)
    if is_dataclass(data) and not isinstance(data, type):
        return _convert_recursive(asdict(data))

    # Handle your custom ORM/DTO
    if isinstance(data, BaseDTO) and type(data) is not BaseDTO:
        try:
            return _convert_recursive(data.to_dict())
        except Exception as e:
            print(f"Warning: Failed calling to_dict() on BaseDTO {type(data)}: {e}")
            # Fall through

    # Handle your custom ORM Model instances
    if isinstance(data, Model):
        try:
            return _convert_recursive(data.to_dict())
        except Exception as e:
            print(f"Warning: Failed calling to_dict() on Model {type(data)}: {e}")
            # Fall through

    # Handle your custom ORM Field instances
    if isinstance(data, Field):
        try:
            return _convert_recursive(data.to_dict())
        except Exception as e:
            print(f"Warning: Failed calling to_dict() on ORM Field {type(data)}: {e}")
            # Fall through

    # Handle psycopg2 RealDictRow if imported
    # Convert it to a regular dict before general dict handling
    if HAS_PSYCOPG2 and isinstance(data, RealDictRow):
         # RealDictRow acts like a dict, so convert and recurse
        return _convert_recursive(dict(data))

    # SimpleNamespace needs explicit dict conversion
    if isinstance(data, types.SimpleNamespace):
        return {str(key): _convert_recursive(value) for key, value in data.__dict__.items()}

    # 2. Handle collection types (recurse on elements/values)

    # Convert sets to lists
    if isinstance(data, set):
        return [_convert_recursive(item) for item in data]

    # Recursively handle dictionaries (must come after specific dict-like types like RealDictRow)
    if isinstance(data, dict):
        return {str(k): _convert_recursive(v) for k, v in data.items()}

    # Recursively handle lists and tuples
    if isinstance(data, (list, tuple)):
        return [_convert_recursive(item) for item in data]

    # 3. Handle specific atomic types needing conversion to basic types

    if isinstance(data, Enum):
        return _convert_recursive(data.value)
    if isinstance(data, UUID):
        return str(data)
    if isinstance(data, datetime.datetime):
        return data.isoformat()
    if isinstance(data, datetime.date):
        return data.isoformat()
    if isinstance(data, datetime.time):
        return data.isoformat()
    if isinstance(data, Decimal):
        return float(data)
    if isinstance(data, (bytes, bytearray)):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return f"<binary data length={len(data)}>"

    # 4. Handle basic Python types (int, float, bool, None) AND STRINGS
    #    For strings, attempt to parse if they look like JSON.
    if isinstance(data, (int, float, bool, type(None))):
        return data
    elif isinstance(data, str):
        # <<<--- MODIFIED STRING HANDLING --- >>>
        stripped_data = data.strip()
        # Check if it looks like a JSON object or array
        if len(stripped_data) > 1 and stripped_data.startswith(("{", "[")) and stripped_data.endswith(("}", "]")):
            try:
                # Attempt to parse the string as JSON
                parsed_json = json.loads(data)
                # If parsing succeeds, recursively convert the parsed structure
                # This handles nested JSON strings
                return _convert_recursive(parsed_json)
            except (json.JSONDecodeError, TypeError):
                # If parsing fails (e.g., it's not valid JSON, maybe a Python repr),
                # treat it as a regular string. Pass prevents falling through.
                pass
        # Return the original string if it wasn't parseable JSON or didn't look like it
        return data
        # <<<--- END MODIFIED STRING HANDLING --- >>>

    # 5. Handle types themselves
    if isinstance(data, type):
        return f"<class '{data.__module__}.{data.__name__}'>"

    # 6. Fallback for other objects with common serialization methods
    # Check AFTER specific types like Model, DTO, Field, RealDictRow
    if hasattr(data, "to_dict") and callable(data.to_dict):
        try:
            return _convert_recursive(data.to_dict())
        except Exception as e:
            print(f"Warning: Failed calling fallback to_dict() on {type(data)}: {e}")
            # Fall through
    if hasattr(data, "dict") and callable(data.dict): # Common in Pydantic
        try:
            return _convert_recursive(data.dict())
        except Exception as e:
            print(f"Warning: Failed calling fallback dict() on {type(data)}: {e}")
            # Fall through

    # 7. Final fallback: Convert any remaining unhandled types to string
    # This will catch types like RealDictRow if psycopg2 isn't installed or handled above
    try:
        # Using repr() might be slightly more informative than str() for unknown types
        return repr(data)
    except Exception as e:
        print(f"Error: Could not convert object of type {type(data).__name__} to string/repr: {e}")
        return f"<Unconvertible type: {type(data).__name__}>"


# --- validate_basic_types remains the same ---
def validate_basic_types(data, path="root"):
    """
    Recursively checks if the nested data structure contains only basic
    Python types allowed in JSON (dict, list, str, int, float, bool, None)
    and that dictionary keys are strings. Prints errors if violations found.
    Returns True if valid, False otherwise.
    """
    basic_types = (str, int, float, bool, type(None))

    if isinstance(data, basic_types):
        return True
    elif isinstance(data, list):
        all_valid = True
        for i, item in enumerate(data):
            item_path = f"{path}[{i}]"
            if isinstance(item, (list, dict)):
                if not validate_basic_types(item, item_path):
                    all_valid = False
            elif not isinstance(item, basic_types):
                print(f"Validation Error at {item_path}: Value '{repr(item)}' is of non-basic type {type(item).__name__}")
                all_valid = False
        return all_valid
    elif isinstance(data, dict):
        all_valid = True
        for key, value in data.items():
            key_path = f"{path}.key('{key}')"
            value_path = f"{path}.{key}"

            if not isinstance(key, str):
                print(f"Validation Error at {key_path}: Key '{repr(key)}' is not a string (type: {type(key).__name__})")
                all_valid = False

            if isinstance(value, (list, dict)):
                if not validate_basic_types(value, value_path):
                    all_valid = False
            elif not isinstance(value, basic_types):
                print(f"Validation Error at {value_path}: Value '{repr(value)}' is of non-basic type {type(value).__name__}")
                all_valid = False
        return all_valid
    else:
        print(f"Validation Error at {path}: Data '{repr(data)}' is of non-basic type {type(data).__name__}")
        return False

# --- to_matrx_json remains the same ---
def to_matrx_json(data=None):
    """
    Converts a Python object, including nested structures and custom types
    (like specific DTOs/Fields via .to_dict(), dataclasses), into a structure
    containing only basic Python types (dict, list, str, int, float, bool, None),
    suitable for JSON serialization. Handles embedded JSON strings.

    Handles common types like Enums, UUIDs, datetimes/dates/times, Decimals,
    sets, bytes, and objects with .to_dict()/.dict().
    """
    initial_input = data
    local_debug_internal = False # Set to True for debugging this specific function

    # Handle if the initial input is a string that looks like JSON
    # This specifically targets the *top-level* input being a JSON string.
    # Nested JSON strings are handled within _convert_recursive.
    if isinstance(initial_input, str):
        stripped_input = initial_input.strip()
        if len(stripped_input) > 1 and stripped_input.startswith(("{", "[")) and stripped_input.endswith(("}", "]")):
            if local_debug_internal: print("Input is a string that looks like JSON.")
            try:
                parsed_data = json.loads(initial_input)
                # Now convert the parsed structure recursively
                data = parsed_data  # Use the parsed data for the main conversion
                if local_debug_internal: print("Input string successfully parsed as JSON.")
            except (json.JSONDecodeError, TypeError):
                # If JSON parsing fails, treat it as a regular string
                if local_debug_internal: print("Input string looked like JSON but failed to parse. Treating as plain string.")
                # 'data' remains 'initial_input' (the original string)
                pass # Let _convert_recursive handle it as a plain string below
        else:
             if local_debug_internal: print("Input is a string, but doesn't look like JSON.")
             # 'data' remains 'initial_input'

    # Perform the main recursive conversion
    if local_debug_internal: print(f"Starting recursive conversion on: {type(data)}")
    converted_data = _convert_recursive(data)

    # Final validation step to ensure the output is clean
    if LOCAL_DEBUG is True:
        print("\n--- Running Final Validation ---")
    if not validate_basic_types(converted_data):
        raise ValueError("Conversion result validation failed: Contains non-basic Python types or invalid keys.")
    else:
        if LOCAL_DEBUG is True:
            print("Validation successful: All elements are basic Python types (str, int, float, bool, None, list, dict) with string keys.")
            print("---\n")

    return converted_data

