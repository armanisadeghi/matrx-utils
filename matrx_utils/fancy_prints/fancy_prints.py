from enum import Enum
import inspect
import sys
import re
from dataclasses import is_dataclass, asdict
import json
from decimal import Decimal
from uuid import UUID
import datetime
import types
import random
import os
import logging

from matrx_utils.fancy_prints.utils.matrx_json_converter import to_matrx_json
from .colors import COLORS

print_debug = False

logger = logging.getLogger("matrx_utils.vcprint")


def clean_data_for_logging(data):
    """
    Clean the data to make it safe for logging.
    Removes emojis and other special characters that could cause logging errors.
    """
    if isinstance(data, str):
        data = re.sub(r"[^\x00-\x7F]+", "", data)
    return data


def colorize(text, color=None, background=None, style=None):
    # ANSI escape codes for colors

    colors = COLORS

    backgrounds = {
        "black": "\033[40m",
        "light_red": "\033[41m",
        "light_green": "\033[42m",
        "light_yellow": "\033[43m",
        "light_blue": "\033[44m",
        "light_magenta": "\033[45m",
        "light_cyan": "\033[46m",
        "gray": "\033[47m",
        "dark_gray": "\033[100m",
        "red": "\033[101m",
        "green": "\033[102m",
        "yellow": "\033[103m",
        "blue": "\033[104m",
        "magenta": "\033[105m",
        "cyan": "\033[106m",
        "white": "\033[107m",
    }

    styles = {
        "bold": "\033[1m",
        "dim": "\033[2m",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "blink": "\033[5m",
        "reverse": "\033[7m",
        "hidden": "\033[8m",
        "strikethrough": "\033[9m",
    }

    reset = "\033[0m"

    if background is None and color in ["black", "dark_gray"]:
        background = "white"
        style = "reverse"

    color_code = colors.get(color, "")
    background_code = backgrounds.get(background, "")
    style_code = styles.get(style, "")

    return f"{color_code}{background_code}{style_code}{text}{reset}"


def vcprint(
        data=None,
        title="Unnamed Data",
        verbose=True,
        color=None,
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
        simple=False,  # New parameter
        log_level=logging.INFO
) -> None:
    """
    Optionally prints data with styling based on verbosity and formatting preferences, and logs the output.

    Args:
        verbose (bool): Controls verbosity of the print output. Default is True.
        data: The data to be printed. Can be of any type that can be converted to a string. Default is None.
        title (str): A title for the data being printed. Default is "Unnamed Data".
        color (str): Text color. Default is None.
        background (str): Background color. Default is None.
        style (str): Text style (e.g., "bold"). Default is None.
        pretty (bool): Enables pretty printing of the data if True. Default is False.
        indent (int): Sets the indent level for pretty printing. Default is 4.
        inline (bool): Whether to print the title and data on the same line. Default is False.
        chunks (bool): Whether to print chunks on the same line without newlines, with color. Default is False.
        simple (bool): Prevents auto-enabling pretty printing for complex types when True. Default is False.

    Returns:
        None
    """
    from matrx_utils.database.orm.core.extended import BaseDTO
    from dataclasses import is_dataclass, asdict
    from uuid import UUID
    from enum import Enum

    BASIC_TYPES = (
        str, int, float, bool, type(None), bytes, complex,  # Core primitives
    )

    if not simple and not pretty:  # Only override if pretty is at default (False) and simple isn't True
        if not isinstance(data, BASIC_TYPES):
            pretty = True

    if data is None:
        data = "No data provided."
    elif isinstance(data, type):
        data = str(data)
    elif isinstance(data, BaseDTO):
        data = data.to_dict()
    elif is_dataclass(data):
        data = asdict(data)
    elif hasattr(data, "to_dict") and callable(data.to_dict):
        data = data.to_dict()
    elif isinstance(data, Enum):
        data = data.value
    elif isinstance(data, UUID):
        data = str(data)

    if inline:
        log_message = f"{title}: {data}"
    else:
        if title == "Unnamed Data":
            log_message = f"{data}"
        else:
            log_message = f"\n{title}:\n{data}"

    log_message = clean_data_for_logging(log_message)

    try:
        logger.log(level=log_level, msg=log_message)
    except Exception as e:
        logger.error("[SYSTEM LOGGER] Internal Error...")

    try:
        if verbose:
            if pretty:
                try:
                    parsed_data = to_matrx_json(data)
                    pretty_print(
                        parsed_data,
                        title,
                        color,
                        background,
                        style,
                        indent,
                        inline=inline,
                        chunks=chunks,
                    )
                except (json.JSONDecodeError, TypeError) as e:
                    if print_debug:
                        print(f"----> Failed to parse data: {str(e)}")
                    pretty_print(
                        data,
                        title,
                        color,
                        background,
                        style,
                        indent,
                        inline=inline,
                        chunks=chunks,
                    )
            else:
                if title == "Unnamed Data":
                    if chunks:
                        colored_text = colorize(f"{data}", color, background, style)
                        sys.stdout.write(colored_text)
                        sys.stdout.flush()
                    else:
                        cool_print(
                            text=f"{data}",
                            color=color,
                            background=background,
                            style=style,
                        )
                else:
                    if chunks:
                        colored_text = colorize(f"{title}: {data}", color, background, style)
                        sys.stdout.write(colored_text)
                        sys.stdout.flush()
                    elif inline:
                        cool_print(
                            text=f"{title}: {data}",
                            color=color,
                            background=background,
                            style=style,
                        )
                    else:
                        cool_print(
                            text=f"\n{title}:\n{data}",
                            color=color,
                            background=background,
                            style=style,
                        )
    except Exception as e:
        print(f"Failed to print data: {str(e)}")  # Error CAUGHT HERE1
        print("Raw data:\n\n")
        print(data)
        print(f"Type of data: {type(data)}")
        print("==============================")


def pretty_print(data,
                 title="Unnamed Data",
                 color="white",
                 background="black",
                 style=None,
                 indent=4, inline=False,
                 chunks=False):
    frame = inspect.currentframe()
    try:
        context = inspect.getouterframes(frame)
        if title == "Unnamed Data":
            name = title
            for var_name, var_val in context[1].frame.f_locals.items():
                if var_val is data:
                    name = var_name
                    break
        else:
            name = title

        if isinstance(data, str) and not data.strip().startswith(("{", "[")):
            if chunks:
                colored_text = colorize(f"{name}: {data}", color, background, style)
                sys.stdout.write(colored_text)
                sys.stdout.flush()
            elif color:
                if inline:
                    cool_print(text=f"{name}: {data}", color=color, background=background, style=style)
                else:
                    cool_print(text=f"\n{name}:\n{data}", color=color, background=background, style=style)
            else:
                if inline:
                    print(f"{name}: {data}")
                else:
                    print(f"\n{name}:\n{data}")
            return

        converted_data, old_type, new_type = convert_to_json_compatible(data)
        type_message = f" [{old_type} converted to {new_type}]" if old_type != new_type else ""
        json_string = json.dumps(converted_data, indent=indent)

        compact_json_string = re.sub(r'"\\"([^"]*)\\""', r'"\1"', json_string)
        compact_json_string = re.sub(
            r"\[\n\s+((?:\d+,?\s*)+)\n\s+\]", lambda m: "[" + m.group(1).replace("\n", "").replace(" ", "") + "]",
            compact_json_string
        )

        if chunks:
            colored_text = colorize(f"{name}:{type_message} {compact_json_string}", color, background, style)
            sys.stdout.write(colored_text)
            sys.stdout.flush()
        elif color:
            if inline:
                cool_print(text=f"{name}:{type_message} {compact_json_string}", color=color, background=background,
                           style=style)
            else:
                cool_print(text=f"\n{name}:{type_message}\n{compact_json_string}", color=color, background=background,
                           style=style)
        else:
            if inline:
                print(f"{name}:{type_message} {compact_json_string}")
            else:
                print(f"\n{name}:{type_message}\n{compact_json_string}")

    finally:
        del frame


def handle_string_conversion(data):
    """Handle string parsing and type conversion"""

    try:
        # Try direct JSON parse
        try:
            parsed = json.loads(data)
            converted_data, _, nested_type = convert_to_json_compatible(parsed)
            return converted_data, nested_type
        except json.JSONDecodeError:
            # Try unescaped JSON
            unescaped = data.encode().decode("unicode_escape")
            try:
                parsed = json.loads(unescaped)
                converted_data, _, nested_type = convert_to_json_compatible(parsed)
                return converted_data, nested_type
            except json.JSONDecodeError:
                return handle_string_type_conversion(data)
    except Exception:
        return data, "str"


def handle_string_type_conversion(data):
    """Convert string to appropriate primitive type if possible"""
    if data.lower() == "true":
        return True, "bool"
    elif data.lower() == "false":
        return False, "bool"
    elif data.lower() in ("none", "null"):
        return None, "NoneType"

    try:
        if "." in data:
            return float(data), "float"
        return int(data), "int"
    except ValueError:
        return data, "str"


def handle_model_class(cls):
    print("excecuting handle_model_class")
    if hasattr(cls, "_fields"):
        fields_info = {}
        for field_name, field in cls._fields.items():
            field_info = {"type": type(field).__name__}
            if hasattr(field, "default"):
                field_info["default"] = field.default
            fields_info[field_name] = field_info
        return {"class_name": cls.__name__, "module": cls.__module__, "fields": fields_info}, "dict"
    return f"<class '{cls.__module__}.{cls.__name__}'>", "str"


def handle_model_data(instance):
    return convert_to_json_compatible(instance.to_dict())[0], "dict"


def handle_orm_field(field):
    """Handle conversion of ORM field objects by using their to_dict method"""
    return convert_to_json_compatible(field.to_dict())[0], "dict"


def handle_dataclass_instance(instance):
    """Handle conversion of dataclass instances"""

    return asdict(instance), "dict"


def handle_simplenamespace_instance(instance):
    """Handle conversion of SimpleNamespace instances"""

    # Convert attributes, handling enums specifically
    result = {}
    for key, value in instance.__dict__.items():
        if isinstance(value, Enum):
            result[key] = value.value  # Use the enum's value (e.g., 'user')
        else:
            result[key] = convert_to_json_compatible(value)[0]  # Recursively convert other values
    return result, "dict"


def handle_dto_instance(instance):
    print(f"Handling DTO: {type(instance).__name__}")
    return instance.to_dict(), "dict"


def convert_to_json_compatible(data):
    from matrx_utils.database.orm.core.fields import Field
    from matrx_utils.database.orm.core.extended import BaseDTO

    TYPE_HANDLERS = {
        "simplenamespace": (lambda x: isinstance(x, types.SimpleNamespace), handle_simplenamespace_instance),
        "dto": (
            lambda x: isinstance(x, BaseDTO) and type(x) is not BaseDTO,
            handle_dto_instance,
        ),
        "model_data": (lambda x: hasattr(x, "to_dict") and callable(x.to_dict), handle_model_data),
        "orm_field": (lambda x: isinstance(x, Field), handle_orm_field),
        "dataclass": (is_dataclass, handle_dataclass_instance),
    }

    old_type = type(data).__name__

    if isinstance(data, type):
        converted_data, new_type = handle_model_class(data)
        return converted_data, old_type, new_type

    # Handle registered type handlers
    for handler_name, (check_func, handler_func) in TYPE_HANDLERS.items():
        if check_func(data):
            converted_data, new_type = handler_func(data)
            return converted_data, old_type, new_type

    # Handle basic types
    if isinstance(data, str):
        converted_data, new_type = handle_string_conversion(data)
        return converted_data, old_type, new_type

    elif isinstance(data, Enum):
        return data.value, old_type, "enum"

    elif isinstance(data, UUID):
        return str(data), old_type, "str"

    elif isinstance(data, (int, float, bool, type(None))):
        return data, old_type, old_type
    elif isinstance(data, UUID):
        return str(data), old_type, "str"
    elif isinstance(data, (list, tuple)):
        converted_list = [convert_to_json_compatible(item)[0] for item in data]
        new_type = "list" if isinstance(data, list) else "tuple"
        return converted_list, old_type, new_type
    elif isinstance(data, dict):
        converted_dict = {key: convert_to_json_compatible(value)[0] for key, value in data.items()}
        return converted_dict, old_type, "dict"
    elif isinstance(data, datetime.datetime):
        return data.isoformat(), old_type, "str"
    elif isinstance(data, Decimal):
        return float(data), old_type, "float"

    # Handle objects with to_dict method
    if hasattr(data, "to_dict"):
        try:
            # Try to call to_dict() regardless of whether it's a bound method or not
            dict_data = data.to_dict()
            return convert_to_json_compatible(dict_data)[0], old_type, "dict"
        except (AttributeError, TypeError):
            pass

    # Handle objects with dict method
    if hasattr(data, "dict"):
        try:
            dict_data = data.dict()
            return convert_to_json_compatible(dict_data)[0], old_type, "dict"
        except (AttributeError, TypeError):
            pass

    # Default fallback
    try:
        return str(data), old_type, "str"
    except Exception:
        return "This data type is:", old_type, "which is not compatible with pretty print."


def print_link(path):
    from urllib.parse import urlparse
    import os

    if not isinstance(path, str):
        path = str(path)

    if any(suffix in path.lower() for suffix in {".com", ".org", ".net", ".io", ".us", ".gov"}):
        print(path)
        return

    if not isinstance(path, str):
        raise ValueError("The provided path must be a string.")

    parsed_path = urlparse(path)

    if parsed_path.scheme and parsed_path.netloc:
        print(path)

    else:
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        url_compatible_path = path.replace("\\", "/")
        print(colorize("file:///{}".format(url_compatible_path), "blue"))


def plt(path, title):
    print(colorize(f"\n{title}: ", "yellow"), end="")
    print_link(path)


def print_truncated(value, max_chars=250):
    """
    Safely print the value with a maximum character limit if applicable.
    If the value is a string, truncate it.
    Otherwise, print the value directly.
    """
    if isinstance(value, str):
        if len(value) > max_chars:
            truncated_value = value[:max_chars]
            print(f"----Truncated Value----\n{truncated_value}...\n----------")
    else:
        print(value)


def cool_print(text, color, background=None, style=None):
    print(colorize(text, color, background, style))


class InlinePrinter:
    def __init__(self, prefix="", separator=" | "):
        self.prefix = prefix
        self.separator = separator
        self.first_item = True

    def print(self, item, color="blue", end=False):
        if self.first_item:
            print(colorize(self.prefix, "magenta"), end="", flush=True)
            self.first_item = False
        else:
            print(self.separator, end="", flush=True)

        print(colorize(item, color), end="", flush=True)

        if end:
            print()

        sys.stdout.flush()


def create_inline_printer(prefix="[AI Matrix] ", separator=" | "):
    return InlinePrinter(prefix, separator)


def get_random_color():
    all_colors = list(COLORS.keys())
    return random.choice(all_colors)


def is_empty(value):
    """
    Recursively check if a value is considered empty.
    - None, empty strings, empty dictionaries, and empty lists are considered empty.
    - For dictionaries, all values must be empty for it to be considered empty.
    """
    if value is None or value == "" or (isinstance(value, (list, dict)) and not value):
        return True
    if isinstance(value, dict):
        return all(is_empty(v) for v in value.values())
    if isinstance(value, list):
        return all(is_empty(v) for v in value)
    return False


def vclist(data=None, title="Unnamed Data", verbose=True, color=None, background=None, style=None, pretty=False,
           indent=4, inline=False):
    """
    Wrapper for vcprint that handles lists of data.
    Calls vcprint for each item in the list, only including the title for the first item.
    Skips empty lists, empty items, empty dictionaries, and empty nested lists.
    """
    if not data:  # Check if data is None or an empty list
        return

    if isinstance(data, list):
        for index, item in enumerate(data):
            if is_empty(item):
                continue

            # Prepare arguments for vcprint
            vcprint_args = {
                "data": item,
                "verbose": verbose,
                "color": color,
                "background": background,
                "style": style,
                "pretty": pretty,
                "indent": indent,
                "inline": inline,
            }

            if index == 0 and title:  # Only include the title for the first item
                vcprint_args["title"] = title

            vcprint(**vcprint_args)
    else:
        # If data is not a list, just call vcprint normally
        vcprint(
            data=data,
            title=title,
            verbose=verbose,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
        )


def vcdlist(data=None, verbose=True, color=None, background=None, style=None, pretty=False, indent=4, inline=False):
    """
    Specialized wrapper for vcprint that handles a list of dictionaries.
    For each dictionary in the list, it calls vcprint with the dictionary's key as the title
    and its value as the data.
    Skips empty dictionaries and values.
    """
    if not data:  # Check if data is None or an empty list
        return

    if isinstance(data, list):
        for item in data:
            if is_empty(item):
                continue

            if isinstance(item, dict):
                for key, value in item.items():
                    if not is_empty(value):  # Ensure value is not empty
                        vcprint(
                            data=value,
                            title=key,
                            verbose=verbose,
                            color=color,
                            background=background,
                            style=style,
                            pretty=pretty,
                            indent=indent,
                            inline=inline,
                        )
    else:
        # If data is not a list, just call vcprint normally
        vcprint(data=data, verbose=verbose, color=color, background=background, style=style, pretty=pretty,
                indent=indent, inline=inline)


def print_file_link(path):
    if isinstance(path, str):
        if not os.path.isabs(path):
            path = os.path.abspath(path)
        # if not os.path.exists(path):
        # raise FileNotFoundError(f"The path {path} does not exist.")
        url_compatible_path = path.replace("\\", "/")
    else:
        if not os.path.exists(str(path)):
            raise FileNotFoundError(f"The path {path} does not exist.")
        url_compatible_path = str(path).replace("\\", "/")

    print("file:///{}".format(url_compatible_path))
