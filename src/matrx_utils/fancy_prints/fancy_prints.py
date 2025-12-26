import inspect
import sys
import re
import json
import random
import logging

from matrx_utils.fancy_prints.utils.matrx_json_converter import to_matrx_json
from .colors import COLORS

print_debug = False

logger = logging.getLogger("vcprint")


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
        color=None,
        verbose=True,
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
        simple=False,
        log_level=logging.INFO
) -> None:
    """
    Optionally prints data with styling based on verbosity and formatting preferences, and logs the output.

    Args:
        data: The data to be printed. Can be of any type that can be converted to a string. Default is None.
        title (str): A title for the data being printed. Default is "Unnamed Data".
        color (str): Text color. Default is None.
        verbose (bool): Controls verbosity of the print output. Default is True.
        background (str): Background color. Default is None.
        style (str): Text style (e.g., "bold"). Default is None.
        pretty (bool): Enables pretty printing of the data if True. Default is False.
        indent (int): Sets the indent level for pretty printing. Default is 4.
        inline (bool): Whether to print the title and data on the same line. Default is False.
        chunks (bool): Whether to print chunks on the same line without newlines, with color. Default is False.
        simple (bool): Prevents auto-enabling pretty printing for complex types when True. Default is False.
        log_level: The logging level to use. Default is logging.INFO.

    Returns:
        None
    """
    BASIC_TYPES = (str, int, float, bool, type(None), bytes, complex)

    if not simple and not pretty:
        if not isinstance(data, BASIC_TYPES):
            pretty = True

    # Prepare log message
    log_message = clean_data_for_logging(
        f"{title}: {data}" if inline else f"\n{title}:\n{data}" if title != "Unnamed Data" else f"{data}")
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
                except Exception as e:
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
        print(f"Failed to print data: {str(e)}")
        print("Raw data:\n\n")
        print(data)
        print(f"Type of data: {type(data)}")
        print("==============================")


def pretty_print(data,
                 title="Unnamed Data",
                 color="white",
                 background="black",
                 style=None,
                 indent=4,
                 inline=False,
                 chunks=False):
    frame = inspect.currentframe()
    try:
        context = inspect.getouterframes(frame)
        name = title if title != "Unnamed Data" else next(
            (var_name for var_name, var_val in context[1].frame.f_locals.items() if var_val is data), title)

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

        converted_data = to_matrx_json(data)
        json_string = json.dumps(converted_data, indent=indent)
        compact_json_string = re.sub(r'"\\"([^"]*)\\""', r'"\1"', json_string)
        compact_json_string = re.sub(
            r"\[\n\s+((?:\d+,?\s*)+)\n\s+\]", lambda m: "[" + m.group(1).replace("\n", "").replace(" ", "") + "]",
            compact_json_string
        )

        if chunks:
            colored_text = colorize(f"{name}: {compact_json_string}", color, background, style)
            sys.stdout.write(colored_text)
            sys.stdout.flush()
        elif color:
            if inline:
                cool_print(text=f"{name}: {compact_json_string}", color=color, background=background, style=style)
            else:
                cool_print(text=f"\n{name}:\n{compact_json_string}", color=color, background=background, style=style)
        else:
            if inline:
                print(f"{name}: {compact_json_string}")
            else:
                print(f"\n{name}:\n{compact_json_string}")

    finally:
        del frame


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


def plt(path,
        title):  # Note For Armani: I have seen you use this in lot of places. Please tell me what to call this or it needs to be removed.
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


def vclist(data=None, title="Unnamed Data", color=None, verbose=True, background=None, style=None, pretty=False,
           indent=4, inline=False):
    """
    Wrapper for vcprint that handles lists of data.
    Calls vcprint for each item in the list, only including the title for the first item.
    Skips empty lists, empty items, empty dictionaries, and empty nested lists.
    """
    if not data:
        return

    if isinstance(data, list):
        for index, item in enumerate(data):
            if is_empty(item):
                continue

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

            if index == 0 and title:
                vcprint_args["title"] = title

            vcprint(**vcprint_args)
