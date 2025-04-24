import os
import importlib
import inspect
from datetime import datetime
from typing import List, Type, Union
from database.orm.core.config import get_database_config
from database.orm.core.base import Model
from database.orm.adapters.base_adapter import BaseAdapter
from database.orm.core.relations import ForeignKey


class Migration:
    def __init__(self, name: str, operations: List[dict]):
        self.name = name
        self.operations = operations

    def up(self, adapter: BaseAdapter):
        for operation in self.operations:
            getattr(self, f"_up_{operation['type']}")(adapter, **operation["params"])

    def down(self, adapter: BaseAdapter):
        for operation in reversed(self.operations):
            getattr(self, f"_down_{operation['type']}")(adapter, **operation["params"])

    def _up_create_table(self, adapter: BaseAdapter, table_name: str, fields: dict):
        adapter.execute_raw(f"CREATE TABLE {table_name} ({', '.join([f'{name} {spec}' for name, spec in fields.items()])})")

    def _down_create_table(self, adapter: BaseAdapter, table_name: str, fields: dict):
        adapter.execute_raw(f"DROP TABLE {table_name}")

    def _up_add_column(self, adapter: BaseAdapter, table_name: str, column_name: str, column_type: str):
        adapter.execute_raw(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

    def _down_add_column(self, adapter: BaseAdapter, table_name: str, column_name: str, column_type: str):
        adapter.execute_raw(f"ALTER TABLE {table_name} DROP COLUMN {column_name}")

    def _up_rename_column(self, adapter: BaseAdapter, table_name: str, old_name: str, new_name: str):
        adapter.execute_raw(f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}")

    def _down_rename_column(self, adapter: BaseAdapter, table_name: str, old_name: str, new_name: str):
        adapter.execute_raw(f"ALTER TABLE {table_name} RENAME COLUMN {new_name} TO {old_name}")

    def _up_alter_column(self, adapter: BaseAdapter, table_name: str, column_name: str, new_type: str):
        adapter.execute_raw(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {new_type}")

    def _down_alter_column(self, adapter: BaseAdapter, table_name: str, column_name: str, old_type: str):
        adapter.execute_raw(f"ALTER TABLE {table_name} ALTER COLUMN {column_name} TYPE {old_type}")

    def _up_add_index(
        self,
        adapter: BaseAdapter,
        table_name: str,
        column_names: List[str],
        index_name: str = None,
    ):
        index_name = index_name or f"idx_{table_name}_{'_'.join(column_names)}"
        adapter.execute_raw(f"CREATE INDEX {index_name} ON {table_name} ({', '.join(column_names)})")

    def _down_add_index(
        self,
        adapter: BaseAdapter,
        table_name: str,
        column_names: List[str],
        index_name: str = None,
    ):
        index_name = index_name or f"idx_{table_name}_{'_'.join(column_names)}"
        adapter.execute_raw(f"DROP INDEX {index_name}")

    def _up_add_foreign_key(
        self,
        adapter: BaseAdapter,
        table_name: str,
        column_name: str,
        reference_table: str,
        reference_column: str,
    ):
        adapter.execute_raw(f"ALTER TABLE {table_name} ADD CONSTRAINT fk_{table_name}_{column_name} FOREIGN KEY ({column_name}) REFERENCES {reference_table}({reference_column})")

    def _down_add_foreign_key(
        self,
        adapter: BaseAdapter,
        table_name: str,
        column_name: str,
        reference_table: str,
        reference_column: str,
    ):
        adapter.execute_raw(f"ALTER TABLE {table_name} DROP CONSTRAINT fk_{table_name}_{column_name}")


class MigrationManager:
    def __init__(self):
        self.config = get_database_config()
        self.adapter = self._get_adapter()
        self.migrations_dir = os.path.join(os.getcwd(), "migrations")
        self._ensure_migrations_table()

    def _get_adapter(self) -> BaseAdapter:
        if self.config.use_supabase:
            from ..adapters.supabase import SupabaseAdapter

            return SupabaseAdapter()
        from ..adapters.postgresql import PostgreSQLAdapter

        return PostgreSQLAdapter()

    def _ensure_migrations_table(self):
        self.adapter.execute_raw("""
            CREATE TABLE IF NOT EXISTS migrations (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    def create_migration(self, name: str):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{name}.py"
        filepath = os.path.join(self.migrations_dir, filename)

        with open(filepath, "w") as f:
            f.write(
                """from ..migrations.manager import Migration

class {0}(Migration):
    def __init__(self):
        super().__init__("{0}", [
            # Define your operations here
            # Example:
            # {{'type': 'create_table', 'params': {{'table_name': 'users', 'fields': {{'id': 'SERIAL PRIMARY KEY', 'name': 'VARCHAR(100)'}}}}}},
        ])

# Don't forget to define the 'down' operations for each 'up' operation
""".format(name.title().replace("_", ""))
            )

        print(f"Created migration: {filename}")

    def apply_migrations(self, target: Union[str, int] = None):
        applied_migrations = self._get_applied_migrations()
        available_migrations = self._get_available_migrations()

        to_apply = [m for m in available_migrations if m.name not in applied_migrations]
        if target:
            to_apply = [m for m in to_apply if m.name <= target] if isinstance(target, str) else to_apply[:target]

        for migration in to_apply:
            print(f"Applying migration: {migration.name}")
            migration.up(self.adapter)
            self.adapter.execute_raw("INSERT INTO migrations (name) VALUES (%s)", (migration.name,))

    def rollback_migrations(self, steps: int = 1):
        applied_migrations = self._get_applied_migrations()
        available_migrations = self._get_available_migrations()

        to_rollback = [m for m in reversed(available_migrations) if m.name in applied_migrations][:steps]

        for migration in to_rollback:
            print(f"Rolling back migration: {migration.name}")
            migration.down(self.adapter)
            self.adapter.execute_raw("DELETE FROM migrations WHERE name = %s", (migration.name,))

    def _get_applied_migrations(self) -> List[str]:
        result = self.adapter.execute_raw("SELECT name FROM migrations ORDER BY applied_at")
        return [row["name"] for row in result]

    def _get_available_migrations(self) -> List[Migration]:
        migrations = []
        for filename in sorted(os.listdir(self.migrations_dir)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module = importlib.import_module(f"migrations.{module_name}")
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, Migration) and obj != Migration:
                        migrations.append(obj())
        return migrations

    def generate_migration_from_models(self, models: List[Type[Model]]):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        migration_name = f"auto_generated_migration_{timestamp}"
        operations = []

        for model in models:
            table_name = model.__tablename__
            fields = {}
            for field_name, field in model._fields.items():
                fields[field_name] = field.db_type

            operations.append(
                {
                    "type": "create_table",
                    "params": {"table_name": table_name, "fields": fields},
                }
            )

            for field_name, field in model._fields.items():
                if isinstance(field, ForeignKey):
                    operations.append(
                        {
                            "type": "add_foreign_key",
                            "params": {
                                "table_name": table_name,
                                "column_name": field_name,
                                "reference_table": field.to_model.__tablename__,
                                "reference_column": "id",
                            },
                        }
                    )

        self.create_migration(migration_name)
        migration_file = os.path.join(self.migrations_dir, f"{timestamp}_{migration_name}.py")
        with open(migration_file, "r") as f:
            content = f.read()

        content = content.replace("# Define your operations here", f"operations = {operations}")

        with open(migration_file, "w") as f:
            f.write(content)

        print(f"Generated migration from models: {migration_name}")


# Usage
migration_manager = MigrationManager()

# Create a new migration
migration_manager.create_migration("add_users_table")

# Apply all pending migrations
migration_manager.apply_migrations()

# Rollback the last migration
migration_manager.rollback_migrations(1)

# # Generate migration from models
# from database.orm.core.fields import ForeignKey
# from myapp.models import User, Post

# migration_manager.generate_migration_from_models([User, Post])
