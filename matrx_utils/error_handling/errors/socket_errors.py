from ..base import BaseAppError


class ServiceNotDefinedError(BaseAppError):
    def __init__(self,
                 message="Service not found",
                 user_visible_message="The service you are trying to use is not available. Please try again later.",
                 code="service_404",
                 details=None,
                 error_type="not_found_error"):

        super().__init__(message, user_visible_message, code, details, error_type)
