# Creating services

1. Create a class that extends SocketServiceBase
 - Must include all args as self.some_attribute
 - Must include a method for process_task and mic_check

 Example:

 ```python
 class LogService(SocketServiceBase):
    def __init__(self, log_dir: str = "/var/log/aidream"):
        self.log_dir = log_dir
        self.logger = logging.getLogger(__name__)
        self.mic_check_message = None
        # Default attributes for log operations
        self.filename = "application logs"  # Use user-friendly name
        self.lines = 100
        self.search = None
        self.interval = 1.0
        self._tail_task = None  # Track tailing task
        self._tail_active = False  # Flag to control tailing
        self._ensure_log_dir()
        super().__init__(app_name="log_service", service_name="log_service", log_level="INFO", batch_print=False)

    async def process_task(self, task, task_context=None, process=True):
        vcprint("Log Service Processing Task")
        return await self.execute_task(task, task_context, process)

    async def mic_check(self):
        print("Mic Check")
        print("Message: " + str(self.mic_check_message))
        await self.stream_handler.send_text_chunk(
            f"Log Service Mic Check Response to: {self.mic_check_message} | One more response coming from Log Service.\n\n"
        )
        await self.stream_handler.end_stream()
        print("Mic Check Done")
```

2. Create a method for each 'task' you want to extend
3. Create a scheme for each task
4. Create a structure for the service that brings all task schemas together
5. Add the service to service_factory


