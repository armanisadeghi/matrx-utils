from typing import Dict, Any, List, Union, Tuple
import asyncpg
from .base_adapter import BaseAdapter
from ..core.config import get_orm_config


class PostgreSQLAdapter(BaseAdapter):
    def __init__(self):
        self.config = get_orm_config().database
        self.connection = None

    async def _get_connection(self):
        if self.connection is None or self.connection.is_closed():
            self.connection = await asyncpg.connect(
                host=self.config.host,
                port=self.config.port,
                database=self.config.name,
                user=self.config.user,
                password=self.config.password
            )
        return self.connection

    async def execute_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        sql, params = self._build_sql(query)
        connection = await self._get_connection()
        rows = await connection.fetch(sql, *params)
        return [dict(row) for row in rows]

    async def count(self, query: Dict[str, Any]) -> int:
        sql, params = self._build_count_sql(query)
        connection = await self._get_connection()
        row = await connection.fetchrow(sql, *params)
        return row['count']

    async def exists(self, query: Dict[str, Any]) -> bool:
        sql, params = self._build_exists_sql(query)
        connection = await self._get_connection()
        row = await connection.fetchrow(sql, *params)
        return row['exists']

    async def insert(self, query: Dict[str, Any]) -> Dict[str, Any]:
        sql, params = self._build_insert_sql(query)
        connection = await self._get_connection()
        row = await connection.fetchrow(sql, *params)
        return dict(row)

    async def bulk_insert(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        sql, params = self._build_bulk_insert_sql(query)
        connection = await self._get_connection()
        await connection.executemany(sql, params)
        return await connection.fetch(sql, *params)

    async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        sql, params = self._build_update_sql(query, data)
        connection = await self._get_connection()
        result = await connection.execute(sql, *params)
        return result

    async def bulk_update(self, query: Dict[str, Any]) -> int:
        sql, params = self._build_bulk_update_sql(query)
        connection = await self._get_connection()
        result = await connection.executemany(sql, params)
        return result

    async def delete(self, query: Dict[str, Any]) -> int:
        sql, params = self._build_delete_sql(query)
        connection = await self._get_connection()
        result = await connection.execute(sql, *params)
        return result

    async def raw_sql(self, sql: str, params: List[Any] = None) -> Union[List[Dict[str, Any]], int]:
        connection = await self._get_connection()
        if sql.strip().upper().startswith("SELECT"):
            rows = await connection.fetch(sql, *params)
            return [dict(row) for row in rows]
        else:
            return await connection.execute(sql, *params)

    async def close(self):
        if self.connection is not None and not self.connection.is_closed():
            await self.connection.close()

    async def transaction(self):
        connection = await self._get_connection()
        async with connection.transaction():
            yield

    async def savepoint(self, name: str):
        connection = await self._get_connection()
        await connection.execute(f"SAVEPOINT {name}")

    async def rollback_to_savepoint(self, name: str):
        connection = await self._get_connection()
        await connection.execute(f"ROLLBACK TO SAVEPOINT {name}")

    async def release_savepoint(self, name: str):
        connection = await self._get_connection()
        await connection.execute(f"RELEASE SAVEPOINT {name}")

    def _build_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        # Generic SQL building logic for select statements
        sql = f"SELECT * FROM {query['model'].__tablename__} WHERE "
        filters = []
        params = []
        for field, value in query['filters'].items():
            filters.append(f"{field} = ${len(params) + 1}")
            params.append(value)
        sql += " AND ".join(filters)
        return sql, params

    def _build_count_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        sql = f"SELECT COUNT(*) FROM {query['model'].__tablename__} WHERE "
        filters = []
        params = []
        for field, value in query['filters'].items():
            filters.append(f"{field} = ${len(params) + 1}")
            params.append(value)
        sql += " AND ".join(filters)
        return sql, params

    def _build_exists_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        sql = f"SELECT EXISTS(SELECT 1 FROM {query['model'].__tablename__} WHERE "
        filters = []
        params = []
        for field, value in query['filters'].items():
            filters.append(f"{field} = ${len(params) + 1}")
            params.append(value)
        sql += " AND ".join(filters) + ")"
        return sql, params

    def _build_insert_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        fields = ", ".join(query['data'].keys())
        placeholders = ", ".join([f"${i + 1}" for i in range(len(query['data']))])
        sql = f"INSERT INTO {query['model'].__tablename__} ({fields}) VALUES ({placeholders}) RETURNING *"
        params = list(query['data'].values())
        return sql, params

    def _build_bulk_insert_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        fields = ", ".join(query['data'][0].keys())
        placeholders = ", ".join([f"${i + 1}" for i in range(len(query['data'][0]))])
        sql = f"INSERT INTO {query['model'].__tablename__} ({fields}) VALUES ({placeholders})"
        params = [tuple(row.values()) for row in query['data']]
        return sql, params

    def _build_update_sql(self, query: Dict[str, Any], data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        set_clause = ", ".join([f"{key} = ${i + 1}" for i, key in enumerate(data.keys())])
        sql = f"UPDATE {query['model'].__tablename__} SET {set_clause} WHERE "
        filters = []
        params = list(data.values())
        for field, value in query['filters'].items():
            filters.append(f"{field} = ${len(params) + 1}")
            params.append(value)
        sql += " AND ".join(filters)
        return sql, params

    def _build_bulk_update_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        # Similar to update but for bulk updates
        raise NotImplementedError("Bulk update logic to be implemented")

    def _build_delete_sql(self, query: Dict[str, Any]) -> Tuple[str, List[Any]]:
        sql = f"DELETE FROM {query['model'].__tablename__} WHERE "
        filters = []
        params = []
        for field, value in query['filters'].items():
            filters.append(f"{field} = ${len(params) + 1}")
            params.append(value)
        sql += " AND ".join(filters)
        return sql, params
