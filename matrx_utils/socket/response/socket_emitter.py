from typing import Any, Dict, Optional
from matrx_utils import vcprint
from matrx_utils.socket.response.response_base import SocketResponse


class SocketEmitter(SocketResponse):
    def __init__(self, event_name: str, sid: str, namespace: str = "/UserSession", debug: bool = False):
        super().__init__(event_name, sid, namespace, debug)

    async def send_chunk(self, chunk: str):
        await self._send_chunk(chunk)

    async def send_chunk_final(self, chunk: str):
        await self._send_chunk(chunk)
        await self._send_end()

    async def send_data(self, data: Any):
        if not isinstance(data, dict):
            await self._send_data(data)
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

        await self._send_data(data)

    async def send_data_final(self, data: Any):
        await self.send_data(data)
        await self._send_end()

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

        await self._send_info(info_object)

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

        await self._send_error(error_object)

    async def send_end(self):
        await self._send_end()

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

        await self._send_error(error_object)
        await self._send_end()

    # THE FOLLOWING ARE LEGACY METHODS WHICH WILL BE REMOVED SOON. Please stop using them asap!
    async def send_text_chunk(self, text: str):
        await self._send_chunk(text)
        vcprint("Warning! send_text_chunk is depreciated. Use 'send_chunk' instead.", color="red")

    async def send_data_chunk(self, data: Any):
        await self._send_data(data)
        vcprint("Warning! send_data_chunk is depreciated. Use 'send_data' instead.", color="red")

    async def send_info(self, info: Any):
        await self._send_info(info)
        vcprint("Warning! send_info is depreciated. Use 'send_status_update' instead.", color="red")

    async def send_object(self, obj: any):
        await self.send_data(obj)
        vcprint("Warning! send_object is depreciated. Use 'send_data' instead.", color="red")

    async def finalize_event(self, obj: any):
        await self.send_data_final(obj)
        vcprint("Warning! finalize_event is depreciated. Use 'send_data_final' instead.", color="red")

    async def non_fatal_error(
        self,
        string_error_message: str,
    ):
        vcprint("Warning! non_fatal_error is depreciated. Use 'send_error' instead with updated parameters.", color="red")
        error_object = {
            "message": string_error_message,
            "type": "error",
            "user_visible_message": "Sorry. An error occurred. Please try again.",
        }

        await self._send_error(error_object)
