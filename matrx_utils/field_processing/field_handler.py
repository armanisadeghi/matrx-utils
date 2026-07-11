from typing import Dict, Any, List, Optional
import re


def camel_to_snake(name: str) -> str:
    """Convert camelCase string to snake_case."""
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def snake_to_camel(name: str) -> str:
    """Convert snake_case string to camelCase."""
    components = name.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def convert_list_elements(value: list, target_type: type) -> list:
    """Attempt to convert all elements in a list to the target type."""
    result = []
    for item in value:
        try:
            if target_type is str:
                result.append(str(item))
            elif target_type is int:
                result.append(int(item))
            elif target_type is bool:
                result.append(bool(item))
            else:
                result.append(item)  # Fallback for unsupported types
        except (ValueError, TypeError):
            result.append(item)  # Keep original if conversion fails
    return result


def process_field_definitions(
        field_definitions: Dict[str, Dict[str, Any]], convert_camel_case: bool = False,
        fieldname_map: Optional[Dict[str, str]] = None, **kwargs
) -> Dict[str, Any]:
    """Generic function to process field definitions and return a dictionary of values."""
    result = {}

    # Step 1: Apply camel case conversion if enabled
    processed_kwargs = kwargs.copy()
    if convert_camel_case:
        # Create a new dict with snake_case keys when applicable
        camel_case_additions = {}
        for key in kwargs:
            # Convert camelCase keys to snake_case and add to our mapping
            if any(c.isupper() for c in key):  # Only process keys that might be camelCase
                snake_key = camel_to_snake(key)
                camel_case_additions[snake_key] = kwargs[key]

        # Update processed_kwargs with snake_case versions
        # (only if they don't already exist in the original kwargs)
        for snake_key, value in camel_case_additions.items():
            if snake_key not in processed_kwargs:
                processed_kwargs[snake_key] = value

    # Step 2: Apply field mapping if provided
    if fieldname_map:
        # Apply source -> target mapping
        for source_field, target_field in fieldname_map.items():
            if source_field in processed_kwargs:
                processed_kwargs[target_field] = processed_kwargs[source_field]

    # Step 3: Process each defined field
    for field_name, field_spec in field_definitions.items():
        value = None
        found = False

        # Check if the field exists in our processed kwargs
        if field_name in processed_kwargs:
            value = processed_kwargs[field_name]
            found = True

        if found:
            # Check for "default" special value - must be done before type conversion
            # Handle string "default" regardless of expected type
            if value == "default" or value == b"default":
                # If always_include is True, use the default value
                if field_spec.get("always_include", False):
                    result[field_name] = field_spec["default"]
                # Otherwise, skip this field (don't add to result)
                continue

            # Handle None specifically
            elif value is None:
                result[field_name] = None
            else:
                # Try to convert to the expected type if needed
                try:
                    if isinstance(value, field_spec["type"]):
                        # Special handling for lists with specific element types
                        if field_spec["type"] is list and "list_type" in field_spec:
                            if isinstance(value, list):
                                result[field_name] = convert_list_elements(value, field_spec["list_type"])
                            else:
                                # If not a list, try to make it a list with one converted element
                                result[field_name] = convert_list_elements([value], field_spec["list_type"])
                        else:
                            result[field_name] = value
                    else:
                        # Simple type conversions
                        if field_spec["type"] is bool:
                            result[field_name] = bool(value)
                        elif field_spec["type"] is int:
                            result[field_name] = int(value)
                        elif field_spec["type"] is str:
                            result[field_name] = str(value)
                        elif field_spec["type"] is list and "list_type" in field_spec:
                            # Handle non-list input for list fields
                            result[field_name] = convert_list_elements([value], field_spec["list_type"])
                        else:
                            # For complex types like dict or unsupported cases, use as-is
                            result[field_name] = value
                except (ValueError, TypeError):
                    # If conversion fails, use the original value
                    result[field_name] = value

        # If field wasn't provided but should always be included
        elif field_spec.get("always_include", False):
            result[field_name] = field_spec["default"]

    return result


# Process a single object
def process_object_field_definitions(
        field_definitions: Dict[str, Dict[str, Any]], obj: Any, convert_camel_case: bool = False,
        fieldname_map: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Process field definitions for a single object."""
    # Handle dictionaries directly
    if isinstance(obj, dict):
        return process_field_definitions(field_definitions, convert_camel_case=convert_camel_case,
                                         fieldname_map=fieldname_map, **obj)

    # Handle objects with attributes
    elif hasattr(obj, "__dict__"):
        kwargs = vars(obj)
        return process_field_definitions(field_definitions, convert_camel_case=convert_camel_case,
                                         fieldname_map=fieldname_map, **kwargs)

    # For other objects that might have attributes (like namedtuples)
    else:
        try:
            kwargs = {key: getattr(obj, key) for key in dir(obj) if
                      not key.startswith("_") and not callable(getattr(obj, key))}
            return process_field_definitions(
                field_definitions, convert_camel_case=convert_camel_case, fieldname_map=fieldname_map, **kwargs
            )
        except (AttributeError, TypeError):
            # If we can't extract attributes, return empty or default values
            default_result = {k: v["default"] for k, v in field_definitions.items() if v.get("always_include", False)}
            return default_result


# Process a batch of objects
def process_batch_field_definitions(
        field_definitions: Dict[str, Dict[str, Any]],
        objects: List[Any],
        convert_camel_case: bool = False,
        fieldname_map: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Process field definitions for a batch of objects."""
    result = []
    for obj in objects:
        result.append(
            process_object_field_definitions(field_definitions, obj, convert_camel_case=convert_camel_case,
                                             fieldname_map=fieldname_map)
        )
    return result
