# database/orm/core/error_handling.py

from contextlib import asynccontextmanager
import traceback
from matrx_utils.database.orm.exceptions import (
    ORMException,
    CacheError,
    DatabaseError,
    MultipleObjectsReturned,
    DoesNotExist,
)
from matrx_utils import vcprint


@asynccontextmanager
async def handle_orm_operation(operation_name, model=None, **context):
    """Context manager for handling ORM operations with proper error encapsulation."""
    try:
        yield
    except MultipleObjectsReturned as e:
        vcprint(str(e), "MultipleObjectsReturned", color="light_yellow")
        raise
    except DoesNotExist as e:
        vcprint(str(e), "DoesNotExist", color="light_yellow")
        raise
    except DatabaseError as e:
        # Log the error and traceback once here, then re-raise
        vcprint(str(e), "DatabaseError", color="red")
        vcprint("Here is the traceback:", "TracebackHeader", color="yellow")
        vcprint(traceback.format_exc(), "Traceback", color="white")  # Use vcprint for consistency, but white
        raise  # Re-raise the original exception (e.g., ParameterError)
    except Exception as e:
        if isinstance(e, ORMException):
            # If an ORMException slips through (shouldn't for DatabaseError), log it once
            vcprint(str(e), "ORMException", color="red")
            vcprint("Here is the traceback:", "TracebackHeader", color="yellow")
            vcprint(traceback.format_exc(), "Traceback", color="white")
            raise
        # Unexpected non-ORM exceptions
        vcprint(
            f"Unexpected error in {operation_name}: {str(e)}",
            "UnexpectedError",
            color="red",
        )
        vcprint("Here is the traceback:", "TracebackHeader", color="yellow")
        vcprint(traceback.format_exc(), "Traceback", color="yellow")
        raise CacheError(model=model, operation=operation_name, details=context, original_error=e)
