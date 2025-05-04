# matrx_utils\socket\schema\schema_processor.py
from enum import Enum
import os
from typing import Dict, Any

from matrx_utils.socket.schema.context_registry import SERVICE_DEFINITIONS, STANDARD_FIELD_DEFINITIONS
from matrx_utils.socket.schema.validations.validation_registry import (
    CUSTOM_VALIDATIONS,
    VALIDATION_REGISTRY,
)
from matrx_utils.socket.schema.validations.validations_system import validate_enum
from matrx_utils.socket.schema.conversions.conversions_system import convert_value
from matrx_utils import vcprint

STANDARD_FIELDS = ["user_id", "custom_event_name"]



def validate_and_structure_data(data: Dict[str, Any], definition: Dict[str, Any], user_id: str, depth: int = 0):
    """Validates and structures data according to the provided definition, handling nested references and arrays.

    Args:
        data: The input data to validate.
        definition: The schema definition.
        depth: Tracks recursion depth for nested validation.

    Returns:
        A dictionary with 'data' (structured data) and 'errors' (validation errors).
    """
    structured_data = {}
    errors = {}

    for field, rules in definition.items():
        value = data.get(field, rules["DEFAULT"])
        expected_type = rules.get("DATA_TYPE")
        validation_rule = rules.get("VALIDATION")
        conversion = rules.get("CONVERSION")
        reference = rules.get("REFERENCE")

        if rules["DEFAULT"] == "socket_internal_user_id":
            value = user_id

        converted_value = convert_value(value, expected_type, conversion)

        if rules["REQUIRED"] and converted_value is None:
            errors[field] = "Missing required field"
            continue

        if reference:
            if isinstance(reference, str):
                ref_definition = ValidationSystem.DEFINITIONS.get(reference)
                if not ref_definition:
                    errors[field] = f"Invalid reference: {reference}"
                    continue
                if isinstance(converted_value, dict):
                    nested_result = validate_and_structure_data(converted_value, ref_definition, user_id, depth + 1)
                    if nested_result["errors"]:
                        errors[field] = nested_result["errors"]
                    converted_value = nested_result["data"]
                elif isinstance(converted_value, list) and expected_type == "array":
                    converted_value = []
                    for idx, item in enumerate(value or []):
                        if isinstance(item, dict):
                            nested_result = validate_and_structure_data(item, ref_definition, user_id, depth + 1)
                            if nested_result["errors"]:
                                errors[f"{field}[{idx}]"] = nested_result["errors"]
                            converted_value.append(nested_result["data"])
                        else:
                            errors[f"{field}[{idx}]"] = f"Expected object, got {type(item).__name__}"
                elif converted_value is not None:
                    errors[field] = f"Expected {expected_type}, got {type(converted_value).__name__}"

        if validation_rule and not errors.get(field):
            if validation_rule in CUSTOM_VALIDATIONS:
                try:
                    CUSTOM_VALIDATIONS[validation_rule](converted_value)
                except Exception as e:
                    errors[field] = f"Validation failed: {str(e)}"
            elif validation_rule in VALIDATION_REGISTRY:
                validator = VALIDATION_REGISTRY[validation_rule]
                try:
                    if isinstance(validator, type) and issubclass(validator, Enum):
                        validate_enum(converted_value, validator)
                    elif callable(validator):
                        validator(converted_value)
                except Exception as e:
                    errors[field] = f"Validation failed: {str(e)}"

        structured_data[field] = converted_value

    return {"data": structured_data, "errors": errors}


def flatten_definitions(definitions, prefix="", result=None):
    """Flattens SERVICE_DEFINITIONS, removes 'DEFINITION' from keys, converts to lowercase,
    and includes nested references as separate entries.

    Args:
        definitions: The dictionary of definitions (e.g., SERVICE_DEFINITIONS).
        prefix: The current prefix for nested keys (used in recursion).
        result: The dictionary to store flattened definitions.

    Returns:
        A dictionary with flattened, lowercase keys and their corresponding definitions.
    """
    if result is None:
        result = {}

    for key, value in definitions.items():
        cleaned_key = key.replace("_DEFINITION", "").lower()
        new_key = f"{prefix}{cleaned_key}" if prefix else cleaned_key

        if isinstance(value, dict):
            is_task_definition = any(isinstance(v, dict) and any(k in v for k in ["REQUIRED", "DATA_TYPE", "VALIDATION"]) for k, v in value.items())

            if is_task_definition:
                result[new_key] = value
                for field, props in value.items():
                    if isinstance(props, dict) and "REFERENCE" in props and props["REFERENCE"]:
                        ref_key = field.lower()
                        if isinstance(props["REFERENCE"], dict) and ref_key not in result:
                            result[ref_key] = props["REFERENCE"]
                        props["REFERENCE"] = ref_key
            else:
                flatten_definitions(value, f"{new_key}.", result)

    return result


class ValidationSystem:
    """Centralized validation system for resolving definitions and validating data."""

    DEFINITIONS = flatten_definitions(SERVICE_DEFINITIONS)

    @classmethod
    def validate(cls, data: Dict[str, Any], event: str, task: str, user_id: str):
        """Validates data against a schema definition identified by definition_key.

        Args:
            data: The data to validate.
            definition_key: The key identifying the schema (e.g., 'chat.run_chat_recipe').

        Returns:
            A dictionary with 'data' (structured data) and 'errors' (validation errors).
        """
        try:
            definition_key = f"{event}.{task}"
            definition = cls.DEFINITIONS.get(definition_key)
            if not definition:
                raise KeyError(definition_key)

            # Create a copy of the definition to avoid modifying the original
            modified_definition = definition.copy()

            # Dynamically add STANDARD_FIELD_DEFINITIONS if fields are not already present
            for field, field_def in STANDARD_FIELD_DEFINITIONS.items():
                if field not in modified_definition:
                    modified_definition[field] = field_def

            validation_result = {
                "event": event,
                "task": task,
                "context": {},
                "errors": {},
            }
            validation_results = validate_and_structure_data(data, modified_definition, user_id)
            validation_result["context"] = validation_results["data"]
            validation_result["errors"] = validation_results["errors"]
            return validation_result

        except KeyError:
            return {"event": event, "task": task, "context": {}, "errors": {definition_key: "Invalid definition key"}}


def get_full_schema():
    """Returns the flattened schema of all SERVICE_DEFINITIONS.

    Returns:
        A dictionary with flattened, lowercase keys and their definitions.
    """
    return flatten_definitions(SERVICE_DEFINITIONS)


def get_task_schema(event_name: str, task_name: str):
    """Retrieves the schema definition for a given event and task name.

    Args:
        event_name: The name of the event (e.g., 'chat_service').
        task_name: The name of the task (e.g., 'run_chat_recipe').

    Returns:
        The schema definition for the task, or None if not found.
    """
    flat_defs = get_full_schema()
    service_name = event_name.replace("_service", "").lower()
    possible_keys = [
        f"{service_name}.{task_name}".lower(),
        task_name.lower(),
    ]

    for key in possible_keys:
        if key in flat_defs:
            return flat_defs[key]

    return None
