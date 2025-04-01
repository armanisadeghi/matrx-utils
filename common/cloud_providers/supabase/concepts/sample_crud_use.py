import asyncio
from common.supabase.async_supabase_crud import AsyncSupabaseClient

from common import vcprint

verbose = True


class RecipeDatabaseClient(AsyncSupabaseClient):
    def __init__(self):
        super().__init__()
        if self.initialized:
            print("[RECIPE DATABASE] initialized...")

    async def get_matrix_schema(self):
        schema = await self.get_schema()
        vcprint(verbose=verbose, pretty=True, data=schema, title="Database Schema", color="blue")
        return schema

    async def select_all_recipes(self):
        all_recipes = self.client.rpc("fetch_all_recipe").execute()
        vcprint(verbose=verbose, pretty=True, data=all_recipes, title="All Recipes", color="blue")
        return all_recipes


async def main():
    supabase = RecipeDatabaseClient()

    schema = await supabase.get_matrix_schema()
    # all_recipes = await supabase.select_all_recipes()

    return schema


if __name__ == "__main__":
    schema = asyncio.run(main())

#
# async def main():
#     supabase = AsyncSupabaseClient()
#
#     # Example usage
#     print("Selecting all rows from 'broker' table:")
#     rows = await supabase.select('broker')
#     print(rows)
#
#     print("\nInserting a new row into 'broker' table:")
#     new_row = await supabase.insert('broker', {
#         'display_name': 'Test Broker',
#         'data_type': 'str',
#         'description': 'A test broker entry'
#     })
#     print(new_row)
#
#     print("\nUpdating the row we just inserted:")
#     updated_row = await supabase.update('broker', {'description': 'Updated test broker entry'}, {'id': new_row['id']})
#     print(updated_row)
#
#     print("\nSelecting the updated row:")
#     updated_rows = await supabase.select('broker', filters={'id': new_row['id']})
#     print(updated_rows)
#
#     print("\nCounting rows in 'broker' table:")
#     count = await supabase.count('broker')
#     print(f"Total rows: {count}")
#
#     print("\nSelecting a single row:")
#     single_row = await supabase.select_single('broker', filters={'id': new_row['id']})
#     print(single_row)
#
#     print("\nBulk inserting rows:")
#     bulk_rows = await supabase.bulk_insert('broker', [
#         {'display_name': 'Bulk Test 1', 'data_type': 'str', 'description': 'Bulk insert test 1'},
#         {'display_name': 'Bulk Test 2', 'data_type': 'str', 'description': 'Bulk insert test 2'}
#     ])
#     print(bulk_rows)
#
#     print("\nSelecting rows with IN clause:")
#     in_rows = await supabase.select_in('broker', 'display_name', ['Bulk Test 1', 'Bulk Test 2'])
#     print(in_rows)
#
#     print("\nSelecting rows within a range:")
#     range_rows = await supabase.select_range('broker', 'id', new_row['id'], new_row['id'] + 2)
#     print(range_rows)
#
#     print("\nDeleting the rows we inserted:")
#     deleted_rows = await supabase.delete('broker', {'id': new_row['id']})
#     print(deleted_rows)
#
#     print("\nUpserting a row (insert or update):")
#     upserted_row = await supabase.upsert('broker', {
#         'id': '12345',
#         'display_name': 'Upsert Test',
#         'data_type': 'str',
#         'description': 'Testing upsert functionality'
#     }, ['id'])
#     print(upserted_row)
#
#
#     async def select_recipe_by_id(self, recipe_id):
#         print(f"\nSelecting recipe by ID: {recipe_id}")
#         rows = await self.supabase.execute(
#             "SELECT * FROM public.fetch_by_id_recipe(%s)", (recipe_id,)
#         )
#         print(rows)
#         return rows
#
#     async def add_recipe(self, p_id, p_name, p_status, p_varsion=None):
#         print(f"\nAdding a new recipe with ID: {p_id}")
#         rows = await self.supabase.execute(
#             "SELECT * FROM public.add_one_recipe(%s, %s, %s, %s)",
#             (p_id, p_name, p_status, p_varsion),
#         )
#         print(rows)
#         return rows
#
#     async def upsert_recipe(
#         self,
#         p_id,
#         p_name,
#         p_status,
#         p_varsion=None,
#         p_description="",
#         p_tags=None,
#         p_sample_output="",
#         p_is_public=None,
#         p_messages=None,
#         p_post_result_options=None,
#     ):
#         print(f"\nUpserting recipe with ID: {p_id}")
#         rows = await self.supabase.execute(
#             """
#             SELECT public.upsert_recipe(
#                 %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
#             )
#             """,
#             (
#                 p_id,
#                 p_name,
#                 p_status,
#                 p_varsion,
#                 p_description,
#                 p_tags,
#                 p_sample_output,
#                 p_is_public,
#                 p_messages,
#                 p_post_result_options,
#             ),
#         )
#         print(rows)
#         return rows
#
#     async def delete_recipe(self, recipe_id):
#         print(f"\nDeleting recipe with ID: {recipe_id}")
#         rows = await self.supabase.execute(
#             "SELECT public.delete_one('recipe', %s)", (recipe_id,)
#         )
#         print(rows)
#         return rows
#
#     async def update_recipe(self, recipe_id, update_data):
#         print(f"\nUpdating recipe with ID: {recipe_id}")
#         rows = await self.supabase.execute(
#             "SELECT public.update_one('recipe', %s, %s::jsonb)",
#             (recipe_id, update_data),
#         )
#         print(rows)
#         return rows
#
#     async def fetch_paginated(self, table_name, page, page_size):
#         print(f"\nFetching paginated data from {table_name}")
#         rows = await self.supabase.execute(
#             "SELECT * FROM public.fetch_paginated(%s, %s, %s)",
#             (table_name, page, page_size),
#         )
#         print(rows)
#         return rows
#
#     async def fetch_filtered(self, table_name, filters):
#         print(f"\nFetching filtered data from {table_name}")
#         rows = await self.supabase.execute(
#             "SELECT * FROM public.fetch_filtered(%s, %s::jsonb)", (table_name, filters)
#         )
#         print(rows)
#         return rows
#
#     async def fetch_with_children(self, table_name, record_id):
#         print(f"\nFetching {table_name} with children for ID: {record_id}")
#         rows = await self.supabase.execute(
#             "SELECT public.fetch_with_children(%s, %s)", (table_name, record_id)
#         )
#         print(rows)
#         return rows
#
#     async def fetch_all_with_children(self, table_name):
#         print(f"\nFetching all {table_name} with children")
#         rows = await self.supabase.execute(
#             "SELECT public.fetch_all_with_children(%s)", (table_name,)
#         )
#         print(rows)
#         return rows
#
#
# async def main():
#     client = RecipeDatabaseClient()
#     recipe_id = 'a0c28430-d8b0-465a-8c20-139c830c3e95'
#     # Add all variables here
#
#
#     await client.select_all_recipes()
#     await client.select_recipe_by_id(recipe_id)  # Use them like this
#     await client.add_recipe('a0c28430-d8b0-465a-8c20-139c830c3e95', 'Samplename0344', 'active_testing')
#     await client.upsert_recipe(
#         'a0c28430-d8b0-465a-8c20-139c830c3e95',
#         'Samplename0344',
#         'active_testing',
#         p_description='NonReqdescription0344',
#         p_tags='{"zeta": "zeta0344"}'::jsonb,
#         p_sample_output='NonReqsample_output0344',
#         p_messages='{"zeta": "zeta0344"}'::jsonb,
#         p_post_result_options='{"zeta": "zeta0344"}'::jsonb,
#     )
#     await client.delete_recipe('a0c28430-d8b0-465a-8c20-139c830c3e95')
#     await client.update_recipe('a0c28430-d8b0-465a-8c20-139c830c3e95', '{"name": "Updated Name", "type": "partial_page"}')
#     await client.fetch_paginated('recipe', 1, 3)
#     await client.fetch_filtered('recipe', '{"type": "full_page"}'::jsonb)
#     await client.fetch_with_children('recipe', 'a0c28430-d8b0-465a-8c20-139c830c3e95')
#     await client.fetch_all_with_children('recipe')
#
#
#
