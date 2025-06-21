
from .file_handler import FileHandler
from .specific_handlers.html_handler import HtmlHandler
from .specific_handlers.json_handler import JsonHandler
from .specific_handlers.markdown_handler import MarkdownHandler
from .specific_handlers.text_handler import TextHandler
from .specific_handlers.image_handler import ImageHandler
from .batch_handler import BatchHandler

from datetime import datetime
import uuid


class FileManager:
    _instances = {}
    _log_intro = "[MATRX FILE MANAGER]"

    def __init__(self, app_name, new_instance=False, batch_print=False, print_errors=True, batch_handler=None):
        self.app_name = app_name
        self.batch_print = batch_print
        self.print_errors = print_errors
        self.batch_handler = batch_handler or BatchHandler.get_instance(enable_batch=batch_print)

        self.file_handler = FileHandler.get_instance(app_name, new_instance, batch_print, print_errors, self.batch_handler)
        self.text_handler = TextHandler(app_name, batch_print=batch_print)
        self.json_handler = JsonHandler(app_name, batch_print=batch_print)
        self.html_handler = HtmlHandler(app_name, batch_print=batch_print)
        self.image_handler = ImageHandler(app_name, batch_print=batch_print)
        self.markdown_handler = MarkdownHandler(app_name, batch_print=batch_print)

    @classmethod
    def get_instance(cls, app_name, new_instance=False, batch_print=False, print_errors=True, batch_handler=None):
        key = (app_name, batch_print, print_errors, id(batch_handler))
        if not new_instance and key in cls._instances:
            return cls._instances[key]

        instance = cls(app_name, new_instance, batch_print, print_errors, batch_handler)
        if not new_instance:
            cls._instances[key] = instance
        return instance

    def read(self, root, path, file_type='text'):
        handler = getattr(self, f"{file_type}_handler")
        return getattr(handler, f"read_{file_type}")(root, path)

    def write(self, root, path, content, file_type='text', clean=True):
        handler = getattr(self, f"{file_type}_handler")
        return getattr(handler, f"write_{file_type}")(root, path, content, clean=clean)

    def file_exists(self, root, path, file_type='text'):
        handler = getattr(self, f"{file_type}_handler")
        return handler.file_exists(root, path)

    def delete_file(self, root, path, file_type='text'):
        handler = getattr(self, f"{file_type}_handler")
        return handler.delete_file(root, path)

    def list_files(self, root, path="", file_type='text'):
        handler = getattr(self, f"{file_type}_handler")
        return handler.list_files(root, path)

    def print_batch(self):
        self.file_handler.print_batch()

    def read_json(self, root, path):
        return self.json_handler.read_json(root, path)

    def write_json(self, root, path, data, clean=True):
        return self.json_handler.write_json(root=root, path=path, data=data, clean=clean)

    def append_json(self, root, path, data, clean=True):
        return self.json_handler.append_json(root=root, path=path, data=data, clean=clean)

    def read_temp_json(self, path):
        return self.json_handler.read_json(root="temp", path=path)

    def write_temp_json(self, path, data, clean=True):
        return self.json_handler.write_json(root="temp", path=path, data=data, clean=clean)

    def get_config_json(self, path):
        return self.json_handler.read_json(root="config", path=path)

    def read_text(self, root, path):
        return self.text_handler.read_text(root, path)

    def write_text(self, root, path, data, clean=True):
        return self.text_handler.write_text(root=root, path=path, content=data, clean=clean)

    def read_temp_text(self, path):
        return self.text_handler.read_text(root="temp", path=path)

    def write_temp_text(self, path, data, clean=True):
        return self.text_handler.write_text(root="temp", path=path, content=data, clean=clean)

    # HTML specific methods
    def read_html(self, root, path):
        return self.html_handler.read_html(root, path)

    def write_html(self, root, path, data, clean=True):
        return self.html_handler.write_html(root=root, path=path, content=data, clean=clean)

    def read_temp_html(self, path):
        return self.html_handler.read_html(root="temp", path=path)

    def write_temp_html(self, path, data, clean=True):
        return self.html_handler.write_html(root="temp", path=path, content=data, clean=clean)

    # Markdown specific methods
    def read_markdown(self, root, path):
        return self.markdown_handler.read_markdown(root, path)

    def write_markdown(self, root, path, data, clean=True):
        return self.markdown_handler.write_markdown(root=root, path=path, content=data, clean=clean)

    def read_temp_markdown(self, path):
        return self.markdown_handler.read_markdown(root="temp", path=path)

    def write_temp_markdown(self, path, data, clean=True):
        return self.markdown_handler.write_markdown(root="temp", path=path, content=data, clean=clean)

    def read_markdown_lines(self, root, path):
        return self.markdown_handler.read_lines(root, path)

    def write_markdown_lines(self, root, path, data, clean=True):
        return self.markdown_handler.write_lines(root, path, lines=data, clean=clean)


    # Image specific
    def read_image(self, root, path):
        return self.image_handler.read_image(root, path)

    def write_image(self, root, path, data):
        return self.image_handler.write_image(root=root, path=path, image=data)

    def read_temp_image(self, path):
        return self.image_handler.read_image(root="temp", path=path)

    def write_temp_image(self, path, data, clean=True):
        return self.image_handler.write_image(root="temp", path=path, image=data)

    def generate_filename(self, extension, sub_dir="", prefix="", suffix="", random=False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_dir = f"{sub_dir}/" if sub_dir else ""
        prefix = f"{prefix}_" if prefix else ""
        suffix = f"_{suffix}" if suffix else ""

        if random:
            return f"{sub_dir}{prefix}{str(uuid.uuid4())}{suffix}.{extension}"

        return f"{sub_dir}{prefix}{timestamp}{suffix}.{extension}"

    def generate_directoryname(self, sub_dir="", prefix="", suffix="", random=False):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_dir = f"{sub_dir}/" if sub_dir else ""
        prefix = f"{prefix}_" if prefix else ""
        suffix = f"_{suffix}" if suffix else ""

        if random:
            return f"{sub_dir}{prefix}{str(uuid.uuid4())}{suffix}"

        return f"{sub_dir}{prefix}{timestamp}{suffix}"

    def add_to_batch(self, full_path=None, message=None, color=None):
        self.file_handler.add_to_batch(full_path, message, color)

    def get_full_path_from_base(self,root, path):
        return self.file_handler.public_get_full_path(root, path)