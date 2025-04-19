import json
import re
import inspect
import sys
from core import settings
from core.system_logger import get_logger
from uuid import UUID
from enum import Enum
from dataclasses import is_dataclass, asdict
from ..utils.matrx_json_converter import to_matrx_json


class MatrixPrintLog:
    def __init__(self, system_level, class_name, outro=None):
        self.level_options = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "PRINT"]
        self.logger = get_logger()
        self.log_vcprint = settings.LOG_VCPRINT
        self.system_level = system_level.upper() if system_level in self.level_options else "INFO"
        self.class_name = class_name
        self.module_intro = f"[MATRIX {self.class_name}]"
        self.outro = outro if outro else "[MATRIX OUTRO]"
        self.caller_info = self.module_intro
        self.override_level = "CRITICAL"
        self.data = "No data provided."
        self.title = "Unnamed Data"
        self.color = None
        self.background = None
        self.style = None
        self.pretty = False
        self.indent = 4
        self.inline = False
        self.chunks = False  # Added to match vcprint
        self.full_text = ""
        self.message_for_log = ""
        self.path = None
        self.method_intro = "[MATRIX METHOD]"
        self.class_intro = "[MATRIX CLASS]"
        self.function_intro = "[MATRIX FUNCTION]"
        self.process_intro = "[MATRIX PROCESS]"

    @staticmethod
    def camel_case_to_title(name):
        return re.sub(r"(?<!^)(?=[A-Z])", " ", name).title()

    @staticmethod
    def snake_case_to_title(name):
        return name.replace("_", " ").title()

    def get_caller_info(self, number=2):
        frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(frame)[number]
        method_name = caller_frame.function
        class_name = caller_frame.frame.f_globals["__name__"]
        proper_class_name = self.camel_case_to_title(class_name.split(".")[-1])
        proper_method_name = self.snake_case_to_title(method_name.split(".")[-1])
        caller_info = f"[MATRIX {proper_class_name} {proper_method_name}]"
        return caller_info, proper_class_name, proper_method_name

    def method_into(self, number=1, start_text=""):
        frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(frame)[number]
        method_name = re.sub(r"(?<!^)(?=[A-Z])", " ", caller_frame.function).title()
        if start_text and not start_text.endswith(" "):
            start_text = f"{start_text} "
        return f"[{start_text}MATRIX {self.class_name.upper()} {method_name} Method]"

    def method_name(self, number=1, pretty=False):
        frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(frame)[number]
        method_name = re.sub(r"(?<!^)(?=[A-Z])", " ", caller_frame.function).title()
        if pretty:
            return self.snake_case_to_title(method_name.split(".")[-1])
        return method_name

    def simple_method_into(self, number=1, start_text=""):
        frame = inspect.currentframe()
        caller_frame = inspect.getouterframes(frame)[number]
        method_name = re.sub(r"(?<!^)(?=[A-Z])", " ", caller_frame.function).title()
        if start_text:
            start_text = f"{start_text} "
        return f"{start_text}{method_name}"

    def get_effective_level(self, message_level=None):
        effective_level = self.system_level
        if message_level is not None:
            effective_level = message_level
        if self.level_options.index(effective_level) > self.level_options.index(self.override_level):
            effective_level = self.override_level
        return effective_level

    def should_log(self, message_level=None):
        effective_level = self.get_effective_level(message_level)
        if not self.log_vcprint:
            return False
        return self.level_options.index(effective_level) <= self.level_options.index("ERROR")

    def should_print(self, message_level=None):
        effective_level = self.get_effective_level(message_level)
        return self.level_options.index(effective_level) <= self.level_options.index(self.system_level)

    def _clean_for_log(self):
        if isinstance(self.full_text, str):
            self.message_for_log = re.sub(r"[^\x00-\x7F]+", "", self.full_text)

    def log_message(self):
        try:
            self.logger.info(self.message_for_log)
        except Exception as e:
            self.logger.error(f"[SYSTEM LOGGER] Internal Error... {e}")

    def _convert_data(self, data):
        from matrx_utils.database.orm.core.extended import BaseDTO

        if data is None:
            return "No data provided."
        elif isinstance(data, type):
            return str(data)
        elif isinstance(data, BaseDTO):
            return data.to_dict()
        elif is_dataclass(data):
            return asdict(data)
        elif hasattr(data, "to_dict") and callable(data.to_dict):
            return data.to_dict()
        elif isinstance(data, Enum):
            return data.value
        elif isinstance(data, UUID):
            return str(data)
        else:
            return data

    def vcprint(
        self,
        data=None,
        title="no title",
        level=None,
        color=None,
        background=None,
        style=None,
        pretty=True,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or title == "no title":
            title = self.method_into(2)
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def pretty_print(
        self,
        data=None,
        title=None,
        level=None,
        color=None,
        background=None,
        style=None,
        pretty=True,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or not title:
            title = self.method_into(2)
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def inline_print(
        self,
        data=None,
        title=None,
        level=None,
        color=None,
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=True,
        chunks=False,
    ):
        if title == "me" or not title:
            title = self.method_into(2)
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def print(
        self,
        data=None,
        title=None,
        level="PRINT",
        color=None,
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or not title:
            title = self.method_into(2)
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def debug_print(
        self,
        data=None,
        title=None,
        level="DEBUG",
        color="gray",
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or not title:
            title = self.method_into(2)
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def info_print(
        self,
        data=None,
        title="Info",
        level="INFO",
        color="light_blue",
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or title == "Info":
            title = self.method_into(2, start_text="INFO")
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def warning_print(
        self,
        data=None,
        title="Warning!",
        level="WARNING",
        color="yellow",
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or title == "Warning!":
            title = self.method_into(2, start_text="WARNING!")
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def error_print(
        self,
        data=None,
        title="Error!",
        level="ERROR",
        color="red",
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or title == "Error!":
            title = self.method_into(2, start_text="ERROR!")
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def critical_print(
        self,
        data=None,
        title="critical!",
        level="CRITICAL",
        color="red",
        background=None,
        style=None,
        pretty=False,
        indent=4,
        inline=False,
        chunks=False,
    ):
        if title == "me" or title == "critical!":
            title = self.method_into(2, start_text="CRITICAL!")
        self._print_and_or_log(
            data=data,
            title=title,
            level=level,
            color=color,
            background=background,
            style=style,
            pretty=pretty,
            indent=indent,
            inline=inline,
            chunks=chunks,
        )

    def _print_and_or_log(
        self,
        data=None,
        title=None,
        level=None,
        color=None,
        background=None,
        style=None,
        pretty=None,
        indent=None,
        inline=None,
        chunks=None,
    ):
        level = level.upper() if level and level in self.level_options else None
        effective_level = self.get_effective_level(level)
        should_log = self.should_log(effective_level)
        should_print = self.should_print(effective_level)

        if not should_log and not should_print:
            print("Early Exit -- Not Logging or printing.")
            return

        if data is not None:
            self.data = self._convert_data(data)

        if title is not None:
            self.title = title if title != "me" else self.get_caller_info()[2]

        if self.title == "Unnamed Data":
            self.full_text = f"{self.data}"
        else:
            self.full_text = f"{self.title}: {self.data}" if self.inline else f"\n{self.title}:\n{self.data}"

        if inline is not None:
            self.inline = inline
        if chunks is not None:
            self.chunks = chunks
        if color is not None:
            self.color = color
        if background is not None:
            self.background = background
        if style is not None:
            self.style = style
        if pretty is not None:
            self.pretty = pretty
        if indent is not None:
            self.indent = indent

        if should_print:
            self._print()

        if should_log:
            self._clean_for_log()
            self.log_message()

    def _print(self):
        if self.pretty:
            self._pretty_print()
        else:
            if self.chunks:
                colored_text = self._colorize(self.full_text)
                sys.stdout.write(colored_text)
                sys.stdout.flush()
            else:
                self._color_print()

    def _pretty_print(self):
        frame = inspect.currentframe()
        try:
            context = inspect.getouterframes(frame)
            if self.title == "Unnamed Data":
                name = self.title
                for var_name, var_val in context[1].frame.f_locals.items():
                    if var_val is self.data:
                        name = var_name
                        break
            else:
                name = self.title

            if isinstance(self.data, str) and not self.data.strip().startswith(("{", "[")):
                if self.chunks:
                    colored_text = self._colorize(f"{name}: {self.data}")
                    sys.stdout.write(colored_text)
                    sys.stdout.flush()
                elif self.color:
                    self.full_text = f"{name}: {self.data}" if self.inline else f"\n{name}:\n{self.data}"
                    self._color_print()
                else:
                    print(f"{name}: {self.data}" if self.inline else f"\n{name}:\n{self.data}")
                return

            converted_data = to_matrx_json(self.data)
            json_string = json.dumps(converted_data, indent=self.indent)
            compact_json_string = re.sub(r'"\\"([^"]*)\\""', r'"\1"', json_string)
            compact_json_string = re.sub(
                r"\[\n\s+((?:\d+,?\s*)+)\n\s+\]",
                lambda m: "[" + m.group(1).replace("\n", "").replace(" ", "") + "]",
                compact_json_string,
            )

            if self.chunks:
                colored_text = self._colorize(f"{name}: {compact_json_string}")
                sys.stdout.write(colored_text)
                sys.stdout.flush()
            elif self.color:
                self.full_text = f"{name}: {compact_json_string}" if self.inline else f"\n{name}:\n{compact_json_string}"
                self._color_print()
            else:
                print(f"{name}: {compact_json_string}" if self.inline else f"\n{name}:\n{compact_json_string}")
        finally:
            del frame

    def _colorize(self, text):
        COLORS = {
            "black": "\033[30m",
            "light_red": "\033[31m",
            "light_green": "\033[32m",
            "light_yellow": "\033[33m",
            "light_blue": "\033[34m",
            "light_magenta": "\033[35m",
            "light_cyan": "\033[36m",
            "gray": "\033[37m",
            "dark_gray": "\033[90m",
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "bright_orange": "\033[38;5;208m",
            "bright_pink": "\033[38;5;205m",
            "pink": "\033[38;5;200m",
            "bright_purple": "\033[38;5;129m",
            "bright_lime": "\033[38;5;118m",
            "bright_teal": "\033[38;5;51m",
            "bright_lavender": "\033[38;5;183m",
            "bright_turquoise": "\033[38;5;45m",
            "bright_gold": "\033[38;5;220m",
            "bright_silver": "\033[38;5;250m",
            "bright_red": "\033[38;5;196m",
            "bright_green": "\033[38;5;46m",
            "bright_blue": "\033[38;5;27m",
            "bright_yellow": "\033[38;5;226m",
        }
        BACKGROUNDS = {
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
        STYLES = {
            "bold": "\033[1m",
            "dim": "\033[2m",
            "italic": "\033[3m",
            "underline": "\033[4m",
            "blink": "\033[5m",
            "reverse": "\033[7m",
            "hidden": "\033[8m",
            "strikethrough": "\033[9m",
        }
        RESET = "\033[0m"

        if self.background is None and self.color in ["black", "dark_gray"]:
            self.background = "white"
            self.style = "reverse"

        color_code = COLORS.get(self.color, "")
        background_code = BACKGROUNDS.get(self.background, "")
        style_code = STYLES.get(self.style, "")
        return f"{color_code}{background_code}{style_code}{text}{RESET}"

    def _color_print(self):
        colored_text = self._colorize(self.full_text)
        print(colored_text)

    def print_link(self, path):
        from urllib.parse import urlparse
        import os

        self.path = path
        if not isinstance(self.path, str):
            self.path = str(self.path)
        if os.path.isfile(self.path):
            abs_path = os.path.abspath(self.path)
            url_compatible_path = abs_path.replace("\\", "/")
            print(f"file:///{url_compatible_path}")
            return

        parsed_path = urlparse(self.path)
        if parsed_path.scheme and parsed_path.netloc:
            print(self.path)
        else:
            if not os.path.isabs(self.path):
                self.path = os.path.abspath(self.path)
            url_compatible_path = self.path.replace("\\", "/")
            print(f"file:///{url_compatible_path}")

    def print_truncated(self, value, max_chars=250):
        if isinstance(value, str):
            if len(value) > max_chars:
                truncated_value = value[:max_chars]
                print(f"----Truncated Value----\n{truncated_value}...\n----------")
        else:
            print(value)

