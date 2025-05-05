from ..base import BaseAppError
from dataclasses import dataclass

@dataclass
class ServiceNotDefinedError(BaseAppError):
    message: str = "Service not found"
    user_visible_message: str = "The service you are trying to use is not available. Please try again later."
    code: str = "service_404"
    error_type: str = "not_found_error"