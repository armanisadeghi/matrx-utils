from core.services.socketio_app import sio
import datetime
import uuid
import enum
import uuid
import enum
import json

from matrx_utils.common import vcprint


info = False
debug = False
verbose = False


class MessageType:
    STREAM = "stream"
    ACTION = "action"
    ERROR = "error"
    INFO = "info"

class Status:
    RECEIVED = "received"
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SocketResponse:
    def __init__(self, initial_event_name, sid, namespace="/UserSession"):
        self.event_name = initial_event_name
        self.sid = sid
        self.namespace = namespace
        self.sio = sio

        vcprint(self.event_name, title="[SOCKET RESPONSE] INIT With Event Name", color="gold")

    async def initialize(self):
        # response = {"status": Status.RECEIVED, "event_name": self.event_name}
        # await self.sio.emit(self.initial_event_name, response, to=self.sid, namespace=self.namespace)
        await self.sio.emit(self.event_name, "Hi. This is a test message", to=self.sid, namespace=self.namespace)
        print("socket init send the following message: Hi. This is a test message to", self.event_name)
        await self.sio.emit(self.event_name, {"data": "Hi. This is test data"}, to=self.sid, namespace=self.namespace)
        print("socket init send the following data: {'data': 'Hi. This is test data'} to", self.event_name)



    async def send_chunk(self, chunk):
        print(chunk, end='')
        await self.sio.emit(self.event_name, chunk, to=self.sid, namespace=self.namespace)

    async def send_text_chunk(self, chunk):
        await self.sio.emit(self.event_name, chunk, to=self.sid, namespace=self.namespace)

    async def send_data_chunk(self, chunk):
        response = {"data": chunk}
        await self.sio.emit(self.event_name, response, to=self.sid, namespace=self.namespace)
        vcprint(response, color="gold")

    async def end_stream(self):
        response = {"status": Status.COMPLETED}
        await self.sio.emit(self.event_name, response, to=self.sid, namespace=self.namespace)
        vcprint(response, "Socket End", color="gold")


    async def send_message(
        self,
        type,
        status,
        data=None,
        user_message=None,
        related_id=None,
        send_safe=False
    ):
        """Send a structured message."""
        if send_safe:
            data = self.make_json_serializable(data)

        message = {
            "type": type,
            "status": status,
            "data": data,
            "user_message": user_message,
            "related_id": related_id,
            "request_details": {
                "event_name": self.event_name,
                "sid": self.sid,
                "namespace": self.namespace
            }
        }

        await self.sio.emit(self.event_name, message, to=self.sid, namespace=self.namespace)

    async def send_stream_chunk(self, chunk, related_id=None):
        """Send a streaming chunk."""
        await self.send_message(
            type=MessageType.STREAM,
            status=Status.PROCESSING,
            data=chunk,
            related_id=related_id
        )

    async def send_stream_complete(self, related_id=None, user_message="Stream completed"):
        """Signal stream completion."""
        await self.send_message(
            type=MessageType.STREAM,
            status=Status.COMPLETED,
            user_message=user_message,
            related_id=related_id
        )

    async def send_action(self, data, status=Status.COMPLETED, related_id=None, user_message=None, send_safe=True):
        """Send an action to drive frontend UI."""
        await self.send_message(
            type=MessageType.ACTION,
            status=status,
            data=data,
            user_message=user_message,
            related_id=related_id,
            send_safe=send_safe
        )

    async def send_error(self, user_message, data=None, related_id=None, send_safe=True):
        """Send an error message."""
        await self.send_message(
            type=MessageType.ERROR,
            status=Status.FAILED,
            data=data,
            user_message=user_message,
            related_id=related_id,
            send_safe=send_safe
        )

    async def send_info(self, user_message, status=Status.PROCESSING, data=None, related_id=None, send_safe=True):
        """Send an informational update."""
        await self.send_message(
            type=MessageType.INFO,
            status=status,
            data=data,
            user_message=user_message,
            related_id=related_id,
            send_safe=send_safe
        )

    async def send_image(self, image_data: bytes, mime_type: str) -> None:
        """Send an image to the client."""
        await sio.emit(self.event_name, {"image": image_data, "mime_type": mime_type}, to=self.sid, namespace=self.namespace)

    def make_json_serializable(self, data):
        """Recursively converts data to a JSON-serializable format."""
        if isinstance(data, (datetime, datetime.date)):
            return data.isoformat()
        elif isinstance(data, uuid.UUID):
            return str(data)
        elif isinstance(data, enum.Enum):
            return data.name
        elif isinstance(data, (set, tuple)):
            return [self.make_json_serializable(item) for item in data]
        elif isinstance(data, dict):
            return {key: self.make_json_serializable(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.make_json_serializable(item) for item in data]
        elif hasattr(data, "__str__"):
            return str(data)
        return data


    async def fatal_error(self, error_message: str) -> None:
        """Handle a fatal error and end the stream."""

        await self.send_message(type=MessageType.ERROR, status=Status.FAILED, data=error_message)
