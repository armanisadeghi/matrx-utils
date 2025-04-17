from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable

from contextlib import contextmanager


class BaseMiddleware(ABC):
    @abstractmethod
    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """Process the query before it's executed."""
        pass

    @abstractmethod
    async def process_result(self, result: Any) -> Any:
        """Process the result after query execution."""
        pass


class MiddlewareManager:
    def __init__(self):
        self.middlewares: List[BaseMiddleware] = []

    def add_middleware(self, middleware: BaseMiddleware):
        self.middlewares.append(middleware)

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        for middleware in self.middlewares:
            query = await middleware.process_query(query)
        return query

    async def process_result(self, result: Any) -> Any:
        for middleware in reversed(self.middlewares):
            result = await middleware.process_result(result)
        return result


# Example middleware implementations


class QueryLoggingMiddleware(BaseMiddleware):
    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Executing query: {query}")
        return query

    async def process_result(self, result: Any) -> Any:
        print(f"Query result: {result}")
        return result


class CachingMiddleware(BaseMiddleware):
    def __init__(self):
        self.cache = {}

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = str(query)
        if cache_key in self.cache:
            query["use_cache"] = True
            query["cached_result"] = self.cache[cache_key]
        return query

    async def process_result(self, result: Any) -> Any:
        # In a real implementation, you'd want to be more selective about what you cache
        self.cache[str(result)] = result
        return result


class SoftDeleteMiddleware(BaseMiddleware):
    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        if "where" not in query:
            query["where"] = {}
        query["where"]["deleted_at"] = None
        return query

    async def process_result(self, result: Any) -> Any:
        return result


class TenantIsolationMiddleware(BaseMiddleware):
    def __init__(self, get_current_tenant_id: Callable[[], str]):
        self.get_current_tenant_id = get_current_tenant_id

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        tenant_id = self.get_current_tenant_id()
        if "where" not in query:
            query["where"] = {}
        query["where"]["tenant_id"] = tenant_id
        return query

    async def process_result(self, result: Any) -> Any:
        return result


class EncryptionMiddleware(BaseMiddleware):
    def __init__(
        self,
        encrypt_func: Callable[[Any], Any],
        decrypt_func: Callable[[Any], Any],
        sensitive_fields: List[str],
    ):
        self.encrypt_func = encrypt_func
        self.decrypt_func = decrypt_func
        self.sensitive_fields = sensitive_fields

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        if "values" in query:
            for field in self.sensitive_fields:
                if field in query["values"]:
                    query["values"][field] = self.encrypt_func(query["values"][field])
        return query

    async def process_result(self, result: Any) -> Any:
        if isinstance(result, dict):
            for field in self.sensitive_fields:
                if field in result:
                    result[field] = self.decrypt_func(result[field])
        elif isinstance(result, list):
            for item in result:
                for field in self.sensitive_fields:
                    if field in item:
                        item[field] = self.decrypt_func(item[field])
        return result


class ValidationMiddleware(BaseMiddleware):
    def __init__(self, validation_rules: Dict[str, Callable[[Any], bool]]):
        self.validation_rules = validation_rules

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        if "values" in query:
            for field, rule in self.validation_rules.items():
                if field in query["values"]:
                    if not rule(query["values"][field]):
                        raise ValueError(f"Validation failed for field {field}")
        return query

    async def process_result(self, result: Any) -> Any:
        return result


class PerformanceMonitoringMiddleware(BaseMiddleware):
    def __init__(self):
        self.query_times = {}

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        import time

        query["start_time"] = time.time()
        return query

    async def process_result(self, result: Any) -> Any:
        import time

        end_time = time.time()
        query_time = end_time - result["start_time"]
        print(f"Query executed in {query_time:.4f} seconds")
        return result


class AuditingMiddleware(BaseMiddleware):
    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        if query.get("operation") in ["insert", "update", "delete"]:
            self.log_operation(query)
        return query

    async def process_result(self, result: Any) -> Any:
        return result

    def log_operation(self, query):
        # Log the operation details
        pass


class SchemaEvolutionMiddleware(BaseMiddleware):
    def __init__(self, schema_version: str):
        self.schema_version = schema_version

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        # Modify query based on schema version
        return query

    async def process_result(self, result: Any) -> Any:
        # Transform result based on schema version
        return result


class DataTransformationMiddleware(BaseMiddleware):
    def __init__(self, transformations: Dict[str, Callable[[Any], Any]]):
        self.transformations = transformations

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        if "values" in query:
            for field, transform in self.transformations.items():
                if field in query["values"]:
                    query["values"][field] = transform(query["values"][field])
        return query

    async def process_result(self, result: Any) -> Any:
        # Apply inverse transformations to result
        return result


class AccessControlMiddleware(BaseMiddleware):
    def __init__(self, get_user_permissions: Callable[[], List[str]]):
        self.get_user_permissions = get_user_permissions

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        permissions = self.get_user_permissions()
        # Modify query based on user permissions
        return query

    async def process_result(self, result: Any) -> Any:
        # Filter result based on user permissions
        return result


class QueryOptimizationMiddleware(BaseMiddleware):
    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        # Analyze and optimize the query
        optimized_query = query  # Placeholder
        return optimized_query

    async def process_result(self, result: Any) -> Any:
        return result


class DistributedTracingMiddleware(BaseMiddleware):
    def __init__(self, tracer):
        self.tracer = tracer

    async def process_query(self, query: Dict[str, Any]) -> Dict[str, Any]:
        with self.tracer.start_span("database_query") as span:
            span.set_tag("query", str(query))
        return query

    async def process_result(self, result: Any) -> Any:
        return result


if __name__ == "__main__":
    # Usage example
    middleware_manager = MiddlewareManager()
    middleware_manager.add_middleware(QueryLoggingMiddleware())
    middleware_manager.add_middleware(CachingMiddleware())
    middleware_manager.add_middleware(SoftDeleteMiddleware())

    # In your query executor
    query = {"table": "users", "where": {"age": 30}}

    # Process the query
    processed_query = middleware_manager.process_query(query)  # Make sure to run this in an async context
    # Execute the processed query (not shown here)
