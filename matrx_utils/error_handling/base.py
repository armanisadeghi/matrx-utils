class BaseAppError(Exception):
    def __init__(self, message=None, user_visible_message=None, code=None, details=None, error_type=None):
        self.message = message
        self.user_visible_message = user_visible_message
        self.code = code
        self.details = details or {}
        self.error_type = error_type
        super().__init__(message)  # This is crucial for Exception to work properly

    async def send_error_via_socket(self, stream_handler, end_stream=False):
        await stream_handler.send_error(error_type=self.error_type,
                                        message=self.message,
                                        user_visible_message=self.user_visible_message,
                                        code=self.code,
                                        details=self.details)
        if end_stream:
            await stream_handler.send_end()
