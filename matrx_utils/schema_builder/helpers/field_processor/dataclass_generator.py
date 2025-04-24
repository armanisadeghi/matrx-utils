from typing import Any, Dict
from aidream.settings import BASE_DIR
from common.utils.fancy_prints import print_link, vcprint
import os

# Define sample data for all possible types at the top of the code generation file
SAMPLE_DATA_TYPE_TO_VALUE_MAP = {
    str: "This is a string",
    int: 123,
    bool: True,
    list: ["a", "b"],
    dict: {"a": "b"},
}


def to_snake_case(name: str) -> str:
    """Convert a CamelCase or PascalCase string to snake_case, preserving acronyms."""
    if not name:
        return name

    result = [name[0].lower()]
    prev_char = name[0]

    # Track if we're in an acronym (consecutive uppercase letters)
    in_acronym = prev_char.isupper()

    for char in name[1:]:
        if char.isupper():
            if prev_char.isupper():
                # We're in an acronym (e.g., "AI" in "AISettings")
                result.append(char.lower())
            else:
                # Transition from lowercase to uppercase (e.g., "broker" to "Object")
                result.append("_")
                result.append(char.lower())
            in_acronym = True
        else:
            if prev_char.isupper() and in_acronym and len(result) > 1:
                # End of an acronym (e.g., "AI" to "Settings")
                # Insert underscore before the last letter of the acronym
                # Only if the acronym is longer than one letter and not already preceded by an underscore
                if result[-2] != "_":
                    result.insert(-1, "_")

            result.append(char)
            in_acronym = False

        prev_char = char

    return "".join(result)



def get_type_str(field_spec: Dict[str, Any]) -> str:
    base_type = field_spec["type"]
    type_map = {str: "str", int: "int", bool: "bool", list: "List", dict: "Dict"}

    type_str = type_map.get(base_type, str(base_type))

    if base_type is list:
        list_type = field_spec.get("list_type", str)
        list_type_str = type_map.get(list_type, str(list_type))
        return f"{type_str}[{list_type_str}]"

    return type_str


def needs_field_factory(default_value: Any) -> bool:
    return isinstance(default_value, (list, dict))


def generate_dataclass_code(class_name: str, fields_spec: Dict[str, Dict[str, Any]]) -> str:
    required_fields = []
    optional_fields = []
    field_names = []

    for field_name, spec in fields_spec.items():
        default = spec["default"]
        always_include = spec["always_include"]

        has_default = default is not None or not always_include

        type_str = get_type_str(spec)
        field_names.append(field_name)
        if has_default:
            if default is None:
                field_line = f"    {field_name}: Optional[{type_str}] = None"
            elif needs_field_factory(default):
                factory = "list" if isinstance(default, list) else "dict"
                field_line = f"    {field_name}: {type_str} = field(default_factory={factory})"
            else:
                default_str = repr(default)
                field_line = f"    {field_name}: {type_str} = {default_str}"
            optional_fields.append(field_line)
        else:
            field_line = f"    {field_name}: {type_str}"
            required_fields.append(field_line)

    to_dict_lines = [
        "    def to_dict(self):",
        "        return {",
    ]
    for field_name in field_names:
        to_dict_lines.append(f"            {repr(field_name)}: self.{field_name},")
    to_dict_lines.append("        }")

    imports = [
        "import os",
        "from dataclasses import dataclass, field",
        "from typing import Dict, List, Optional, Any",
        "import typing",
        "from common.utils.dynamic_field_handler import process_field_definitions, process_object_field_definitions, process_batch_field_definitions",
        "from common.utils.fancy_prints import vcprint",
    ]

    class_lines = ["@dataclass", f"class {class_name}:"]
    if not required_fields and not optional_fields:
        class_lines.append("    pass")
    else:
        class_lines.extend(required_fields)
        class_lines.extend(optional_fields)
    class_lines.extend(to_dict_lines)

    return "\n".join(imports + [""] + class_lines)


def generate_build_function_code(class_name: str) -> str:
    snake_case_name = to_snake_case(class_name)
    function_lines = [
        f"def build_{snake_case_name}_from_kwargs(get_dict=False, **kwargs) -> {class_name}:",
        "    processed_data = process_field_definitions(FIELD_DEFINITIONS, **kwargs, convert_camel_case=True, fieldname_map=FIELD_MAP)",
        f"    obj = {class_name}(**processed_data)",
        "    if get_dict:",
        "        return obj.to_dict()",
        "    return obj",
    ]
    return "\n".join(function_lines)


def generate_build_function_code_from_object(class_name: str) -> str:
    snake_case_name = to_snake_case(class_name)
    function_lines = [
        f"def build_{snake_case_name}_from_object(obj: Any, get_dict=False) -> {class_name}:",
        "    processed_data = process_object_field_definitions(FIELD_DEFINITIONS, obj, convert_camel_case=True, fieldname_map=FIELD_MAP)",
        f"    obj = {class_name}(**processed_data)",
        "    if get_dict:",
        "        return obj.to_dict()",
        "    return obj",
    ]
    return "\n".join(function_lines)


def generate_build_function_code_from_batch_objects(class_name: str) -> str:
    snake_case_name = to_snake_case(class_name)
    function_lines = [
        f"def build_{snake_case_name}_from_batch_objects(objects: List[Any], get_dict=False) -> List[{class_name}]:",
        "    processed_data = process_batch_field_definitions(FIELD_DEFINITIONS, objects, convert_camel_case=True, fieldname_map=FIELD_MAP)",
        f"    objs = [{class_name}(**data) for data in processed_data]",
        "    if get_dict:",
        "        return [obj.to_dict() for obj in objs]",
        "    return objs",
    ]
    return "\n".join(function_lines)


def format_field_definitions(fields_spec: Dict[str, Dict[str, Any]]) -> str:
    type_map = {str: "str", int: "int", bool: "bool", list: "list", dict: "dict"}

    lines = ["FIELD_DEFINITIONS = {"]
    for field_name, spec in fields_spec.items():
        formatted_spec = spec.copy()
        formatted_spec["type"] = type_map.get(spec["type"], str(spec["type"]))
        if "list_type" in spec:
            formatted_spec["list_type"] = type_map.get(spec["list_type"], str(spec["list_type"]))
        lines.append(f"    {repr(field_name)}: {repr(formatted_spec)},")
    lines.append("}")

    return "\n".join(lines)


def format_field_map(field_map: Dict[str, str]) -> str:
    lines = ["FIELD_MAP = {"]
    for external_name, internal_name in field_map.items():
        lines.append(f"    {repr(external_name)}: {repr(internal_name)},")
    lines.append("}")
    return "\n".join(lines)


def generate_test_block(class_name: str, fields_spec: Dict[str, Dict[str, Any]]) -> str:
    snake_case_name = to_snake_case(class_name)
    sample_data_lines = ["    sample_data = {"]
    for field_name, spec in fields_spec.items():
        field_type = spec["type"]
        if field_type is list and "list_type" in spec:
            value = SAMPLE_DATA_TYPE_TO_VALUE_MAP[list]
            if spec["list_type"] is int:
                value = [1, 2]
            elif spec["list_type"] is bool:
                value = [True, False]
        elif field_type in SAMPLE_DATA_TYPE_TO_VALUE_MAP:
            value = SAMPLE_DATA_TYPE_TO_VALUE_MAP[field_type]
        else:
            value = repr(spec["default"])
        sample_data_lines.append(f"        {repr(field_name)}: {repr(value)},")
    sample_data_lines.append("    }")

    minimal_sample_data_lines = ["    minimal_sample_data = {"]
    for field_name, spec in fields_spec.items():
        always_include = spec["always_include"]
        default = spec["default"]
        if always_include and default is None:
            field_type = spec["type"]
            if field_type is list and "list_type" in spec:
                value = SAMPLE_DATA_TYPE_TO_VALUE_MAP[list]
                if spec["list_type"] is int:
                    value = [1, 2]
                elif spec["list_type"] is bool:
                    value = [True, False]
            elif field_type in SAMPLE_DATA_TYPE_TO_VALUE_MAP:
                value = SAMPLE_DATA_TYPE_TO_VALUE_MAP[field_type]
            else:
                value = repr(spec["default"])
            minimal_sample_data_lines.append(f"        {repr(field_name)}: {repr(value)},")
    minimal_sample_data_lines.append("    }")

    test_lines = [
        "",
        'if __name__ == "__main__":',
        "    os.system('cls')",
        *sample_data_lines,
        '    vcprint(sample_data, "Full sample data", pretty=True, color="green")',
        f"    metadata_full = build_{snake_case_name}_from_kwargs(**sample_data)",
        '    vcprint(metadata_full, "Resulting Metadata (full)", pretty=True, color="green")',
        "",
        *minimal_sample_data_lines,
        "",
        '    vcprint(minimal_sample_data, "Minimal sample data (required fields only)", pretty=True, color="yellow")',
        f"    metadata_minimal = build_{snake_case_name}_from_kwargs(**minimal_sample_data)",
        '    vcprint(metadata_minimal, "Resulting Metadata (minimal)", pretty=True, color="yellow")',
        "",
        f"    metadata_from_object = build_{snake_case_name}_from_object(metadata_full)",
        '    vcprint(metadata_from_object, "Resulting Metadata (from object)", pretty=True, color="blue")',
        "",
        f"    metadata_from_batch_objects = build_{snake_case_name}_from_batch_objects([metadata_full, metadata_minimal])",
        '    vcprint(metadata_from_batch_objects, "Resulting Metadata (from batch objects)", pretty=True, color="purple")',
    ]
    return "\n".join(test_lines)


def generate_complete_code(
    class_name: str,
    fields_spec: Dict[str, Dict[str, Any]],
    additional_imports: str,
    path_from_base: str = None,
    field_map: Dict[str, str] = None,
) -> str:
    """Generate complete code with all imports at the top."""
    field_map = field_map or {}
    dataclass_code = generate_dataclass_code(class_name, fields_spec)
    build_function_code = generate_build_function_code(class_name)
    build_function_code_from_object = generate_build_function_code_from_object(class_name)
    build_function_code_from_batch_objects = generate_build_function_code_from_batch_objects(class_name)
    field_definitions_line = format_field_definitions(fields_spec)
    field_map_line = format_field_map(field_map)
    test_block = generate_test_block(class_name, fields_spec)

    dataclass_lines = dataclass_code.split("\n")
    imports = [line for line in dataclass_lines if line.startswith("from ")]
    class_definition = "\n".join([line for line in dataclass_lines if not line.startswith("from ")])

    all_imports = "\n".join(imports + [additional_imports.strip()]) if additional_imports.strip() else "\n".join(imports)

    generated_code = "\n\n".join(
        [
            all_imports,
            class_definition,
            field_definitions_line,
            field_map_line,
            build_function_code,
            build_function_code_from_object,
            build_function_code_from_batch_objects,
            test_block,
        ]
    )

    if path_from_base:
        file_path = f"{BASE_DIR}/{path_from_base}"
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        with open(file_path, "w") as f:
            f.write(generated_code)
        print_link(file_path)
        return generated_code, file_path

    return generated_code, None
