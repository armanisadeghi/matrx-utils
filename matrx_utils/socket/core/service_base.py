# matrx_utils\socket\core\service_base.py
from abc import ABC, abstractmethod

from matrx_utils import vcprint
from matrx_utils.socket.response.socket_printer import SocketPrinter
from matrx_utils import FileManager
from matrx_utils import MatrixPrintLog

local_debug = False


class SocketServiceBase(ABC, FileManager, MatrixPrintLog):
    def __init__(self, app_name: str, service_name: str, log_level: str, batch_print: bool, stream_handler=None,
                 user_id=None, **kwargs):
        if not app_name:
            raise ValueError("app_name must be provided and cannot be empty")
        if not service_name:
            raise ValueError("service_name must be provided and cannot be empty")
        if not log_level:
            raise ValueError("log_level must be provided and cannot be empty")
        self.app_name = app_name
        self.service_name = service_name
        self.log_level = log_level
        self.batch_print = batch_print
        self.stream_handler = stream_handler or SocketPrinter(event_name="socket_service_base_default")
        self.user_id = user_id
        # Dynamically set any additional kwargs as attributes
        for key, value in kwargs.items():
            setattr(self, key, value)
        FileManager.__init__(self, app_name=app_name, batch_print=batch_print)

        MatrixPrintLog.__init__(
            self,
            system_level=log_level,
            class_name=service_name,
            outro=f"= [${service_name} Process Completed] =",
        )

    def __setattr__(self, name, value):
        # Allow dynamic attribute setting without restrictions
        self.__dict__[name] = value

    @abstractmethod
    async def process_task(self, task, task_context=None, process=True):
        pass

    def add_stream_handler(self, stream_handler):
        self.stream_handler = stream_handler

    def set_user_id(self, user_id):
        self.user_id = user_id

    def set_log_level(self, log_level):
        self.log_level = log_level

    def update_attributes(self, context):
        """
        Update instance attributes with context values, allowing new attributes to be set dynamically.
        """
        if not context:
            return

        for key, value in context.items():
            setattr(self, key, value)  # Simplified to always set attributes

    async def execute_task(self, task, task_context=None, process=True):
        """
        Execute the given task if it is available in the TASK_MAP for the service class.
        """
        if local_debug:
            vcprint(task, "[SERVICE BASE] execute_task", color="gold")

        if process and task_context:
            self.update_attributes(task_context)
            if local_debug:
                vcprint(task, "[SERVICE BASE] execute_task updated attributes", color="gold")

        self.task = task

        class_name = self.__class__.__name__
        method = getattr(self, task, None)
        if method:
            return await method()
        else:
            raise ValueError(f"Method {task} not implemented in {class_name}")
