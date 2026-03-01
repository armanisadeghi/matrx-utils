
class ValidationError(ValueError):
    """Raised when a validator fails."""

    def __init__(self, message, code=None, params=None):
        self.message = message
        self.code = code
        self.params = params or {}

        try:
            formatted_message = self.message % self.params
        except (KeyError, TypeError, ValueError):
            formatted_message = self.message

        super().__init__(formatted_message)