# database/orm/query/executor.py
from matrx_utils import vcprint
from matrx_utils.database.orm.core.async_db_manager import AsyncDatabaseManager
from matrx_utils.database.orm.exceptions import (
    DatabaseError,
    DoesNotExist,
    MultipleObjectsReturned,
    ValidationError,
    IntegrityError,
    QueryError,
)

debug = False


class QueryExecutor:
    def __init__(self, query):
        self.model = query["model"]
        self.database = query["database"]
        self.db = AsyncDatabaseManager()
        self._full_query_dict = query
        self.query, self.params = self._build_query()

    def _build_query(self):
        select_clause = ", ".join(self._full_query_dict["select"]) if self._full_query_dict["select"] else "*"
        sql = f"SELECT {select_clause} FROM {self._full_query_dict['table']}"
        params = []
        where_conditions = []

        # Handle filters
        filters = self._full_query_dict.get("filters", {})
        if filters:
            for key, value in filters.items():
                field_name = key
                if hasattr(self.model, "_meta"):
                    if key in self.model._meta.foreign_keys:
                        fk_ref = self.model._meta.foreign_keys[key]
                        field_name = fk_ref.field_name
                where_conditions.append(f"{field_name} = ${len(params) + 1}")
                params.append(value)

        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)

        if self._full_query_dict["order_by"]:
            order_by_terms = []
            for term in self._full_query_dict["order_by"]:
                if isinstance(term, str):
                    # Handle string-based ordering (e.g., "-version" or "version DESC")
                    if term.startswith("-"):
                        order_by_terms.append(f"{term[1:]} DESC")
                    else:
                        order_by_terms.append(f"{term} ASC")
                elif hasattr(term, "_order_direction"):
                    # Handle field object with desc() or asc()
                    field_name = term.name
                    if field_name is None:
                        # Infer field name from model's fields if not set
                        for fname, field in self.model._fields.items():
                            if field is term:  # Compare object identity
                                field_name = fname
                                break
                        if field_name is None:
                            raise ValueError(f"Field object used in order_by could not be matched to a model field: {term}")
                    direction = term._order_direction or "ASC"  # Default to ASC if not set
                    order_by_terms.append(f"{field_name} {direction}")
                else:
                    raise ValueError(f"Invalid order_by term: {term}")
            sql += " ORDER BY " + ", ".join(order_by_terms)

        if self._full_query_dict["limit"] is not None:
            sql += f" LIMIT ${len(params) + 1}"
            params.append(self._full_query_dict["limit"])

        if self._full_query_dict["offset"] is not None:
            sql += f" OFFSET ${len(params) + 1}"
            params.append(self._full_query_dict["offset"])

        if debug:
            vcprint(sql, "Built SQL", verbose=debug, color="cyan")
            vcprint(params, "With params", verbose=debug, color="cyan")

        return sql, params

    async def _execute(self):
        """Executes the built SQL query with proper error handling."""
        try:
            results = await self.db.execute_query(self.database, self.query, *self.params)
            return results
        except DatabaseError as e:
            raise DatabaseError(model=self.model, operation="execute", original_error=e)
        except Exception as e:
            raise QueryError(
                model=self.model,
                details={"query": self.query, "params": self.params, "error": str(e)},
            )

    async def insert(self, query):
        """Inserts a new row with proper error handling."""
        table = query["table"]
        data = query.get("data", {})

        if not data:
            raise ValidationError("No data provided for insert")

        columns = list(data.keys())
        values = list(data.values())
        placeholders = [f"${i + 1}" for i in range(len(values))]

        sql = f"INSERT INTO {table} ({', '.join(columns)}) " f"VALUES ({', '.join(placeholders)}) " f"RETURNING *"

        try:
            rows = await self.db.execute_query(self.database, sql, *values)
            if not rows:
                raise ValidationError("Insert succeeded but returned no data")
            return rows[0]
        except DatabaseError as e:
            if "unique constraint" in str(e).lower():
                raise IntegrityError(str(e))
            raise DatabaseError(str(e))

    async def bulk_insert(self, query):
        """Bulk inserts multiple rows into the database."""
        table = query["table"]
        data_list = query.get("data", [])

        if not data_list:
            return []

        if not isinstance(data_list, list):
            raise ValidationError(
                model=self.model,
                reason="Data must be a list of dictionaries",
                details={"provided_type": type(data_list).__name__},
            )

        try:
            columns = list(data_list[0].keys())
        except (IndexError, AttributeError) as e:
            raise ValidationError(
                model=self.model,
                reason="First item in data list is invalid",
                details={"error": str(e)},
            )

        all_values = []
        placeholders_list = []
        param_index = 1

        # Validate each row has the same columns
        for i, row_data in enumerate(data_list):
            if set(row_data.keys()) != set(columns):
                raise ValidationError(
                    model=self.model,
                    reason=f"Row {i} has different columns than first row",
                    details={
                        "expected_columns": columns,
                        "received_columns": list(row_data.keys()),
                    },
                )

            row_placeholders = []
            for col in columns:
                row_placeholders.append(f"${param_index}")
                all_values.append(row_data[col])
                param_index += 1
            placeholders_list.append(f"({', '.join(row_placeholders)})")

        sql = f"INSERT INTO {table} ({', '.join(columns)}) " f"VALUES {', '.join(placeholders_list)} " f"RETURNING *"

        try:
            results = await self.db.execute_query(self.database, sql, *all_values)
            return [self.model(**row) for row in results]
        except DatabaseError as e:
            if "unique constraint" in str(e).lower():
                raise IntegrityError(model=self.model, constraint="unique", original_error=e)
            raise DatabaseError(model=self.model, operation="bulk_insert", original_error=e)
        except Exception as e:
            raise QueryError(
                model=self.model,
                details={
                    "operation": "bulk_insert",
                    "row_count": len(data_list),
                    "error": str(e),
                },
            )

    async def update(self, **kwargs):
        """Updates rows in the database."""
        try:
            # Initial validation
            if not kwargs:
                raise ValidationError(model=self.model, reason="No update data provided")

            table = self._full_query_dict["table"]
            set_clause = []
            params = []

            # Process update data with field validation
            update_data = {}
            invalid_fields = []
            skipped_fields = []

            for k, v in kwargs.items():
                if k in self.model._fields:
                    field = self.model._fields[k]
                    if getattr(field, "is_native", True):
                        field_name = getattr(field, "field_name", k)
                        update_data[field_name] = v
                    else:
                        skipped_fields.append(k)
                        vcprint(f"Skipping non-native field: {k}", color="red")
                else:
                    invalid_fields.append(k)
                    vcprint(f"Field not found in model: {k}", color="red")

            # Raise validation error if there are invalid fields
            if invalid_fields:
                raise ValidationError(
                    model=self.model,
                    reason="Invalid fields in update data",
                    details={
                        "invalid_fields": invalid_fields,
                        "skipped_fields": skipped_fields,
                    },
                )

            # Build SET clause
            param_index = 1
            for field_name, value in update_data.items():
                set_clause.append(f"{field_name} = ${param_index}")
                params.append(value)
                param_index += 1

            if not set_clause:
                raise ValidationError(
                    model=self.model,
                    reason="No valid fields to update",
                    details={"skipped_fields": skipped_fields},
                )

            # Build WHERE clause
            base_query, where_params = self._build_query()
            where_clause = ""
            if "WHERE" in base_query:
                where_clause = base_query.split("WHERE", 1)[1].strip()
                where_clause = where_clause.split("ORDER BY")[0].strip() if "ORDER BY" in where_clause else where_clause
                # Update the parameter numbers in where clause
                for i in range(len(where_params)):
                    where_clause = where_clause.replace(f"${i + 1}", f"${param_index + i}")

            # Construct final SQL
            sql = f"UPDATE {table} SET {', '.join(set_clause)}"
            if where_clause:
                sql += f" WHERE {where_clause}"

            # Add where params to full params list
            params.extend(where_params)

            if debug:
                vcprint(sql, "Built SQL", verbose=debug, color="cyan")
                vcprint(params, "With params", verbose=debug, color="cyan")

            try:
                result = await self.db.execute_query(self.database, sql + " RETURNING *", *params)
                rows_affected = len(result)

                if rows_affected == 0:
                    vcprint("Update query details:", color="yellow")
                    vcprint(f"SQL: {sql}", color="yellow")
                    vcprint(f"Params: {params}", color="yellow")
                    vcprint(f"Result: {result}", color="yellow")

                # Return both the count and the updated data
                return {"rows_affected": rows_affected, "updated_rows": result}

            except DatabaseError as e:
                if "unique constraint" in str(e).lower():
                    raise IntegrityError(model=self.model, constraint="unique", original_error=e)
                elif "foreign key constraint" in str(e).lower():
                    raise IntegrityError(model=self.model, constraint="foreign_key", original_error=e)
                else:
                    raise DatabaseError(
                        model=self.model,
                        operation="update",
                        original_error=e,
                        details={"sql": sql, "params": params},
                    )

        except (ValidationError, IntegrityError, DatabaseError):
            # Re-raise these as they're already properly formatted
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise QueryError(
                model=self.model,
                details={
                    "operation": "update",
                    "error": str(e),
                    "sql": sql if "sql" in locals() else None,
                    "params": params if "params" in locals() else None,
                },
            )

    async def delete(self):
        """Deletes rows from the database."""
        table = self._full_query_dict["table"]
        base_query, where_params = self._build_query()
        where_clause = ""
        if "WHERE" in base_query:
            where_clause = base_query.split("WHERE", 1)[1].strip()
            where_clause = where_clause.split("ORDER BY")[0].strip() if "ORDER BY" in where_clause else where_clause
            # Update the parameter numbers in where clause
            for i in range(len(where_params)):
                where_clause = where_clause.replace(f"${i + 1}", f"${len(where_params) + i}")

        sql = f"DELETE FROM {table}"
        if where_clause:
            sql += f" WHERE {where_clause}"

        try:
            result = await self.db.execute_query(self.database, sql, *where_params)
            return len(result)
        except DatabaseError as e:
            raise DatabaseError(f"Delete failed: {str(e)}")

    async def all(self):
        """Returns all results with proper error handling."""
        results = await self._execute()
        if not results:
            return []
        return [self.model(**row) for row in results]

    async def first(self):
        """Returns first result with proper error handling."""
        self._full_query_dict["limit"] = 1
        results = await self._execute()
        if not results:
            return None
        return self.model(**results[0])

    async def count(self):
        """Executes a count query and returns the count."""
        base_query, params = self._build_query()
        table_name = self._full_query_dict["table"]

        where_clause = ""
        if "WHERE" in base_query:
            where_clause = base_query.split("WHERE", 1)[1].strip()
            where_clause = where_clause.split("ORDER BY")[0].strip() if "ORDER BY" in where_clause else where_clause

        count_sql = f"SELECT COUNT(*) as count FROM {table_name}"
        if where_clause:
            count_sql += f" WHERE {where_clause}"

        try:
            result = await self.db.execute_query(self.database, count_sql, *params)
            return result[0]["count"] if result else 0
        except DatabaseError as e:
            raise DatabaseError(f"Count query failed: {str(e)}")

    async def exists(self):
        """Checks if any result exists for the given query."""
        self._full_query_dict["limit"] = 1
        results = await self._execute()
        return len(results) > 0

    def __aiter__(self):
        self._iter_index = 0
        return self

    async def __anext__(self):
        if not self._results:
            await self._execute()
        if self._iter_index >= len(self._results):
            raise StopAsyncIteration
        row = self._results[self._iter_index]
        self._iter_index += 1
        return self.model(**row)
