# database/orm/query/builder.py

from matrx_utils import vcprint
from matrx_utils.database.orm.error_handling import handle_orm_operation
from ..query.executor import QueryExecutor
from ..exceptions import (
    DatabaseError,
    DoesNotExist,
    MultipleObjectsReturned,
    QueryError,
    ValidationError,
)
from ...state import StateManager


class QueryBuilder:
    def __init__(self, model, database="supabase_automation_matrix"):
        self.model = model
        self.database = database
        self.filters = []
        self.excludes = []
        self.order_by_fields = []
        self.limit_val = None
        self.offset_val = None
        self.select_fields = []
        self.prefetch_fields = []
        self.joins = []
        self.group_by_fields = []
        self.having_filters = []
        self.aggregations = []

    def filter(self, **kwargs):
        """Applies SQL filters before execution."""
        if kwargs:
            self.filters.append(kwargs)
        return self

    def exclude(self, **kwargs):
        """Applies SQL exclusion filters before execution."""
        if kwargs:
            self.excludes.append(kwargs)
        return self

    def order_by(self, *fields):
        self.order_by_fields.extend(fields)
        return self

    def limit(self, value):
        self.limit_val = value
        return self

    def offset(self, value):
        self.offset_val = value
        return self

    def select(self, *fields):
        self.select_fields.extend(fields)
        return self

    def prefetch_related(self, *fields):
        self.prefetch_fields.extend(fields)
        return self

    def join(self, model, on, join_type="INNER"):
        self.joins.append({"model": model, "on": on, "type": join_type})
        return self

    def group_by(self, *fields):
        self.group_by_fields.extend(fields)
        return self

    def having(self, **kwargs):
        self.having_filters.append(kwargs)
        return self

    def annotate(self, **kwargs):
        for key, value in kwargs.items():
            self.aggregations.append({"name": key, "function": value})
        return self

    def _build_query(self):
        """Constructs the SQL query before execution."""
        query = {
            "model": self.model,
            "table": self.model._meta.table_name,
            "filters": self._merge_filters_excludes(),
            "order_by": self.order_by_fields,
            "limit": self.limit_val,
            "offset": self.offset_val,
            "select": self.select_fields or ["*"],
            "prefetch": self.prefetch_fields,
            "database": self.database,
        }
        return query

    def _merge_filters_excludes(self):
        """Merges filters and excludes for proper SQL conditions."""
        combined = {}
        for f in self.filters:
            combined.update(f)
        for e in self.excludes:
            for k, v in e.items():
                combined[f"exclude__{k}"] = v
        return combined

    def _get_executor(self):
        """Returns the QueryExecutor to execute the query."""
        return QueryExecutor(self._build_query())

    async def all(self):
        """Fetches all records matching the applied filters."""
        try:
            executor = self._get_executor()
            results = await executor.all()
            await StateManager.cache_bulk(self.model, results)
            vcprint(
                f"[BUILDER: QUERY_BUILDER] all method]🛢️  Cached {len(results)} records for {self.model.__name__}",
                color="bright_gold",
            )

            return results
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="all", original_error=e)
        except Exception as e:
            raise QueryError(model=self.model, details={"operation": "all", "error": str(e)})

    async def first(self):
        """Get the first matching record."""
        try:
            return await self._get_executor().first()
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="first", original_error=e)

    async def last(self):
        """Order by primary key descending and fetch the first record."""
        pk_name = getattr(self.model._meta, "pk_name", "id")
        self.order_by(f"-{pk_name}")
        return await self.first()

    async def get(self):
        """
        Retrieves exactly one object matching the criteria.
        """
        async with handle_orm_operation(
            "[BUILDER: QUERY_BUILDER] get method",
            model=self.model,
            filters=self._merge_filters_excludes(),
        ):
            executor = self._get_executor()
            results = await executor.all()
            vcprint(
                f"[BUILDER: QUERY_BUILDER] get method]🛢️  Returning {len(results)} results",
                color="bright_gold",
            )

            if not results:
                raise DoesNotExist(model=self.model, filters=self._merge_filters_excludes())

            if len(results) > 1:
                raise MultipleObjectsReturned(
                    model=self.model,
                    count=len(results),
                    filters=self._merge_filters_excludes(),
                )

            return results[0]

    async def get_or_none(self):
        """
        Execute the query and return None if no results found
        instead of raising DoesNotExist
        """
        try:
            return await self.get()
        except DoesNotExist:
            return None
        except Exception as e:
            vcprint(f"Error in QueryBuilder.get_or_none: {str(e)}", color="red")
            return None

    async def update(self, **kwargs):
        """Update matching records."""
        try:
            if not kwargs:
                raise ValidationError(model=self.model, reason="No update data provided")
            return await self._get_executor().update(**kwargs)
        except ValidationError:
            raise
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="update", original_error=e)

    async def delete(self):
        """Delete matching records."""
        try:
            return await self._get_executor().delete()
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="delete", original_error=e)

    async def count(self):
        """Count matching records."""
        try:
            return await self._get_executor().count()
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="count", original_error=e)

    async def exists(self):
        """Check if matching records exist."""
        try:
            return await self._get_executor().exists()
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="exists", original_error=e)

    async def values(self, *fields):
        exec_ = self._get_executor()
        if fields:
            exec_.select(*fields)
        return await exec_.values()

    async def values_list(self, *fields, flat=False):
        exec_ = self._get_executor()
        if fields:
            exec_.select(*fields)
        return await exec_.values_list(flat=flat)

    async def __aiter__(self):
        executor = self._get_executor()
        async for item in executor:
            yield item

    def __getitem__(self, k):
        if isinstance(k, slice):
            start = k.start or 0
            stop = k.stop if k.stop is not None else 0
            if stop > 0:
                self.limit(stop - start)
            self.offset(start)
            return self
        raise TypeError("Index access not supported, use slicing")
