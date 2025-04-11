import os
import json
from typing import List, Dict, Any, Type, TypeVar
import requests
import psycopg2
from psycopg2.extras import RealDictCursor

T = TypeVar("T", bound="Model")


class SupabaseConfig:
    def __init__(self, url: str, key: str, is_local: bool = False):
        self.url = url
        self.key = key
        self.is_local = is_local


class Field:
    def __init__(self, field_type: str, nullable: bool = True):
        self.field_type = field_type
        self.nullable = nullable


class Model:
    _config: SupabaseConfig = None

    @classmethod
    def set_config(cls, config: SupabaseConfig):
        cls._config = config

    @classmethod
    def table_name(cls) -> str:
        return cls.__name__.lower()

    @classmethod
    def fields(cls) -> Dict[str, Field]:
        return {name: value for name, value in cls.__dict__.items() if isinstance(value, Field)}

    @classmethod
    def create_table(cls):
        if not cls._config.is_local:
            raise Exception("Create table is only available for local instances")

        columns = [f"{name} {field.field_type} {'NOT NULL' if not field.nullable else ''}" for name, field in cls.fields().items()]
        query = f"CREATE TABLE IF NOT EXISTS {cls.table_name()} ({', '.join(columns)})"

        with psycopg2.connect(cls._config.url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()

    @classmethod
    def select(cls: Type[T], *fields) -> List[T]:
        field_names = [f for f in fields] if fields else ["*"]
        if cls._config.is_local:
            with psycopg2.connect(cls._config.url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(f"SELECT {', '.join(field_names)} FROM {cls.table_name()}")
                    return [cls(**row) for row in cur.fetchall()]
        else:
            response = requests.get(
                f"{cls._config.url}/rest/v1/{cls.table_name()}?select={','.join(field_names)}",
                headers={"apikey": cls._config.key},
            )
            return [cls(**item) for item in response.json()]

    def insert(self):
        data = {name: getattr(self, name) for name in self.fields()}
        if self._config.is_local:
            placeholders = ", ".join(["%s"] * len(data))
            columns = ", ".join(data.keys())
            query = f"INSERT INTO {self.table_name()} ({columns}) VALUES ({placeholders})"
            with psycopg2.connect(self._config.url) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, list(data.values()))
                conn.commit()
        else:
            response = requests.post(
                f"{self._config.url}/rest/v1/{self.table_name()}",
                headers={
                    "apikey": self._config.key,
                    "Content-Type": "application/json",
                },
                data=json.dumps(data),
            )
            response.raise_for_status()


# Example usage
class User(Model):
    id = Field("serial primary key")
    name = Field("text", nullable=False)
    email = Field("text", nullable=False)


# Configure for local or cloud usage
if os.environ.get("USE_LOCAL_DB"):
    User.set_config(SupabaseConfig("postgresql://localhost/testdb", "local_key", is_local=True))
    User.create_table()
else:
    User.set_config(SupabaseConfig("https://your-project.supabase.co", "your-supabase-key"))

# Create a new user
new_user = User(name="John Doe", email="john@example.com")
new_user.insert()

# Select all users
users = User.select()
for user in users:
    print(f"User: {user.name}, Email: {user.email}")
