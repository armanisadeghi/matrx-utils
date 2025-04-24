from functools import wraps
import traceback
import sys

DEFAULT_CLIENT_MESSAGE = "Oops. Something went wrong. Please reload the page and try again."


class AppError(Exception):
    def __init__(
        self,
        message: str,
        error_type: str = "GenericError",
        client_visible: str = None,
        context: dict = None,
    ):
        self.error = {
            "status": "error",
            "type": error_type,
            "message": message,
            "client_visible": client_visible if client_visible is not None else DEFAULT_CLIENT_MESSAGE,
            "context": context or {},
            "traceback": traceback.format_exc() if traceback.format_exc() != "None\n" else "No traceback available",
        }
        super().__init__(message)


def handle_errors(func):
    @wraps(func)
    async def wrapper(cls_or_self, *args, **kwargs):
        try:
            return await func(cls_or_self, *args, **kwargs)
        except Exception as e:
            # Don't re-wrap AppErrors
            if isinstance(e, AppError):
                raise

            # Get the original traceback before we create any new exceptions
            original_traceback = traceback.format_exc()

            try:
                # Handle case where cls_or_self is a class (classmethod) or instance
                if isinstance(cls_or_self, type):  # Class method case
                    context = {"class": cls_or_self.__name__}
                    app_error = AppError(
                        message=str(e),
                        error_type=e.__class__.__name__,
                        client_visible=DEFAULT_CLIENT_MESSAGE,
                        context=context,
                    )
                else:  # Instance method case
                    # Safely check if _report_error exists and is callable
                    if hasattr(cls_or_self, "_report_error") and callable(cls_or_self._report_error):
                        # Call directly without exception wrapping
                        context = {"class": cls_or_self.__class__.__name__}
                        if hasattr(cls_or_self, "_get_error_context") and callable(cls_or_self._get_error_context):
                            try:
                                context.update(cls_or_self._get_error_context())
                            except Exception:
                                # Ignore errors in _get_error_context
                                pass

                        app_error = AppError(
                            message=str(e),
                            error_type=e.__class__.__name__,
                            client_visible=DEFAULT_CLIENT_MESSAGE,
                            context=context,
                        )
                    else:
                        # Fallback if _report_error doesn't exist
                        context = {"class": cls_or_self.__class__.__name__}
                        app_error = AppError(
                            message=str(e),
                            error_type=e.__class__.__name__,
                            client_visible=DEFAULT_CLIENT_MESSAGE,
                            context=context,
                        )

                # Print the original error for debugging
                print(f"Error in {func.__name__}:", file=sys.stderr)
                print(original_traceback, file=sys.stderr)

                raise app_error

            except Exception as wrapping_error:
                if isinstance(wrapping_error, AppError):
                    # If we managed to create an AppError, use it
                    raise
                else:
                    # If error handling itself failed, fall back to simplest case
                    print(
                        f"Error handler failed! Original error in {func.__name__}:",
                        file=sys.stderr,
                    )
                    print(original_traceback, file=sys.stderr)
                    print("Error handling failed with:", file=sys.stderr)
                    print(traceback.format_exc(), file=sys.stderr)

                    # Raise the original exception to avoid masking it with error handling errors
                    raise e

    return wrapper
