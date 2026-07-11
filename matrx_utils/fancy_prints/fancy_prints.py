import inspect
import json
import logging
import random
import re
import sys

from .colors import COLORS
from .matrx_json_converter import to_matrx_json
from .truncation import shorten_for_print, shorten_string_for_print

print_debug = False

_default_logger = logging.getLogger("vcprint")


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
    log_level=None,
    stdout: bool | None = None,
    truncate_blobs=True,
    truncate_secrets=True,
    truncate_text=None,
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
        stdout: When False, emit only through logging (no direct sys.stdout write).
            Default None — WARNING and above log-only (run.py's StreamHandler already
            renders them to the terminal; duplicating to stdout prints every error twice).

    Returns:
        None
    """
    if isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)
    if log_level is None:
        if color == "red":
            log_level = logging.ERROR
        elif color == "yellow":
            log_level = logging.WARNING
        else:
            log_level = logging.INFO

    emit_stdout = stdout if stdout is not None else log_level < logging.WARNING

    BASIC_TYPES = (str, int, float, bool, type(None), bytes, complex)

    if not simple and not pretty:
        if not isinstance(data, BASIC_TYPES):
            pretty = True

    # Resolve the caller's module name for the logger so the log line shows
    # the actual source file rather than the generic "vcprint" label.
    # NOTE: use sys._getframe(1), NOT inspect.stack(). inspect.stack() walks the
    # ENTIRE call stack and opens every frame's source file from disk to attach
    # context lines (findsource -> getmodule -> os.path.realpath). On a hot path
    # that synchronous disk I/O froze the asyncio event loop for ~1s (loop
    # watchdog stall). We only need the immediate caller's module name, which
    # _getframe gives us with zero filesystem access.
    try:
        caller_globals = sys._getframe(1).f_globals
        caller_module = caller_globals.get("__name__", "vcprint")
    except (ValueError, AttributeError):
        caller_module = "vcprint"
    caller_logger = logging.getLogger(caller_module)

    def _log_formatted(serialized: str) -> None:
        """Emit the fully-serialized data to the logger, matching vcprint's visual layout."""
        if title != "Unnamed Data":
            if inline:
                msg = clean_data_for_logging(f"{title}: {serialized}")
            else:
                # Title on one line, data indented on the next — mirrors pretty_print output.
                msg = clean_data_for_logging(f"{title}:\n{serialized}")
        else:
            msg = clean_data_for_logging(serialized)
        try:
            caller_logger.log(level=log_level, msg=msg)
        except Exception:
            _default_logger.error("[SYSTEM LOGGER] Internal Error...")

    try:
        if verbose:
            if pretty:
                try:
                    parsed_data = to_matrx_json(data)
                    display_data = shorten_for_print(
                        parsed_data,
                        truncate_blobs=truncate_blobs,
                        truncate_secrets=truncate_secrets,
                        truncate_text=truncate_text,
                    )
                    _log_formatted(json.dumps(display_data, indent=indent))
                    if emit_stdout:
                        pretty_print(
                            display_data,
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
                    fallback_str = shorten_string_for_print(
                        str(data),
                        truncate_blobs=truncate_blobs,
                        truncate_secrets=truncate_secrets,
                        truncate_text=truncate_text,
                    )
                    _log_formatted(fallback_str)
                    if emit_stdout:
                        pretty_print(
                            fallback_str,
                            title,
                            color,
                            background,
                            style,
                            indent,
                            inline=inline,
                            chunks=chunks,
                        )
            else:
                data = shorten_string_for_print(
                    str(data),
                    truncate_blobs=truncate_blobs,
                    truncate_secrets=truncate_secrets,
                    truncate_text=truncate_text,
                )
                _log_formatted(data)
                if emit_stdout:
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


def pretty_print(
    data,
    title="Unnamed Data",
    color="white",
    background="black",
    style=None,
    indent=4,
    inline=False,
    chunks=False,
):
    frame = inspect.currentframe()
    try:
        # Only reflect over the caller's locals to recover a variable name when
        # no explicit title was given. Use the caller frame directly instead of
        # inspect.getouterframes(), which opens every frame's source file from
        # disk (synchronous I/O that can freeze the asyncio event loop).
        if title != "Unnamed Data":
            name = title
        else:
            caller_frame = frame.f_back if frame is not None else None
            name = title
            if caller_frame is not None:
                name = next(
                    (
                        var_name
                        for var_name, var_val in caller_frame.f_locals.items()
                        if var_val is data
                    ),
                    title,
                )

        if isinstance(data, str) and not data.strip().startswith(("{", "[")):
            if chunks:
                colored_text = colorize(f"{name}: {data}", color, background, style)
                sys.stdout.write(colored_text)
                sys.stdout.flush()
            elif color:
                if inline:
                    cool_print(
                        text=f"{name}: {data}",
                        color=color,
                        background=background,
                        style=style,
                    )
                else:
                    cool_print(
                        text=f"\n{name}:\n{data}",
                        color=color,
                        background=background,
                        style=style,
                    )
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
            r"\[\n\s+((?:\d+,?\s*)+)\n\s+\]",
            lambda m: "[" + m.group(1).replace("\n", "").replace(" ", "") + "]",
            compact_json_string,
        )

        if chunks:
            colored_text = colorize(f"{name}: {compact_json_string}", color, background, style)
            sys.stdout.write(colored_text)
            sys.stdout.flush()
        elif color:
            if inline:
                cool_print(
                    text=f"{name}: {compact_json_string}",
                    color=color,
                    background=background,
                    style=style,
                )
            else:
                cool_print(
                    text=f"\n{name}:\n{compact_json_string}",
                    color=color,
                    background=background,
                    style=style,
                )
        else:
            if inline:
                print(f"{name}: {compact_json_string}")
            else:
                print(f"\n{name}:\n{compact_json_string}")

    finally:
        del frame


def _is_vscode_terminal() -> bool:
    """Detect if running inside a VS Code integrated terminal."""
    import os

    return os.environ.get("TERM_PROGRAM") == "vscode" or "VSCODE_PID" in os.environ


def _format_file_link(path: str) -> str:
    """
    Convert a file system path into the best clickable representation for the
    current environment.

    - **VS Code terminal (any OS):** Plain absolute paths are auto-detected as
      clickable links by the terminal. Wrapping them in ``file://`` or ANSI
      color codes *breaks* that detection, so we return the raw path.
    - **Windows (non-VS Code):** Return a ``file:///C:/...`` URI — the standard
      format that Windows terminals (PowerShell, Windows Terminal, CMD) recognise.
    - **Linux / macOS (non-VS Code):** Return a ``file:///path/...`` URI with
      exactly three slashes before the absolute path (which itself starts with
      ``/``, giving ``file:///path``). Most modern terminals (iTerm2, GNOME
      Terminal, Kitty, Alacritty, Warp) recognise this as a clickable link.
    """
    import os
    import sys

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    if _is_vscode_terminal():
        return path

    if sys.platform == "win32":
        url_path = path.replace("\\", "/")
        return f"file:///{url_path}"

    return f"file://{path}"


def print_link(path):
    from urllib.parse import urlparse

    if not isinstance(path, str):
        path = str(path)

    parsed_path = urlparse(path)
    if parsed_path.scheme in ("http", "https", "ftp"):
        print(path)
        return

    if any(suffix in path.lower() for suffix in {".com", ".org", ".net", ".io", ".us", ".gov"}):
        print(path)
        return

    link = _format_file_link(path)

    if _is_vscode_terminal():
        print(link)
    else:
        print(colorize(link, "blue", style="underline"))


def plt(
    path, title
):  # Note For Armani: I have seen you use this in lot of places. Please tell me what to call this or it needs to be removed.
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


def vclist(
    data=None,
    title="Unnamed Data",
    color=None,
    verbose=True,
    background=None,
    style=None,
    pretty=False,
    indent=4,
    inline=False,
):
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
