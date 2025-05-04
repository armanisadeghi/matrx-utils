# matrx_utils\database\orm\exceptions.py


class ORMException(Exception):
    """Base exception class for all ORM-related errors."""

    def __init__(self, message=None, model=None, details=None, class_name=None, method_name=None):
        self.model = model.__name__ if model else "Unknown Model"
        self.details = details or {}
        self._message = message
        self.class_name = class_name
        self.method_name = method_name
        super().__init__(self.format_message())

    @property
    def message(self):
        """Return the base error message"""
        return self._message or "An error occurred in the ORM"

    def format_message(self):
        """Format the complete error message with all details"""
        # Start with separator
        error_msg = ["\n" + "=" * 80 + "\n"]

        # Add location info if available
        if self.class_name and self.method_name:
            error_msg.append(f"[ERROR in {self.model}: {self.class_name}.{self.method_name}()]\n")
        else:
            error_msg.append(f"[ERROR in {self.model}]\n")

        # Add main message
        error_msg.append(f"Message: {self.message}")

        # Add details in a clean format
        if self.details:
            error_msg.append("\nContext:")
            for key, value in self.details.items():
                error_msg.append(f"  {key}: {value}")

        # End with separator
        error_msg.append("\n" + "=" * 80 + "\n")

        return "\n".join(error_msg)

    def __str__(self):
        return self.format_message()


class ValidationError(ORMException):
    """Raised when data validation fails."""

    def __init__(self, model=None, field=None, value=None, reason=None):
        details = {"field": field, "value": value, "reason": reason}
        message = f"Validation failed for {field if field else 'model'}"
        super().__init__(message=message, model=model, details=details)


class QueryError(ORMException):
    """Base class for query-related errors."""

    pass


class DoesNotExist(QueryError):
    """Raised when a queried object does not exist."""

    def __init__(self, model=None, filters=None, class_name=None, method_name=None):
        details = {"filters": filters or {}}
        filter_str = ", ".join(f"{k}={v}" for k, v in details["filters"].items())
        message = f"No {model.__name__ if model else 'object'} found matching: {filter_str}"
        super().__init__(
            message=message,
            model=model,
            details=details,
            class_name=class_name,
            method_name=method_name,
        )

    def format_message(self):
        """Override to provide a cleaner, less alarming message"""
        msg = ["\n" + "-" * 80 + "\n"]
        msg.append("NOTICE: Requested item not found")
        msg.append(f"\n{self.message}")
        if self.details.get("filters"):
            msg.append("\nSearch criteria:")
            for k, v in self.details["filters"].items():
                msg.append(f"  {k}: {v}")
        msg.append("\n" + "-" * 80 + "\n")
        return "\n".join(msg)


class MultipleObjectsReturned(QueryError):
    """Raised when a query returns multiple objects but one was expected."""

    def __init__(self, model=None, count=None, filters=None):
        details = {"count": count, "filters": filters or {}}
        filter_str = ", ".join(f"{k}={v}" for k, v in details["filters"].items())
        message = f"Found {count} objects when expecting one. Filters: {filter_str}"
        super().__init__(message=message, model=model, details=details)


class DatabaseError(ORMException):
    """Base class for database-related errors."""

    pass


class ConnectionError(DatabaseError):
    """Raised when database connection fails."""

    def __init__(self, model=None, db_url=None, original_error=None):
        details = {"db_url": db_url, "original_error": str(original_error)}
        message = f"Failed to connect to database: {original_error}"
        super().__init__(message=message, model=model, details=details)


class IntegrityError(DatabaseError):
    """Raised for database integrity violations."""

    def __init__(self, model=None, constraint=None, original_error=None):
        details = {"constraint": constraint, "original_error": str(original_error)}
        message = f"Database integrity error: {original_error}"
        super().__init__(message=message, model=model, details=details)


class TransactionError(DatabaseError):
    """Raised when a database transaction fails."""

    def __init__(self, model=None, operation=None, original_error=None):
        details = {"operation": operation, "original_error": str(original_error)}
        message = f"Transaction failed during {operation}: {original_error}"
        super().__init__(message=message, model=model, details=details)


class ConfigurationError(ORMException):
    """Raised when there's an error in ORM configuration."""

    def __init__(self, model=None, config_key=None, reason=None):
        details = {"config_key": config_key, "reason": reason}
        message = f"Configuration error for {config_key}: {reason}"
        super().__init__(message=message, model=model, details=details)


class CacheError(ORMException):
    """Raised when there's an error related to caching."""

    def __init__(self, model=None, operation=None, details=None, original_error=None):
        if original_error:
            details = details or {}
            details["original_error"] = str(original_error)
        message = f"Cache operation '{operation}' failed"
        super().__init__(message=message, model=model, details=details)


class StateError(ORMException):
    """Raised when there's an error in state management."""

    def __init__(self, model=None, operation=None, reason=None, details=None, original_error=None):
        details = details or {}
        if reason:
            details["reason"] = reason
        if original_error:
            details["original_error"] = str(original_error)
        message = f"State operation '{operation}' failed"
        if reason:
            message += f": {reason}"
        super().__init__(message=message, model=model, details=details)


class RelationshipError(ORMException):
    """Raised when there's an error in model relationships."""

    def __init__(self, model=None, related_model=None, field=None, reason=None):
        details = {
            "related_model": related_model.__name__ if related_model else None,
            "field": field,
            "reason": reason,
        }
        message = f"Relationship error: {reason}"
        super().__init__(message=message, model=model, details=details)


class AdapterError(ORMException):
    """Raised when there's an error specific to a database adapter."""

    def __init__(self, model=None, adapter_name=None, original_error=None):
        details = {"adapter": adapter_name, "original_error": str(original_error)}
        message = f"Error in {adapter_name} adapter: {original_error}"
        super().__init__(message=message, model=model, details=details)


class FieldError(ORMException):
    """Raised when there's an error related to model fields."""

    def __init__(self, model=None, field=None, value=None, reason=None):
        details = {"field": field, "value": value, "reason": reason}
        message = f"Field error for {field}: {reason}"
        super().__init__(message=message, model=model, details=details)


class MigrationError(ORMException):
    """Raised when there's an error during database migration."""

    def __init__(self, model=None, migration=None, original_error=None):
        details = {"migration": migration, "original_error": str(original_error)}
        message = f"Migration '{migration}' failed: {original_error}"
        super().__init__(message=message, model=model, details=details)


class ParameterError(ORMException):
    """Raised when query parameters are invalid or malformed."""

    def __init__(
        self,
        model=None,
        query=None,
        args=None,
        reason=None,
        class_name=None,
        method_name=None,
    ):
        details = {
            "query": query,
            "args": args if args is not None else [],
            "reason": reason,
        }
        message = f"Invalid query parameter: {reason}"
        super().__init__(
            message=message,
            model=model,
            details=details,
            class_name=class_name,
            method_name=method_name,
        )


class UnknownDatabaseError(ORMException):
    """Raised when an unexpected database error occurs, capturing full context."""

    def __init__(
        self,
        model=None,
        operation=None,
        query=None,
        args=None,
        traceback=None,
        original_error=None,
    ):
        details = {
            "operation": operation,
            "query": query,
            "args": args if args is not None else [],
            "traceback": traceback,
            "original_error": str(original_error) if original_error else "Unknown",
        }
        message = f"Unexpected database error during {operation}: {str(original_error)}"
        super().__init__(message=message, model=model, details=details)
