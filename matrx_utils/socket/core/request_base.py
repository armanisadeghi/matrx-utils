from matrx_utils.socket.core.socket_response import SocketResponse
from matrx_utils.socket.core.stream.stream_handler import SocketStreamHandler
from matrx_utils.socket.utils.log_request import handle_error
from matrx_utils.socket.schema.schema_processor import ValidationSystem
from core.services.socketio_app import sio
from matrx_utils.common import vcprint


verbose = True
debug = False
info = False

DEFINITION_NOT_REQUIRED = object()


def validate_object_structure(obj):
    errors = []

    if not isinstance(obj, dict):
        errors.append("Object is not a dictionary")
        return None, None, None, None, None, errors

    task = obj.get("task")
    index = obj.get("index")
    stream = obj.get("stream")
    task_data = obj.get("taskData")

    if task is None:
        errors.append("Task was not provided. This field is required in the task object.")
    if index is None:
        errors.append("Index was not provided. This field is required in the task object.")
    if stream is None:
        errors.append("Stream was not provided. This field is required in the task object.")
    if task_data is None:
        errors.append("TaskData was not provided. This field is required in the task object.")

    if errors:
        return None, None, None, None, None, errors

    return task, index, stream, task_data, errors

class SocketRequestBase:
    def __init__(self, sid, data, namespace, event, user_id):
        self.sid = sid
        self.data = data
        self.namespace = namespace
        self.event = event
        self.prepared_tasks = []
        self.context_builder = ValidationSystem()
        self.namespace_handler = sio.namespace_handlers[namespace]
        self.user_id = user_id

    async def initialize(self):
        """Set up basic request validation and stream handlers for all tasks"""
        try:
            if not self.data:
                return await self._handle_error("No data provided")

            all_successful = True

            for obj in self.data:
                task, index, stream, task_data, errors = validate_object_structure(obj)
                if errors:
                    await self._handle_error({"errors": errors})
                    all_successful = False
                    continue

                result = self.context_builder.validate(task_data, self.event, task, self.user_id)
                vcprint(result, title="Validation Result", color="gold")

                context = result.get("context")
                errors = result.get("errors")

                if errors is not None and errors:
                    vcprint(errors, title="Validation Errors", pretty=True, color="red")

                # event_name = f"{self.sid}_{task}_{index}"
                event_name = context.get("response_listener_event", f"{self.sid}_{task}_{index}")
                vcprint(event_name, title="SocketRequestBase with Event Name", color="blue")

                stream_handler = SocketStreamHandler(event_name=event_name, sid=self.sid, namespace=self.namespace)

                stream_handler.send_chunk(f"Processing task {task} with index {index}")


                # response_handler = SocketResponse(
                #     initial_event_name=event_name,
                #     sid=self.sid,
                #     namespace=self.namespace,
                # )


                # await response_handler.initialize()

                # await response_handler.send_chunk(f"Processing task {task} with index {index}")

                if errors:
                    vcprint(errors, title="Validation Errors", pretty=True, color="red")
                    all_successful = False
                    await stream_handler.fatal_error(errors)
                    return

                else:
                    self.prepared_tasks.append({"stream_handler": stream_handler, "task": task, "user_id": self.user_id, "context": context})

            return all_successful, self.prepared_tasks

        except Exception as e:
            vcprint(e, title="Error", color="red")
            return await self._handle_error(e)

    async def _handle_error(self, error_message):
        """Centralized error handling"""
        stream_handler = SocketStreamHandler(event_name="error", sid=self.sid, namespace=self.namespace)
        # response_handler = SocketResponse(initial_event_name=self.event, sid=self.sid, namespace=self.namespace, client_event_name=None)
        await handle_error(stream_handler, error_message)
        return False

    async def process_request(self, obj):
        """Override this method in specific request handlers"""
        raise NotImplementedError

    async def get_service_instance(self, service_class, sid, event, stream_handler=None):
        return await self.namespace_handler.get_service_instance(
            service_class=service_class,
            sid=sid,
            stream_handler=stream_handler,
            event=event,
        )
