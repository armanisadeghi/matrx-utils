import json
import os
import asyncio
from dotenv import load_dotenv
from functools import wraps
import inspect

from common import pretty_print
from common.supabase.supabase_client import get_supabase_client
import os
from supabase import create_client, Client

load_dotenv()


def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(func(*args, **kwargs))

    return wrapper


class SyncSupabaseClient:
    def __init__(self):
        self.async_client = AsyncSupabaseClient()
        self._create_sync_methods()

    def _create_sync_methods(self):
        for name, method in inspect.getmembers(self.async_client, inspect.iscoroutinefunction):
            setattr(self, name, self._create_sync_method(name, method))

    def _create_sync_method(self, name, async_method):
        @run_async
        def sync_method(*args, **kwargs):
            result = async_method(*args, **kwargs)
            if hasattr(result, 'dict'):
                return result.dict()
            elif hasattr(result, 'model_dump'):
                return result.model_dump()
            else:
                return result

        return sync_method


class AsyncSupabaseClient:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_MATRIX_URL")
        key: str = os.environ.get("SUPABASE_MATRIX_KEY")
        supabase: Client = create_client(url, key)

        self.client = supabase
        if self.client:
            print("Supabase client initialized")
            self.initialized = True

    def get_schema(self):
        schema = self.client.rpc("get_database_schema_json").execute()
        return schema

    def select(self, table, columns="*", filters=None, order=None, limit=None, offset=None):
        query = self.client.table(table).select(columns)
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        if order:
            query = query.order(order)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        response = query.execute()
        return response.data

    def insert(self, table, data):
        response = self.client.table(table).insert(data).execute()
        return response.data[0] if response.data else {}

    def update(self, table, data, filters):
        query = self.client.table(table).update(data)
        for key, value in filters.items():
            query = query.eq(key, value)
        response = query.execute()
        return response.data[0] if response.data else {}

    def delete(self, table, filters):
        query = self.client.table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        response = query.execute()
        return response.data

    def upsert(self, table, data, unique_columns):
        response = self.client.table(table).upsert(data, on_conflict=",".join(unique_columns)).execute()
        return response.data[0] if response.data else {}

    def count(self, table, filters=None):
        query = self.client.table(table).select("*", count="exact")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.count

    def select_single(self, table, columns="*", filters=None):
        query = self.client.table(table).select(columns).limit(1)
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.data[0] if response.data else None

    def bulk_insert(self, table, data_list):
        response = self.client.table(table).insert(data_list).execute()
        return response.data

    def select_in(self, table, column, values, additional_filters=None):
        query = self.client.table(table).select("*").in_(column, values)
        if additional_filters:
            for key, value in additional_filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.data

    def select_range(self, table, column, start, end, additional_filters=None):
        query = self.client.table(table).select("*").gte(column, start).lte(column, end)
        if additional_filters:
            for key, value in additional_filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.data

    # Method to execute a stored procedure
    def execute_sql(self, function_name, params=None):
        """
        Executes a stored procedure on the Supabase database.

        :param function_name: The name of the stored procedure to execute.
        :param params: A dictionary of parameters to pass to the procedure.
        :return: The result of the stored procedure execution.
        """
        if params is None:
            params = {}
        response = self.client.rpc(function_name, params).execute()
        return response.data

    # Existing methods for select, insert, update, delete, etc.

    # Example usage
    def create_broker(self, params):
        """
        Calls the add_one_broker stored procedure with the given parameters.

        :param params: A dictionary of parameters required by the stored procedure.
        :return: The result of the procedure.
        """
        return self.execute_sql('add_one_broker', params)

    def get_db_schema(self):
        schema = {"matrix_schema": {"table_names": {}, "tables": []}}

        # Get all tables
        tables_response = self.client.table("information_schema.tables").select("table_name").eq("table_schema", "public").execute()
        tables = [table['table_name'] for table in tables_response.data]

        for table_name in tables:
            # Get columns for the table
            columns_response = self.client.table("information_schema.columns").select("*").eq("table_name", table_name).eq("table_schema", "public").execute()
            columns = columns_response.data

            # Get primary key for the table
            pk_response = self.client.table("information_schema.key_column_usage").select("column_name").eq("table_name", table_name).eq("constraint_name", f"{table_name}_pkey").execute()
            primary_key = pk_response.data[0]['column_name'] if pk_response.data else None

            # Get foreign keys for the table
            fk_to_response = self.client.table("information_schema.key_column_usage").select("*").eq("table_name", table_name).neq("constraint_name", f"{table_name}_pkey").execute()
            fk_from_response = self.client.table("information_schema.key_column_usage").select("*").eq("referenced_table_name", table_name).execute()

            # Build table schema
            table_schema = {
                "table_name": table_name,
                "primary_key": primary_key,
                "schema": [],
                "inbound_foreign_keys": fk_to_response.data,
                "outbound_foreign_keys": fk_from_response.data
            }

            column_names = []
            for column in columns:
                column_schema = {
                    "column_name": column['column_name'],
                    "data_type": column['data_type'],
                    "is_nullable": column['is_nullable'],
                    "column_default": column['column_default'],
                    "is_primary_key": (column['column_name'] == primary_key)
                }
                table_schema["schema"].append(column_schema)
                column_names.append(column['column_name'])

            schema["matrix_schema"]["table_names"][table_name] = {
                "columns": column_names,
                "primary_key": primary_key
            }
            schema["matrix_schema"]["tables"].append(table_schema)

        return schema





def sample_function():
    supabase = AsyncSupabaseClient()

    # Example usage
    print("Selecting all rows from 'broker' table:")
    rows = supabase.select('broker')
    print(rows)

    print("\nInserting a new row into 'broker' table:")
    new_row = supabase.insert('broker', {
        'display_name': 'Test Broker',
        'data_type': 'str',
        'description': 'A test broker entry'
    })
    print(new_row)

    print("\nUpdating the row we just inserted:")
    updated_row = supabase.update('broker', {
        'description': 'Updated test broker entry'}, {
                                            'id': new_row['id']})
    print(updated_row)

    print("\nSelecting the updated row:")
    updated_rows = supabase.select('broker', filters={
        'id': new_row['id']})
    print(updated_rows)

    print("\nCounting rows in 'broker' table:")
    count = supabase.count('broker')
    print(f"Total rows: {count}")

    print("\nSelecting a single row:")
    single_row = supabase.select_single('broker', filters={
        'id': new_row['id']})
    print(single_row)

    print("\nBulk inserting rows:")
    bulk_rows = supabase.bulk_insert('broker', [
        {
            'display_name': 'Bulk Test 1',
            'data_type': 'str',
            'description': 'Bulk insert test 1'},
        {
            'display_name': 'Bulk Test 2',
            'data_type': 'str',
            'description': 'Bulk insert test 2'}
    ])
    print(bulk_rows)

    print("\nSelecting rows with IN clause:")
    in_rows = supabase.select_in('broker', 'display_name', ['Bulk Test 1', 'Bulk Test 2'])
    print(in_rows)

    print("\nSelecting rows within a range:")
    range_rows = supabase.select_range('broker', 'id', new_row['id'], new_row['id'] + 2)
    print(range_rows)

    print("\nDeleting the rows we inserted:")
    deleted_rows = supabase.delete('broker', {
        'id': new_row['id']})


def fetch_all_recipes():
    # Initialize the AsyncSupabaseClient
    client = AsyncSupabaseClient()

    # Check if the client was initialized successfully
    if not client.initialized:
        print("Supabase client not initialized.")
        return None

    # Use the select method to fetch all entries from the 'recipes' table
    try:
        # Call the select method without any filters, to get all entries
        recipes = client.select(table="recipes", columns="*")
        return recipes
    except Exception as e:
        print(f"An error occurred while fetching recipes: {e}")
        return None


def direct_tasks(task, *args, **kwargs):
    client = AsyncSupabaseClient()

    if task == "task1":
        # Logic for task 1
        print("Executing task 1")
        # Add your specific logic here for task 1
        # Use args and kwargs as needed
        result = args[0] + kwargs.get('increment', 0)
        print(f"Result for task 1: {result}")

    elif task == "task2":
        # Logic for task 2
        print("Executing task 2")
        # Add your specific logic here for task 2
        # Use args and kwargs as needed
        for i in range(kwargs.get('repeat', 1)):
            print(f"Task 2, iteration {i + 1}: {args}")

    elif task == "task3":
        # Logic for task 3
        print("Executing task 3")
        # Add your specific logic here for task 3
        data = kwargs.get('data', [])
        print(f"Data received: {data}")
        filtered_data = [x for x in data if x > args[0]]
        print(f"Filtered data: {filtered_data}")

    elif task == "task4":
        # Logic for task 4
        print("Executing task 4")
        # Add your specific logic here for task 4
        value = sum(args) + sum(kwargs.values())
        print(f"Total sum for task 4: {value}")

    elif task == "task5":
        # Logic for task 5
        print("Executing task 5")
        # Add your specific logic here for task 5
        if 'key' in kwargs:
            print(f"Task 5 received key: {kwargs['key']}")

    elif task == "task6":
        # Logic for task 6
        print("Executing task 6")
        # Add your specific logic here for task 6
        print(f"Arguments: {args}, Keyword Arguments: {kwargs}")

    elif task == "task7":
        # Logic for task 7
        print("Executing task 7")
        # Add your specific logic here for task 7
        print("Performing task 7 operations...")

    elif task == "task8":
        # Logic for task 8
        print("Executing task 8")
        # Add your specific logic here for task 8
        count = kwargs.get('count', 0)
        for _ in range(count):
            print("Task 8 loop")

    elif task == "task9":
        # Logic for task 9
        print("Executing task 9")
        # Add your specific logic here for task 9
        if args:
            print(f"Task 9 received arguments: {args}")

    elif task == "task10":
        # Logic for task 10
        print("Executing task 10")
        # Add your specific logic here for task 10
        config = kwargs.get('config', {})
        print(f"Configuration: {config}")

    else:
        print(f"Task '{task}' not recognized. Available tasks: task1 to task10")

def main(task, *args, **kwargs):
    client = AsyncSupabaseClient()

    tasks = {
        "task1": lambda *args, **kwargs: print("Executing task 1", args, kwargs),
        "task2": lambda *args, **kwargs: print("Executing task 2", args, kwargs),
        "task3": lambda *args, **kwargs: print("Executing task 3", args, kwargs),
        "task4": lambda *args, **kwargs: print("Executing task 4", args, kwargs),
        "task5": lambda *args, **kwargs: print("Executing task 5", args, kwargs),
        "task6": lambda *args, **kwargs: print("Executing task 6", args, kwargs),
        "task7": lambda *args, **kwargs: print("Executing task 7", args, kwargs),
        "task8": lambda *args, **kwargs: print("Executing task 8", args, kwargs),
        "task9": lambda *args, **kwargs: print("Executing task 9", args, kwargs),
        "task10": lambda *args, **kwargs: print("Executing task 10", args, kwargs),
    }

    if task not in tasks:
        print(f"Task '{task}' not recognized. Available tasks: {list(tasks.keys())}")
        return None

    try:
        tasks[task](*args, **kwargs)
    except Exception as e:
        print(f"An error occurred while executing the task '{task}': {e}")



if __name__ == "__main__":

    main("task1", 42, key="value")

    db = AsyncSupabaseClient()
    schema = db.get_schema()
    pretty_print(schema)




































