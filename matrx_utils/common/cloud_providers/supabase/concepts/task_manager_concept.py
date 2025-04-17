import asyncio

from common import pretty_print
from common.supabase.async_supabase_crud import AsyncSupabaseClient


class TaskManager:
    def __init__(self, client):
        self.client = client

    async def task3(self, *args, **kwargs):
        print("Executing task 3 as a method")
        # Example logic for task 3
        if self.client.initialized:
            data = kwargs.get('data', [])
            filtered_data = [x for x in data if x > args[0]]
            print(f"Filtered data for task 3: {filtered_data}")
        else:
            print("Supabase client not initialized.")

    async def task4(self, *args, **kwargs):
        print("Executing task 4 as a method")
        # Example logic for task 4
        if self.client.initialized:
            value = sum(args) + sum(kwargs.values())
            print(f"Total sum for task 4: {value}")
        else:
            print("Supabase client not initialized.")

    async def schema(self, *args, **kwargs):
        print("Executing schema task")
        if self.client.initialized:
            schema = await self.client.get_db_schema()
            pretty_print(schema)

            if table := kwargs.get('table'):
                specific_table = schema.get(table)
                pretty_print(specific_table)
                return specific_table
            else:
                return schema
        else:
            print("Supabase client not initialized.")
            return None





async def task1(client, *args, **kwargs):
    print("Executing task 1 as a function")
    # Example logic for task 1
    if client.initialized:
        result = args[0] + kwargs.get('increment', 0)
        print(f"Result for task 1: {result}")
    else:
        print("Supabase client not initialized.")

async def task2(client, *args, **kwargs):
    print("Executing task 2 as a function")
    # Example logic for task 2
    if client.initialized:
        for i in range(kwargs.get('repeat', 1)):
            print(f"Task 2, iteration {i + 1}: {args}")
    else:
        print("Supabase client not initialized.")

async def fetch_recipes():
    client = AsyncSupabaseClient()
    if not client.initialized:
        print("Failed to initialize Supabase client.")
        return

    try:
        # Fetch all recipes from the 'recipe' table
        recipes = await client.select(table='recipe')
        print("Recipes:", recipes)
    except Exception as e:
        print(f"An error occurred: {e}")

def main(task, *args, **kwargs):
    client = AsyncSupabaseClient()
    task_manager = TaskManager(client)

    # Define a dictionary to map task names to functions/methods
    tasks = {
        "schema": lambda: task_manager.schema(*args, **kwargs),
        "fetch_recipes": fetch_recipes,
        "task1": lambda: task1(client, *args, **kwargs),
        "task2": lambda: task2(client, *args, **kwargs),
        "task3": lambda: task_manager.task3(*args, **kwargs),
        "task4": lambda: task_manager.task4(*args, **kwargs),
        # Add more tasks here as needed
    }

    if task not in tasks:
        print(f"Task '{task}' not recognized. Available tasks: {list(tasks.keys())}")
        return None

    try:
        # Run the selected task asynchronously
        asyncio.run(tasks[task]())
    except Exception as e:
        print(f"An error occurred while executing the task '{task}': {e}")





if __name__ == "__main__":
    main(task="fetch_recipes")





















'''
main("task2", "Hello", repeat=3)  # Example call for task2
main("task3", 5, data=[1, 6, 3, 8])  # Example call for task3
main("task4", 1, 2, 3, multiplier=2)  # Example call for task4
'''
