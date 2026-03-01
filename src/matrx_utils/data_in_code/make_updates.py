import importlib.util
import json
import os
from datetime import datetime

from matrx_utils import vcprint

DEFAULT_DATA_FILE = os.path.join("common", "utils", "data_in_code", "current_data.py")
DEFAULT_TS_DATA_FILE = os.path.join("common", "utils", "data_in_code", "current_ts_data.ts")
HISTORY_FILE = os.path.join("common", "utils", "data_in_code", "data_history.json")


def _to_serializable(obj, visited=None):
    if visited is None:
        visited = set()

    # Check for circular reference
    obj_id = id(obj)
    if obj_id in visited:
        return f"<CircularReference: {type(obj).__name__} at {hex(obj_id)}>"

    # Add current object to visited set
    if hasattr(obj, "__dict__") or isinstance(obj, (list, tuple)):
        visited.add(obj_id)

    if isinstance(obj, dict):
        return {k: _to_serializable(v, visited.copy()) for k, v in obj.items()}
    elif hasattr(obj, "__dict__"):
        return {k: _to_serializable(v, visited.copy()) for k, v in obj.__dict__.items()}
    elif isinstance(obj, (list, tuple)):
        return [_to_serializable(item, visited.copy()) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    return str(obj)


def _format_value(value, indent=4):
    if isinstance(value, list):
        if not value:
            return "[]"
        items = []
        for item in value:
            if isinstance(item, dict):
                dict_str = (
                    "{\n"
                    + "\n".join(
                        f"{' ' * (indent + 4)}\"{k}\": {_format_value(v, indent + 4)}," for k, v in item.items()
                    )
                    + f"\n{' ' * indent}"
                    + "}"
                )
                items.append(dict_str)
            else:
                items.append(repr(item))
        return "[\n" + f"{' ' * indent}" + f",\n{' ' * indent}".join(items) + f"\n{' ' * (indent - 4)}" + "]"
    return repr(value)


def _format_ts_value(value, indent=2):
    """Format value for TypeScript with proper syntax"""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, type(None)):
        return "null"
    elif isinstance(value, str):
        # Use double quotes for TypeScript strings
        return json.dumps(value)
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        if not value:
            return "[]"
        items = []
        for item in value:
            items.append(_format_ts_value(item, indent + 2))
        if len(items) == 1 and not isinstance(value[0], (dict, list)):
            return f"[{items[0]}]"
        return "[\n" + f"{' ' * indent}" + f",\n{' ' * indent}".join(items) + f"\n{' ' * (indent - 2)}" + "]"
    elif isinstance(value, dict):
        if not value:
            return "{}"
        items = []
        for k, v in value.items():
            # Ensure proper key formatting for TypeScript
            key_str = (
                f'"{k}"'
                if not k.isidentifier()
                or k in ["import", "export", "default", "class", "function", "const", "let", "var"]
                else k
            )
            items.append(f"{key_str}: {_format_ts_value(v, indent + 2)}")
        return "{\n" + f"{' ' * indent}" + f",\n{' ' * indent}".join(items) + f"\n{' ' * (indent - 2)}" + "}"
    return json.dumps(value)


def _update_ts_file(variable_name, value, filename, timestamp):
    """Update TypeScript file with new constant"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    content_lines = []
    variable_found = False
    variable_start = -1
    variable_end = -1

    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content_lines = f.readlines()

        # Look for existing const declaration
        for i, line in enumerate(content_lines):
            if line.strip().startswith(f"export const {variable_name}"):
                variable_found = True
                variable_start = i

                # Find the end of the constant declaration
                assignment_part = line.split("=", 1)[1].strip() if "=" in line else ""

                # Check if it's a multi-line declaration
                if (assignment_part.startswith("[") and not assignment_part.rstrip().endswith("];")) or (
                    assignment_part.startswith("{") and not assignment_part.rstrip().endswith("};")
                ):
                    # Multi-line: find the end
                    bracket_count = 0
                    brace_count = 0
                    in_string = False
                    escape_next = False

                    for j in range(i, len(content_lines)):
                        line_content = content_lines[j]

                        # Skip the variable name part on first line
                        if j == i:
                            equals_pos = line_content.find("=")
                            if equals_pos != -1:
                                line_content = line_content[equals_pos + 1 :]

                        # Parse character by character
                        for char in line_content:
                            if escape_next:
                                escape_next = False
                                continue

                            if char == "\\":
                                escape_next = True
                                continue

                            if char in ['"', "'"]:
                                in_string = not in_string
                                continue

                            if not in_string:
                                if char == "[":
                                    bracket_count += 1
                                elif char == "]":
                                    bracket_count -= 1
                                elif char == "{":
                                    brace_count += 1
                                elif char == "}":
                                    brace_count -= 1
                                elif char == ";" and bracket_count <= 0 and brace_count <= 0:
                                    variable_end = j
                                    break

                        if variable_end != -1:
                            break

                    # Fallback if no semicolon found
                    if variable_end == -1:
                        variable_end = i
                else:
                    # Single line
                    variable_end = i
                break

    # Format the TypeScript constant
    ts_value = _format_ts_value(value, 2)
    new_definition = f"export const {variable_name} = {ts_value};\n"

    if variable_found:
        updated_lines = content_lines[:variable_start] + [new_definition] + content_lines[variable_end + 1 :]
    else:
        comment = f"// {variable_name} added on {timestamp}\n"
        if content_lines and not content_lines[-1].endswith("\n"):
            content_lines[-1] += "\n"
        updated_lines = content_lines + ["\n", comment, new_definition]

    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)


def update_data_in_code(variable_name, new_value, filename=DEFAULT_DATA_FILE, verbose=False, ts_filename=DEFAULT_TS_DATA_FILE):
    from common import plt

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    serializable_value = _to_serializable(new_value)
    value_str = _format_value(serializable_value)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    content_lines = []
    variable_found = False
    variable_start = -1
    variable_end = -1

    if os.path.exists(filename):
        with open(filename, "r") as f:
            content_lines = f.readlines()

        for i, line in enumerate(content_lines):
            if line.strip().startswith(f"{variable_name} ="):
                variable_found = True
                variable_start = i

                # More robust multi-line detection
                # Check if the assignment is complete on this line
                assignment_part = line.split("=", 1)[1].strip()

                # Simple heuristic: if it starts with [ or { and doesn't end with ] or }
                # then it's likely multi-line
                if (assignment_part.startswith("[") and not assignment_part.rstrip().endswith("]")) or (
                    assignment_part.startswith("{") and not assignment_part.rstrip().endswith("}")
                ):
                    # Track nesting level to find the real end
                    bracket_count = 0
                    brace_count = 0
                    in_string = False
                    escape_next = False

                    # Start from the assignment line
                    for j in range(i, len(content_lines)):
                        line_content = content_lines[j]

                        # If this is the first line, skip the variable name part
                        if j == i:
                            equals_pos = line_content.find("=")
                            if equals_pos != -1:
                                line_content = line_content[equals_pos + 1 :]

                        # Parse character by character to handle strings properly
                        for char in line_content:
                            if escape_next:
                                escape_next = False
                                continue

                            if char == "\\":
                                escape_next = True
                                continue

                            if char in ['"', "'"]:
                                in_string = not in_string
                                continue

                            if not in_string:
                                if char == "[":
                                    bracket_count += 1
                                elif char == "]":
                                    bracket_count -= 1
                                elif char == "{":
                                    brace_count += 1
                                elif char == "}":
                                    brace_count -= 1

                        # If we've closed all brackets and braces, we found the end
                        if bracket_count <= 0 and brace_count <= 0:
                            variable_end = j
                            break

                    # Fallback: if we couldn't find proper end, assume it's the last line with content
                    if variable_end == -1:
                        variable_end = i
                else:
                    # Single line assignment
                    variable_end = i
                break

    new_definition = f"{variable_name} = {value_str}\n"
    if variable_found:
        updated_lines = content_lines[:variable_start] + [new_definition] + content_lines[variable_end + 1 :]
    else:
        comment = f"# {variable_name} added on {timestamp}\n"
        if content_lines and not content_lines[-1].endswith("\n"):
            content_lines[-1] += "\n"
        updated_lines = content_lines + ["\n", "\n", comment, new_definition]

    with open(filename, "w") as f:
        f.writelines(updated_lines)

    plt(filename, "Updated Data File")

    update_history(filename, variable_name, serializable_value, timestamp, verbose)

    if ts_filename:
        _update_ts_file(variable_name, new_value, ts_filename, timestamp)
        if verbose:
            plt(ts_filename, "Updated TypeScript Data File")


def update_history(filename, variable_name, new_value, timestamp, verbose=False):
    from common import plt
    
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history_key = f"{os.path.normpath(filename)}:{variable_name}"
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {}

    if history_key not in history:
        history[history_key] = []

    history_entry = {
        "timestamp": timestamp,
        "filename": filename,
        "variable_name": variable_name,
        "data": new_value,
    }
    history[history_key].append(history_entry)

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

    if verbose:
        plt(HISTORY_FILE, "Updated History File")


def clean_history(variable_name, filename=DEFAULT_DATA_FILE, verbose=False):
    from common import plt
    
    history_key = f"{os.path.normpath(filename)}:{variable_name}"
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {}

    if history_key in history and history[history_key]:
        latest_entry = history[history_key][-1]
        history[history_key] = [latest_entry]

        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        if verbose:
            plt(HISTORY_FILE, f"Cleaned history for {variable_name} in {filename}")
    else:
        vcprint(f"\nNo history found for {variable_name} in {filename}", color="yellow")


def delete_from_history(variable_name, filename=DEFAULT_DATA_FILE, verbose=False):
    from common import plt
    
    history_key = f"{os.path.normpath(filename)}:{variable_name}"
    history = {}
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = {}

    if history_key in history:
        del history[history_key]

        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=4)

        if verbose:
            plt(HISTORY_FILE, f"Deleted {variable_name} from history in {filename}")
    else:
        vcprint(f"\nNo history found for {variable_name} in {filename}", color="yellow")


def fetch_data(variable_name, filename=DEFAULT_DATA_FILE, verbose=False):
    if not os.path.exists(filename):
        return None

    spec = importlib.util.spec_from_file_location("data_module", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return getattr(module, variable_name, None)


def update_data_in_code_with_ts(
    variable_name, new_value, py_filename=DEFAULT_DATA_FILE, ts_filename=DEFAULT_TS_DATA_FILE, verbose=False
):
    """
    Convenience function to update both Python and TypeScript files at once
    """
    update_data_in_code(variable_name, new_value, py_filename, verbose, ts_filename)


if __name__ == "__main__":
    os.system("cls")
    ai_models = [
        {
            "id": "88b47b41-669d-4884-bce0-f5c7c85900ea",
            "name": "gpt-4o-audio-preview",
            "common_name": "GPT 4o Audio Preview",
            "model_class": "gpt-4o-audio",
            "provider": "OpenAi",
            "endpoints": ["openai"],
            "max_tokens": 2048,
            "model_provider": "99fa34b1-4c36-427f-ab73-cc56f1d5c4a0",
        },
        {
            "id": "226e0f0f-5ac1-4234-a80f-4254b841684a",
            "name": "gpt-4o-2024-08-06",
            "common_name": "GPT-4o",
            "model_class": "gpt-4o",
            "provider": "OpenAI",
            "context_window": 128000,
            "max_tokens": 16384,
            "capabilities": [
                "text-generation",
                "image-to-text",
                "advanced-reasoning",
                "coding",
                "multilingual-tasks",
            ],
            "model_provider": "99fa34b1-4c36-427f-ab73-cc56f1d5c4a0",
        },
    ]

    # Update both Python and TypeScript files
    update_data_in_code_with_ts("all_active_ai_models", ai_models, verbose=True)
    if verbose_data := fetch_data("all_active_ai_models"):
        vcprint(verbose_data, "Current AI Models:", color="green", pretty=True)
