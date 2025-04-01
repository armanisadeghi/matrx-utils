import os
import asyncio
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()


class AsyncSupabaseClient:
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.client = create_client(self.url, self.key)

    async def execute_sql(self, sql):
        response = await self.client.rpc('exec_sql', {
            'query': sql})
        return response

    async def create_table(self, table_name, columns):
        column_definitions = []
        primary_key = None

        for col in columns:
            col_def = f"{col['name']} {col['type']}"

            if col.get('nullable') == False:
                col_def += " NOT NULL"

            if col.get('unique'):
                col_def += " UNIQUE"

            if col.get('primary_key'):
                primary_key = col['name']

            if col.get('default') is not None:
                col_def += f" DEFAULT {col['default']}"

            column_definitions.append(col_def)

        if primary_key:
            column_definitions.append(f"PRIMARY KEY ({primary_key})")

        columns_sql = ", ".join(column_definitions)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql});"

        result = await self.execute_sql(create_table_sql)
        return result

    async def drop_table(self, table_name):
        drop_table_sql = f"DROP TABLE IF EXISTS {table_name};"
        result = await self.execute_sql(drop_table_sql)
        return result

    async def add_column(self, table_name, column):
        col_def = f"{column['name']} {column['type']}"
        if column.get('nullable') == False:
            col_def += " NOT NULL"
        if column.get('unique'):
            col_def += " UNIQUE"
        if column.get('default') is not None:
            col_def += f" DEFAULT {column['default']}"

        add_column_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_def};"
        result = await self.execute_sql(add_column_sql)
        return result

    async def list_tables(self):
        list_tables_sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        result = await self.execute_sql(list_tables_sql)
        return result


async def main():
    client = AsyncSupabaseClient()

    # Example: Create a new table
    new_table = "example_table"
    columns = [
        {
            "name": "id",
            "type": "serial",
            "primary_key": True},
        {
            "name": "name",
            "type": "varchar(100)",
            "nullable": False},
        {
            "name": "email",
            "type": "varchar(100)",
            "unique": True},
        {
            "name": "created_at",
            "type": "timestamp",
            "default": "CURRENT_TIMESTAMP"}
    ]

    print(f"Creating table '{new_table}'...")
    result = await client.create_table(new_table, columns)
    print(result)

    # List all tables
    print("\nListing all tables:")
    tables = await client.list_tables()
    print(tables)

    # Add a new column
    new_column = {
        "name": "description",
        "type": "text",
        "nullable": True
    }
    print(f"\nAdding new column 'description' to '{new_table}'...")
    result = await client.add_column(new_table, new_column)
    print(result)

    # Drop the table
    print(f"\nDropping table '{new_table}'...")
    result = await client.drop_table(new_table)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
