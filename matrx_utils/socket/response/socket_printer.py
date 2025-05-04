# matrx_utils\socket\response\socket_printer.py
from typing import Any, Dict, Optional
from matrx_utils import vcprint
import datetime
import uuid
import enum


class SocketPrinter():
    def __init__(self, event_name: str, sid: str = None, namespace: str = "/UserSession", debug: bool = False):
        self.event_name = event_name
        self.sid = sid
        self.namespace = namespace
        self.debug = debug

    async def send_chunk(self, chunk: str):
        vcprint(data=chunk, chunks=True)

    async def send_chunk_final(self, chunk: str):
        vcprint(data=chunk, chunks=True)
        vcprint(data="End of transmission", title="SocketPrinter.send_chunk_final")

    async def send_data(self, data: Any):
        if not isinstance(data, dict):
            vcprint(data=data, title="SocketPrinter.send_data")
            return

        if "data" in data:
            vcprint(
                "WARNING! Sending 'data' inside of data doesn't make any sense and will cause errors on the frontend. your data object should be a flat structure with the data you want to send.",
                color="red",
            )
            vcprint(
                "Your object is being modified prior to sending so ensure 'data' is never a key inside of the data, as this causes confusion and unecessary nesting which the frontend cannot process. Flatten structures to send what you're trying to send, without the user of additional layers of complexity.",
                color="yellow",
            )
            nested = data.pop("data")
            if isinstance(nested, dict):
                data.update(nested)
            else:
                data = nested

        vcprint(data=data, title="SocketPrinter.send_data")

    async def send_data_final(self, data: Any):
        await self.send_data(data)
        vcprint(data="End of transmission", title="SocketPrinter.send_data_final")

    async def send_status_update(self, status: str, system_message: Optional[str] = None, user_visible_message: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        if status not in ["confirm", "processing"]:
            vcprint("status must be one of: confirm, processing | For Errors and Completion, use send_error and send_end", title="Error", color="red")
            return

        if system_message is None:
            vcprint("system_message is required", title="Error", color="red")
            return

        info_object = {"status": status, "system_message": system_message, "metadata": metadata}

        if user_visible_message is not None:
            info_object["user_visible_message"] = user_visible_message

        vcprint(data=info_object, title="SocketPrinter.send_status_update")

    async def send_error(
        self,
        error_type: str,
        message: str,
        user_visible_message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if user_visible_message is None:
            user_visible_message = "Sorry. An error occurred. Please try again."

        error_object = {
            "message": message,
            "type": error_type,
            "user_visible_message": user_visible_message,
        }

        if code:
            error_object["code"] = code

        if details:
            error_object["details"] = self._serialize(details)

        vcprint(data=error_object, title="SocketPrinter.send_error")

    async def send_end(self):
        vcprint(data="End of transmission", title="SocketPrinter.send_end")

    async def fatal_error(
        self,
        error_type: str,
        message: str,
        user_visible_message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if user_visible_message is None:
            user_visible_message = "Sorry. An error occurred. Please try again."

        error_object = {
            "message": message,
            "type": error_type,
            "user_visible_message": user_visible_message,
        }

        if code:
            error_object["code"] = code

        if details:
            error_object["details"] = self._serialize(details)

        vcprint(data=error_object, title="SocketPrinter.fatal_error")
        vcprint(data="End of transmission", title="SocketPrinter.fatal_error")

    # THE FOLLOWING ARE LEGACY METHODS WHICH WILL BE REMOVED SOON. Please stop using them asap!
    async def send_text_chunk(self, text: str):
        vcprint(data=text, chunks=True)
        vcprint("Warning! send_text_chunk is depreciated. Use 'send_chunk' instead.", color="red")

    async def send_data_chunk(self, data: Any):
        vcprint(data=data, title="SocketPrinter.send_data_chunk")
        vcprint("Warning! send_data_chunk is depreciated. Use 'send_data' instead.", color="red")

    async def send_info(self, info: Any):
        vcprint(data=info, title="SocketPrinter.send_info")
        vcprint("Warning! send_info is depreciated. Use 'send_status_update' instead.", color="red")

    async def send_object(self, obj: any):
        await self.send_data(obj)
        vcprint("Warning! send_object is depreciated. Use 'send_data' instead.", color="red")

    async def finalize_event(self, obj: any):
        await self.send_data_final(obj)
        vcprint("Warning! finalize_event is depreciated. Use 'send_data_final' instead.", color="red")

    def _serialize(self, data):
        if data is None or isinstance(data, (bool, int, float, str)):  # Preserve JSON-serializable types
            return data
        elif isinstance(data, (datetime.datetime, datetime.date)):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, enum.Enum):
            return data.name
        elif isinstance(data, (set, tuple)):
            return [self._serialize(item) for item in data]
        elif isinstance(data, dict):
            return {key: self._serialize(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._serialize(item) for item in data]
        elif hasattr(data, "__str__"):
            return str(data)
        return data
