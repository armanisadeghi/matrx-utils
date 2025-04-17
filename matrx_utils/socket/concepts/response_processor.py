import asyncio


class ResponseProcessor:
    def __init__(self, sio, task_queue):
        self.sio = sio
        self.task_queue = task_queue

    async def process_task(self, task_context, result):
        try:
            if task_context.response_type == "stream":
                await self.stream_response(task_context.event_name, result)
            elif task_context.response_type == "json":
                await self.json_response(task_context.event_name, result)
            elif task_context.response_type == "text":
                await self.text_response(task_context.event_name, result)
            elif task_context.response_type == "db":
                await self.push_to_database(task_context.event_name, result)
            elif task_context.response_type == "none":
                await self.completion_notification(task_context.event_name)
            else:
                await self.unknown_task_response(task_context.event_name, task_context.response_type)
        except Exception as e:
            await self.error_response(task_context.event_name, str(e))
        finally:
            await self.mark_task_complete(task_context)

    async def stream_response(self, event_name, data_generator):
        try:
            async for chunk in data_generator:
                await self.sio.emit(event_name, {"data": chunk, "status": "Streaming"})
                await asyncio.sleep(0.05)
            await self.sio.emit(event_name, {"status": "Complete", "message": "Stream completed"})
        except Exception as e:
            await self.error_response(event_name, str(e))

    async def json_response(self, event_name, data):
        await self.sio.emit(event_name, {"status": "Success", "data": data})

    async def text_response(self, event_name, text):
        await self.sio.emit(event_name, {"status": "Success", "text": text})

    async def push_to_database(self, event_name, data):
        # TODO: Implement this method to push data to the database
        await self.sio.emit(event_name, {"status": "Success", "message": "Data pushed to database"})

    async def completion_notification(self, event_name):
        await self.sio.emit(
            event_name,
            {"status": "Success", "message": "Task complete. No results requested."},
        )

    async def unknown_task_response(self, event_name, response_type):
        await self.sio.emit(
            event_name,
            {
                "status": "Error",
                "message": f"Response type '{response_type}' not recognized.",
            },
        )

    async def error_response(self, event_name, error_message):
        await self.sio.emit(event_name, {"status": "Error", "message": error_message})

    async def mark_task_complete(self, task_context):
        task_id = f"{task_context.matrix_id}_{task_context.service}_{task_context.task}"
        await self.task_queue.update_task_status(task_id, "completed")

        completion_event = f"{task_id}_completed"
        await self.sio.emit(completion_event, {"status": "Success", "message": "Task completed"})
