from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class BaseAppError(Exception):
    message: Optional[str] = None
    user_visible_message: Optional[str] = None
    code: Optional[str] = None
    details: Dict = field(default_factory=dict)
    error_type: Optional[str] = None

    async def send_error_via_socket(self, stream_handler, end_stream=False):
        if stream_handler is not None:
            await stream_handler.send_error(error_type=self.error_type,
                                            message=self.message,
                                            user_visible_message=self.user_visible_message,
                                            code=self.code,
                                            details=self.details)
            if end_stream:
                await stream_handler.send_end()
