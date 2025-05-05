# matrx_utils\socket\schema\schema_processor.py
from enum import Enum
from typing import Any

from matrx_utils.socket.schema.validations.validation_registry import (
    CUSTOM_VALIDATIONS,
    VALIDATION_REGISTRY,
)
from matrx_utils.socket.schema.validations.validations_system import validate_enum
from matrx_utils.socket.schema.conversions.conversions_system import convert_value
from matrx_utils import vcprint
from matrx_utils.socket.utils.fake_get_schema import get_schema
from typing import Set, Dict, Optional
import copy



STANDARD_FIELD_DEFINITIONS = {
    "user_id": {
        "REQUIRED": False,
        "DEFAULT": "socket_internal_user_id",
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "CircleUser",
        "DESCRIPTION": "The ID of the user to be used in the recipe.",
    },
    "response_listener_event": {
        "REQUIRED": False,
        "DEFAULT": None,
        "VALIDATION": None,
        "DATA_TYPE": "string",
        "CONVERSION": None,
        "REFERENCE": None,
        "COMPONENT": "input",
        "COMPONENT_PROPS": {},
        "ICON_NAME": "Zap",
        "DESCRIPTION": "The name of the event to be used in the recipe.",
    },
}


class SocketSchemaError(ValueError):
    """Custom exception for schema-related errors."""
    pass

class ValidationSystem:
    """Validates data against a loaded JSON schema at runtime, validating the schema itself first."""

    def __init__(self, schema: Dict[str, Any]):
        """Loads and validates the schema structure."""
        if not isinstance(schema, dict):
             raise SocketSchemaError("Invalid schema format. Input must be a dictionary.")

        self.schema = schema
        self.definitions = self.schema.get("definitions")
        self.tasks = self.schema.get("tasks")

        if not isinstance(self.definitions, dict):
            raise SocketSchemaError("Schema missing or invalid 'definitions' (must be an object).")
        if not isinstance(self.tasks, dict):
            raise SocketSchemaError("Schema missing or invalid 'tasks' (must be an object).")

        self._validate_schema()
        vcprint("Schema structure validated successfully.")

    def _validate_schema(self):
        """Performs structural validation of the loaded schema."""
        # --- 1. Validate Definitions Structure and References ---
        for def_key, definition in self.definitions.items():
            is_field = not all(type(k)==dict for k,v in definition.items())
            path = f"definitions/{def_key}"
            if not isinstance(definition, dict):
                 raise SocketSchemaError(f"Invalid definition at '{path}'. Expected an object.")

            # Check if it's a named group (contains fields which are dicts) or a single field definition
            is_named_group = all(isinstance(v, dict) for v in definition.values())

            if is_named_group:
                self._validate_definition_group(definition, path, set()) # Start cycle check here
            else:
                 self._validate_single_field_def(definition, path) # Validate single field def structure

        # --- 2. Validate Tasks Structure and References ---
        for service_name, service_tasks in self.tasks.items():
            service_path = f"tasks/{service_name}"
            if not isinstance(service_tasks, dict):
                raise SocketSchemaError(f"Invalid service definition at '{service_path}'. Expected an object.")

            for task_name, task_definition in service_tasks.items():
                task_path = f"{service_path}/{task_name}"
                if not isinstance(task_definition, dict):
                     raise SocketSchemaError(f"Invalid task definition at '{task_path}'. Expected an object.")

                if "$ref" in task_definition:
                    if len(task_definition) > 1:
                         raise SocketSchemaError(f"Task definition at '{task_path}' with $ref cannot have other properties.")
                    ref_path = task_definition["$ref"]
                    # Task ref must point to a named group (object definition)
                    resolved_def = self._resolve_and_validate_ref(ref_path, task_path, allow_single_field=False, visited=set())
                    # Basic cycle check for task refs pointing to themselves
                    if ref_path.replace("definitions/","") == task_name.upper(): # Simplified check
                         pass # Allow referencing a global def with same name, deeper cycle check handles real issues
                else:
                    # Validate fields within the task definition
                    self._validate_definition_group(task_definition, task_path, set()) # Start cycle check here

    def _validate_definition_group(self, definition_obj: Dict, current_path: str, visited: Set[str]):
        """Validates fields within a named group (from definitions) or task definition. Handles cycles."""
        # --- Cycle Detection ---
        # Use a canonical path for visited check (e.g., always start with definitions/ or tasks/)
        canonical_path = current_path
        if not (canonical_path.startswith("definitions/") or canonical_path.startswith("tasks/")):
             # This case shouldn't happen with correct initial calls, but safety check
             raise SocketSchemaError(f"Internal Error: Invalid path format for cycle check: {current_path}")

        if canonical_path in visited:
            raise SocketSchemaError(f"Circular reference detected involving '{canonical_path}'. Path: {' -> '.join(list(visited)) + ' -> ' + canonical_path}")
        visited.add(canonical_path)

        # --- End Cycle Detection ---
        for field_name, rules in definition_obj.items():
            field_path = f"{current_path}/{field_name}"
            if not isinstance(rules, dict):
                raise SocketSchemaError(f"Invalid field rule structure at '{field_path}'. Expected an object.")

            # --- Determine field type and validate accordingly ---
            if "$ref" in rules:
                # Field uses $ref
                if len(rules) > 1: pass # Allow overrides
                ref_path = rules["$ref"]
                # Field ref can point to single field or named group
                resolved_ref = self._resolve_and_validate_ref(ref_path, field_path, allow_single_field=True, visited=visited)
                # If resolved ref is a named group, recurse for cycle check
                if isinstance(resolved_ref, dict) and all(isinstance(v, dict) for v in resolved_ref.values()):
                    self._validate_definition_group(resolved_ref, ref_path, visited.copy())

            elif "REFERENCE" in rules and rules["REFERENCE"] is not None:
                # Field uses REFERENCE
                ref_name = rules["REFERENCE"]
                if not isinstance(ref_name, str):
                     raise SocketSchemaError(f"Invalid REFERENCE value at '{field_path}'. Expected a string name.")
                ref_path = f"definitions/{ref_name}"
                # REFERENCE must point to a named group
                resolved_ref = self._resolve_and_validate_ref(ref_path, field_path, allow_single_field=False, visited=visited)
                # Recurse for cycle check into the referenced named group
                self._validate_definition_group(resolved_ref, ref_path, visited.copy())
                # We don't call _validate_single_field_def here because the structure of this field
                # itself (COMPONENT, DATA_TYPE=object/array) is implicitly validated by its usage.

            else:
                # Inline field definition (no $ref, no REFERENCE)
                self._validate_single_field_def(rules, field_path)

        visited.remove(canonical_path) # Backtrack for cycle detection

    def _validate_single_field_def(self, rules: Dict, path: str):
        # Check for required properties
        required_props = ["COMPONENT", "DATA_TYPE"]
        for prop in required_props:
            if prop not in rules:
                raise SocketSchemaError(f"Missing required property '{prop}' in inline field definition at '{path}'.")

        # Allow REFERENCE only if DATA_TYPE is 'array' or 'object'
        if "REFERENCE" in rules and rules["REFERENCE"] is not None:
            data_type = rules.get("DATA_TYPE")
            if data_type not in ["array", "object"]:
                raise SocketSchemaError(
                    f"REFERENCE property is only allowed for fields with DATA_TYPE 'array' or 'object' at '{path}'.")

        # Ensure $ref is not used in inline field definitions
        if "$ref" in rules:
            raise SocketSchemaError(
                f"$ref property is invalid in an inline field definition at '{path}'. It should be the only key if used.")

    def _resolve_and_validate_ref(self, ref_path: str, current_path: str, allow_single_field: bool, visited: Set[str]) -> Dict:
        """Resolves a $ref or REFERENCE path, performs basic validation, and checks for immediate cycles."""
        resolved_def = None
        is_definition_ref = False

        if isinstance(ref_path, str) and ref_path.startswith("definitions/"):
            resolved_def = self.get_definition(ref_path)
            is_definition_ref = True
        # Add elif for tasks/ if needed

        if resolved_def is None:
            raise SocketSchemaError(f"Reference '{ref_path}' at '{current_path}' could not be resolved.")

        if not isinstance(resolved_def, dict):
             raise SocketSchemaError(f"Reference '{ref_path}' at '{current_path}' resolved to an invalid type ({type(resolved_def).__name__}). Expected object.")

        # Determine if the resolved definition represents a named group or a single field
        # A named group has dictionary values for its keys (the fields)
        is_named_group = any(isinstance(v, dict) for v in resolved_def.values())

        if not allow_single_field and not is_named_group:
             raise SocketSchemaError(f"Reference '{ref_path}' at '{current_path}' must point to an object definition (named group), but points to a single field definition.")

        # --- Cycle Check during resolution ---
        # Check if the target we are resolving to is already in our current path
        target_path = ref_path # Use the reference path itself for cycle check
        if target_path in visited:
             raise SocketSchemaError(f"Circular reference detected involving '{target_path}'. Path: {' -> '.join(list(visited)) + ' -> ' + target_path}")
        # --- End Cycle Check ---

        return resolved_def

    def get_definition(self, ref_path: str) -> Optional[Dict[str, Any]]:
        if not isinstance(ref_path, str) or not ref_path.startswith("definitions/"): return None
        key = ref_path.split('/', 1)[1]
        return self.definitions.get(key)

    def get_task_definition(self, event: str, task: str) -> Optional[Dict[str, Any]]:
        service_name = event.upper(); task_name = task.upper()
        return self.tasks.get(service_name, {}).get(task_name)

    def validate(self, data: Dict[str, Any], event: str, task: str, user_id: str):
        # Initialize the result dictionary
        validation_result = {"event": event, "task": task, "context": {}, "errors": {}}

        # Always set user_id in the context (available from method parameter)
        validation_result["context"]["user_id"] = user_id

        # Extract response_listener_event from data, fallback to default if not present
        response_listener_event = data.get("response_listener_event", None)  # Default is None per schema
        validation_result["context"]["response_listener_event"] = response_listener_event

        # Proceed with validation
        try:
            initial_task_def = self.get_task_definition(event, task)
            if not initial_task_def:
                raise SocketSchemaError(f"Task definition '{event}.{task}' not found.")

            definition_to_validate = initial_task_def
            if "$ref" in initial_task_def:
                ref_path = initial_task_def["$ref"]
                definition_to_validate = self.get_definition(ref_path)
                # Structure already validated in __init__

            working_definition = copy.deepcopy(definition_to_validate)
            for field, field_def in STANDARD_FIELD_DEFINITIONS.items():
                if field not in working_definition:
                    working_definition[field] = field_def

            validation_results = self._validate_recursive_data(data, working_definition, user_id)
            validation_result["context"].update(validation_results["data"])
            validation_result["errors"] = validation_results["errors"]
        except SocketSchemaError as e:
            validation_result["errors"]["_schema"] = str(e)
        except Exception as e:
            vcprint(f"Unexpected Validation Error for {event}.{task}: {e}", color="error")
            import traceback
            traceback.print_exc()
            validation_result["errors"]["_internal"] = f"Internal validation error: {type(e).__name__}"

        return validation_result

    def _validate_recursive_data(self, data: Dict[str, Any], definition: Dict[str, Any], user_id: str, depth: int = 0):
        structured_data, errors = {}, {}
        for field, rules in definition.items():
            field_errors = []
            original_rules = rules
            if "$ref" in rules:
                ref_path = rules["$ref"]
                resolved_rules = self.get_definition(ref_path)
                rules = copy.deepcopy(resolved_rules)
                overrides = {k: v for k, v in original_rules.items() if k != "$ref"}
                rules.update(overrides)

            value = data.get(field)
            if value is None:
                value = rules.get("DEFAULT")

            if rules.get("DEFAULT") == "socket_internal_user_id":
                value = user_id

            expected_type = rules.get("DATA_TYPE")
            validation_rule = rules.get("VALIDATION")
            conversion = rules.get("CONVERSION")
            reference = rules.get("REFERENCE")

            try:
                converted_value = convert_value(value, expected_type, conversion)
            except Exception as e:
                field_errors.append(f"Conversion failed: {str(e)}")
                errors[field] = "; ".join(field_errors)
                continue

            if rules.get("REQUIRED") and converted_value is None and value is None:
                field_errors.append("Missing required field")

            if reference and converted_value is not None:
                ref_def_path = f"definitions/{reference}"
                ref_definition = self.get_definition(ref_def_path)
                if isinstance(converted_value, dict):
                    nested_result = self._validate_recursive_data(converted_value, ref_definition, user_id, depth + 1)
                    if nested_result["errors"]:
                        errors[field] = nested_result["errors"]
                    converted_value = nested_result["data"]
                elif isinstance(converted_value, list) and expected_type == "array":
                    processed_list, list_errors = [], {}
                    for idx, item in enumerate(converted_value):
                        if isinstance(item, dict):
                            nested_result = self._validate_recursive_data(item, ref_definition, user_id, depth + 1)
                            if nested_result["errors"]:
                                list_errors[f"[{idx}]"] = nested_result["errors"]
                            processed_list.append(nested_result["data"])
                        else:
                            list_errors[f"[{idx}]"] = f"Expected object for reference '{reference}', got {type(item).__name__}"
                    if list_errors:
                        errors[field] = list_errors
                    converted_value = processed_list
                else:
                    field_errors.append(f"Data type mismatch for reference '{reference}'. Expected object or array, got {type(converted_value).__name__}")

            if not field_errors and validation_rule and converted_value is not None:
                validator, msg = None, None
                if validation_rule in CUSTOM_VALIDATIONS: validator = CUSTOM_VALIDATIONS[validation_rule]
                elif validation_rule in VALIDATION_REGISTRY: validator = VALIDATION_REGISTRY[validation_rule]
                if validator:
                    try:
                        if isinstance(validator, type) and issubclass(validator, Enum):
                            validate_enum(converted_value, validator)
                        elif callable(validator):
                            validator(converted_value)
                        else:
                            msg = f"Invalid validator for rule '{validation_rule}'"
                    except Exception as e:
                        msg = f"Validation failed: {str(e)}"
                if msg:
                    field_errors.append(msg)

            if field_errors:
                if field not in errors:
                    errors[field] = "; ".join(field_errors)
            else:
                structured_data[field] = converted_value
        return {"data": structured_data, "errors": errors}


VALIDATOR = None
def get_validator():
    global VALIDATOR
    if VALIDATOR is not None:
        return VALIDATOR
    VALIDATOR = ValidationSystem(get_schema())
    return VALIDATOR
