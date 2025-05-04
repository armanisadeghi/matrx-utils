# matrx_utils\database\orm\adapters\supabase.py
from typing import Dict, Any, List, Union, Optional
from database.orm.models import Recipe
from database.orm.adapters.base_adapter import BaseAdapter
from database.orm.core.config import get_orm_config
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_supabase_client():
    url = os.environ.get("SUPABASE_MATRIX_URL")
    key = os.environ.get("SUPABASE_MATRIX_KEY")
    supabase: Client = create_client(url, key)
    return supabase


class SupabaseAdapter(BaseAdapter):
    def __init__(self):
        self.client = get_supabase_client()
        self.config = get_orm_config().supabase

    async def fetch_by_id(self, model: Any, record_id: Union[str, int]) -> Optional[Dict[str, Any]]:
        table = self.client.table(model.__tablename__)
        response = await table.select("*").eq("id", record_id).single().execute()
        return response.data if response.data else None

    async def execute_query(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        table = self.client.table(query["model"].__tablename__)
        query_builder = self._apply_filters(table, query)
        response = await query_builder.execute()
        return response.data

    async def count(self, query: Dict[str, Any]) -> int:
        table = self.client.table(query["model"].__tablename__)
        query_builder = self._apply_filters(table, query)
        response = await query_builder.count().execute()
        return response.count

    async def exists(self, query: Dict[str, Any]) -> bool:
        return await self.count(query) > 0

    async def insert(self, query: Dict[str, Any]) -> Dict[str, Any]:
        table = self.client.table(query["model"].__tablename__)
        response = await table.insert(query["data"]).execute()
        return response.data[0]

    async def bulk_insert(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        table = self.client.table(query["model"].__tablename__)
        response = await table.insert(query["data"]).execute()
        return response.data

    async def update(self, query: Dict[str, Any], data: Dict[str, Any]) -> int:
        table = self.client.table(query["model"].__tablename__)
        query_builder = self._apply_filters(table, query)
        response = await query_builder.update(data).execute()
        return len(response.data)

    async def bulk_update(self, query: Dict[str, Any]) -> int:
        # Supabase doesn't support bulk update natively, so we'll do it one by one
        count = 0
        for obj in query["objects"]:
            count += await self.update(query["model"].__tablename__, {"id": obj.id}, obj.__dict__)
        return count

    async def delete(self, query: Dict[str, Any]) -> int:
        table = self.client.table(query["model"].__tablename__)
        query_builder = self._apply_filters(table, query)
        response = await query_builder.delete().execute()
        return len(response.data)

    async def raw_sql(self, sql: str, params: List[Any] = None) -> Union[List[Dict[str, Any]], int]:
        # Note: Supabase has limited support for raw SQL. This method might need to be adjusted based on specific use cases.
        response = await self.client.rpc("execute_sql", {"sql": sql, "params": params}).execute()
        return response.data

    async def transaction(self):
        # Note: Supabase doesn't support client-side transactions. This is a placeholder.
        return None

    def _apply_filters(self, table, query: Dict[str, Any]):
        query_builder = table
        for filter in query.get("filters", []):
            for key, value in filter.items():
                query_builder = query_builder.filter(key, "eq", value)
        for order in query.get("order_by", []):
            query_builder = query_builder.order(order.lstrip("-"), ascending=not order.startswith("-"))
        if query.get("limit"):
            query_builder = query_builder.limit(query["limit"])
        if query.get("offset"):
            query_builder = query_builder.offset(query["offset"])
        return query_builder


# Example usage
if __name__ == "__main__":
    import asyncio

    async def main():
        adapter = SupabaseAdapter()
        record_id = "e708eaf5-2c06-411f-9384-976ff85a6e24"  # Example ID
        recipe = await adapter.fetch_by_id(Recipe, record_id)
        if recipe:
            print(f"Fetched Recipe: {recipe}")
        else:
            print("No recipe found with that ID.")

    asyncio.run(main())
