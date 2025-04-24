import asyncio
from typing import Any, Optional
from matrx_utils.socket.core.stream.stream_base import StreamInterface
from matrx_utils import vcprint
import socketio

LOCAL_DEBUG_OVERRIDE = True


class SocketStreamHandler(StreamInterface):
    def __init__(self, event_name: str, sid: str, namespace: str = "/UserSession", debug: bool = False, sio_instance=None):
        super().__init__(event_name)
        if not isinstance(sid, str) or not sid.strip():
            raise ValueError("sid must be a non-empty string")
        if not isinstance(namespace, str) or not namespace.strip():
            raise ValueError("namespace must be a non-empty string")

        self.sid = sid
        self.namespace = namespace
        self.debug = LOCAL_DEBUG_OVERRIDE or debug

        self._sio: socketio.AsyncServer = sio_instance
        if not self._sio:
            raise ValueError("Please initialize with a Stream Handler with SIO instance.")

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
            await self._sio.emit(self.event_name, {"data": chunk}, to=self.sid, namespace=self.namespace)
            await self.debug_print(chunk, "send_data_chunk")

        except Exception as e:
            await self._handle_exception("send_data_chunk", e)

    async def send_object(self, obj: Any) -> None:
        try:
            self.ensure_not_ended()
            serialized_obj = self.make_json_serializable(obj)
            await self.debug_print(serialized_obj, "send_object")
            await self._sio.emit(self.event_name, {"data": serialized_obj}, to=self.sid, namespace=self.namespace)
        except Exception as e:
            await self._handle_exception("send_object", e)

    async def send_info(self, info_type: str, message: str, data: Optional[Any] = None) -> None:
        try:
            self.ensure_not_ended()
            payload = {"info": message}
            if data is not None:
                payload = {"info": self.make_json_serializable(data)}
            await self.debug_print(payload, "send_info")
            await self._sio.emit(self.event_name, payload, to=self.sid, namespace=self.namespace)
        except Exception as e:
            await self._handle_exception("send_info", e)

    async def send_confirmation(self, message: str, data: Optional[Any] = None) -> None:
        await self.send_info("confirm", message, data)

    async def finalize_event(self, results, message="") -> None:
        try:
            self.ensure_not_ended()
            payload = {"message": message, "data": self.make_json_serializable(results)}
            await self.debug_print(payload, "finalize_event")
            await self._sio.emit(self.event_name, payload, to=self.sid, namespace=self.namespace)
            await self.end_stream()
        except Exception as e:
            await self._handle_exception("finalize_event", e)

    async def send_action(self, action: str, data: Optional[Any] = None):
        try:
            self.ensure_not_ended()
            payload = {"action": action}
            if data is not None:
                payload["data"] = self.make_json_serializable(data)
            await self.debug_print(payload, "send_action")
            await self._sio.emit(self.event_name, {"action": payload}, to=self.sid, namespace=self.namespace)
        except Exception as e:
            await self._handle_exception("send_action", e)

    async def send_image(self, image_data: bytes, mime_type: str) -> None:
        try:
            self.ensure_not_ended()
            await self.debug_print(f"Image ({mime_type}, {len(image_data)} bytes)", "send_image")

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
        await self.debug_print(error_msg, "handle_exception")
        await self._sio.emit(self.event_name, {"error": error_msg}, to=self.sid, namespace=self.namespace)
        await self.end_stream()
        raise exception

    async def end_stream(self):
        """Mark the stream as ended and perform cleanup."""
        await self._sio.emit(self.event_name, {"end": True}, to=self.sid, namespace=self.namespace)

        if not self._is_ended:
            self._is_ended = True

    async def send_error(self, error_object):
        print("sending error", error_object)
        await self._sio.emit(self.event_name, error_object, to=self.sid, namespace=self.namespace)
        await self.debug_print(error_object, "_send_error")


    async def debug_print(self, data, method_name):
        if not self.debug:
            return
        title = f"[SOCKET STREAM HANDLER] {method_name} for event: {self.event_name}"
        vcprint(data=data, title=title, color="blue")
