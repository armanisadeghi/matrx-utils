import asyncio
from typing import Any, Optional
from matrx_utils.socket.core.stream.stream_base import StreamInterface
from core.services.socketio_app import sio
from matrx_utils.common import vcprint

verbose = False


class SocketStreamHandler(StreamInterface):
    def __init__(self, event_name: str, sid: str, namespace: str = "/UserSession"):
        super().__init__(event_name)
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError("sid must be a non-empty string")
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError("namespace must be a non-empty string")

        self.sid = sid
        self.namespace = namespace
        self._sio = sio
        try:
            asyncio.create_task(
                self._sio.emit(
                    "incoming_stream_event",
                    {"event_name": self.event_name},
                    to=self.sid,
                    namespace=self.namespace,
                )
            )
        except Exception as e:
            vcprint(data=e, title="Exception", color="red")

    async def send_chunk(self, chunk: str) -> None:
        await self._sio.emit(self.event_name, chunk, to=self.sid, namespace=self.namespace)

    async def send_text_chunk(self, chunk: str) -> None:
        await self._sio.emit(self.event_name, chunk, to=self.sid, namespace=self.namespace)

    async def send_data_chunk(self, chunk: str) -> None:
        try:
            self.ensure_not_ended()

            vcprint(
                data=chunk,
                title=f"[{self.__class__.__name__} Chunk] {self.event_name} to {self.sid}",
                verbose=verbose,
                color="blue",
                chunks=True,
            )
            await self._sio.emit(self.event_name, {"data": chunk}, to=self.sid, namespace=self.namespace)
        except Exception as e:
            await self._handle_exception("send_chunk", e)

    async def send_object(self, obj: Any) -> None:
        try:
            self.ensure_not_ended()
            vcprint(
                data=obj,
                title=f"[{self.__class__.__name__} Object] {self.event_name} to {self.sid}",
                verbose=verbose,
                color="green",
                pretty=True,
            )
            await self._sio.emit(self.event_name, {"data": obj}, to=self.sid, namespace=self.namespace)
            await self.end_stream()
        except Exception as e:
            await self._handle_exception("send_object", e)

    async def send_info(self, info_type: str, message: str, data: Optional[Any] = None) -> None:
        try:
            self.ensure_not_ended()
            super().send_info(info_type, message, data)  # Validate inputs
            title = f"[{self.__class__.__name__} Info] {info_type} to {self.sid}"
            payload = {"message": message}
            if data is not None:
                payload["data"] = data
            vcprint(data=payload, title=title, verbose=verbose, color="yellow", pretty=True)
            socket_payload = {
                "status": info_type,
                "message": message,
                "data": data,
                "request_details": {
                    "event_name": self.event_name,
                    "sid": self.sid,
                    "namespace": self.namespace,
                },
            }
            await self._sio.emit(
                self.event_name,
                {"info": socket_payload},
                to=self.sid,
                namespace=self.namespace,
            )
        except Exception as e:
            await self._handle_exception("send_info", e)

    async def finalize_event(self, results, message="") -> None:
        try:
            socket_payload = {
                "status": "completed",
                "message": message,
                "results": results,
                "request_details": {
                    "event_name": self.event_name,
                    "sid": self.sid,
                    "namespace": self.namespace,
                },
            }
            await self._sio.emit(
                self.event_name,
                {"data": socket_payload},
                to=self.sid,
                namespace=self.namespace,
            )
            await self.end_stream()
        except Exception as e:
            await self._handle_exception("send_info", e)

    async def send_action(self, action: str, data: Optional[Any] = None):
        self.ensure_not_ended()
        super().send_action(action, data)
        title = f"[{self.__class__.__name__} Action] {action} to {self.sid}"
        payload = {"action": action}
        if data is not None:
            payload["data"] = data
        vcprint(data=payload, title=title, verbose=verbose, color="yellow", pretty=True)
        await self._sio.emit(self.event_name, {"action": payload}, to=self.sid, namespace=self.namespace)

    async def send_image(self, image_data: bytes, mime_type: str) -> None:
        try:
            self.ensure_not_ended()
            vcprint(
                data=f"Image ({mime_type}, {len(image_data)} bytes)",
                title=f"[{self.__class__.__name__} Image] {self.event_name} to {self.sid}",
                verbose=verbose,
                color="magenta",
            )
            await self._sio.emit(
                self.event_name,
                {"image": {"data": image_data, "mime_type": mime_type}},
                to=self.sid,
                namespace=self.namespace,
            )
        except Exception as e:
            await self._handle_exception("send_image", e)

    async def _handle_exception(self, method_name: str, exception: Exception):
        error_msg = f"Error in {method_name}: {str(exception)}"
        vcprint(data=error_msg, title="Exception", color="red", pretty=True)
        await self._sio.emit(self.event_name, {"error": error_msg}, to=self.sid, namespace=self.namespace)
        await self.end_stream()
        raise exception

    async def end_stream(self):
        """Mark the stream as ended and perform cleanup."""
        await self._sio.emit(self.event_name, {"end": True}, to=self.sid, namespace=self.namespace)

        if not self._is_ended:
            self._is_ended = True
