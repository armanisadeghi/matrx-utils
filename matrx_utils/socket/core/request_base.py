from matrx_utils.socket.core.socket_emitter import SocketEmitter
from matrx_utils.socket.utils.log_request import handle_error
from matrx_utils.socket.schema.schema_processor import ValidationSystem
from matrx_utils import vcprint


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
    def __init__(self, sid, data, namespace, event, user_id, sio_instance):
        self.sid = sid
        self.data = data
        self.namespace = namespace
        self.event = event
        self.prepared_tasks = []
        self.context_builder = ValidationSystem()
        self.user_id = user_id
        self.sio_instance = sio_instance

    async def initialize(self):
        """Set up basic request validation and stream handlers for all tasks"""
        try:
            if not self.data:
                return await self._handle_error("No data provided")

            all_successful = True

            for obj in self.data:
                task, index, stream, task_data, errors = validate_object_structure(obj)

                result = self.context_builder.validate(task_data, self.event, task, self.user_id)
                vcprint(result, title="Validation Result", color="gold")

                context = result.get("context")

                event_name = context.get("response_listener_event", f"{self.sid}_{task}_{index}")
                vcprint(event_name, title="SocketRequestBase with Event Name", color="blue")

                stream_handler = SocketEmitter(event_name=event_name, sid=self.sid, namespace=self.namespace, sio_instance=self.sio_instance)


                if task == 'mic_check':
                    await self.system_mic_check(stream_handler)

                await stream_handler.send_status_update(status="confirm", system_message=f"Processing task {task} with index {index}", user_visible_message=f"Yay! You're about to get some good stuff!")

                errors = result.get("errors")

                if errors is not None and errors:
                    vcprint(errors, title="Validation Errors", color="red")
                    error_object = {
                        "error_type": "validation_error",
                        "message": "SocketRequestBase found errors during task validation. See Details.",
                        "user_visible_message": "Your request was invalid. Please try again.",
                        "details": errors,
                    }

                    await stream_handler.fatal_error(**error_object)

                    all_successful = False
                    return all_successful, self.prepared_tasks

                else:
                    self.prepared_tasks.append({"stream_handler": stream_handler, "task": task, "user_id": self.user_id, "context": context})

            return all_successful, self.prepared_tasks

        except Exception as e:
            vcprint(e, title="Error", color="red")
            error_object = {"message": "Error in SocketRequestBase during task initialization. This is likely a result of an incorrect task object structure.", "error": str(e)}
            await self._handle_error(error_object)

            return await self._handle_error(e)

    async def _handle_error(self, error_object):
        """Centralized error handling"""
        stream_handler = SocketEmitter(event_name="global_error", sid=self.sid, namespace=self.namespace)
        await stream_handler.send_error(**error_object)
        return False

    async def process_request(self, obj):
        """Override this method in specific request handlers"""
        raise NotImplementedError

    async def system_mic_check(self, stream_handler):

        status_object = {
            "status": "confirm",
            "system_message": "System Mic Check",
            "user_visible_message": "Hi User. We're just doing some testing. Sorry.",
            "metadata": {"some_key": "This is the system mic check sent as metadata"},
        }
        await stream_handler.send_status_update(**status_object)

        await stream_handler.send_chunk("This is the system mic check sent as a chunk")

        data_object = {
            "some_key": "This is the system mic check sent as data",
        }
        await stream_handler.send_data(data_object)
        error_object = {
            "error_type": "known_error_type_predefined_in_frontend_and_backend",  # or "unknown_error"
            "message": "This is the system mic check sent as an error",
            "code": "error_code",
            "details": {"some_key": "This is the system mic check sent as details"},
        }
        await stream_handler.send_error(**error_object)

        await stream_handler.send_chunk("You will now receive an individual chunk, data, status update, and every type of transmission available for this service directly from the service and sub-services.")
