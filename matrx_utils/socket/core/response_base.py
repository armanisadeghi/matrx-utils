import asyncio
import datetime
import enum
import uuid
from matrx_utils import vcprint
import socketio

LOCAL_DEBUG_OVERRIDE = True


class SocketResponse:
    def __init__(self, event_name: str, sid: str, namespace: str = "/UserSession", debug: bool = False, sio_instance: socketio.AsyncServer = None):
        self.event_name = event_name
        self.sid = sid
        self.namespace = namespace
        self._sio = sio_instance
        self.debug = LOCAL_DEBUG_OVERRIDE or debug
        self._initialize()


    def _initialize(self):
        if not self._sio:
            raise ValueError("Please initialize SocketResponse with SIO instance. Hint: look at SocketEmitter initialization")
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
        vcprint(self.event_name, title="[SOCKET RESPONSE] INIT With Event Name", color="gold")

    async def _send_chunk(self, chunk):
        print(chunk, end="")
        await self._sio.emit(self.event_name, chunk, to=self.sid, namespace=self.namespace)

    async def _send_data(self, data):
        response = {"data": self._serialize(data)}
        await self._sio.emit(self.event_name, response, to=self.sid, namespace=self.namespace)
        self._debug_print(response, "_send_data")

    async def _send_info(self, info_object):
        response = {"info": info_object}
        await self._sio.emit(self.event_name, response, to=self.sid, namespace=self.namespace)
        self._debug_print(response, "_send_info")

    async def _send_error(self, error_object):
        response = {"error": error_object}
        await self._sio.emit(self.event_name, response, to=self.sid, namespace=self.namespace)
        self._debug_print(response, "_send_error")

    async def _send_end(self):
        response = {"end": True}
        await self._sio.emit(self.event_name, response, to=self.sid, namespace=self.namespace)
        self._debug_print(response, "_send_end")

    def _debug_print(self, data, method_name):
        if not self.debug:
            return
        title = f"[SOCKET RESPONSE] {method_name} for event: {self.event_name}"
        vcprint(data=data, title=title, color="blue")

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
