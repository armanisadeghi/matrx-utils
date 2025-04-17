import os
import json
from typing import List, Dict, Any, Type, TypeVar, Optional
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
    def __init__(self, field_type: str, nullable: bool = True, primary_key: bool = False):
        self.field_type = field_type
        self.nullable = nullable
        self.primary_key = primary_key


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
    def primary_key(cls) -> str:
        for name, field in cls.fields().items():
            if field.primary_key:
                return name
        raise ValueError(f"No primary key defined for {cls.__name__}")

    @classmethod
    def create_table(cls):
        if not cls._config.is_local:
            raise Exception("Create table is only available for local instances")

        columns = [f"{name} {field.field_type} {'NOT NULL' if not field.nullable else ''} {'PRIMARY KEY' if field.primary_key else ''}" for name, field in cls.fields().items()]
        query = f"CREATE TABLE IF NOT EXISTS {cls.table_name()} ({', '.join(columns)})"

        with psycopg2.connect(cls._config.url) as conn:
            with conn.cursor() as cur:
                cur.execute(query)
            conn.commit()

    @classmethod
    def create(cls: Type[T], **kwargs) -> T:
        instance = cls(**kwargs)
        instance.save()
        return instance

    @classmethod
    def get(cls: Type[T], id: Any) -> Optional[T]:
        primary_key = cls.primary_key()
        if cls._config.is_local:
            with psycopg2.connect(cls._config.url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        f"SELECT * FROM {cls.table_name()} WHERE {primary_key} = %s",
                        (id,),
                    )
                    result = cur.fetchone()
                    return cls(**result) if result else None
        else:
            response = requests.get(
                f"{cls._config.url}/rest/v1/{cls.table_name()}?{primary_key}=eq.{id}",
                headers={"apikey": cls._config.key},
            )
            results = response.json()
            return cls(**results[0]) if results else None

    @classmethod
    def filter(cls: Type[T], **kwargs) -> List[T]:
        conditions = [f"{k}=eq.{v}" for k, v in kwargs.items()]
        if cls._config.is_local:
            with psycopg2.connect(cls._config.url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    query = f"SELECT * FROM {cls.table_name()} WHERE {' AND '.join([f'{k} = %s' for k in kwargs.keys()])}"
                    cur.execute(query, tuple(kwargs.values()))
                    return [cls(**row) for row in cur.fetchall()]
        else:
            response = requests.get(
                f"{cls._config.url}/rest/v1/{cls.table_name()}?{'&'.join(conditions)}",
                headers={"apikey": cls._config.key},
            )
            return [cls(**item) for item in response.json()]

    @classmethod
    def all(cls: Type[T]) -> List[T]:
        if cls._config.is_local:
            with psycopg2.connect(cls._config.url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(f"SELECT * FROM {cls.table_name()}")
                    return [cls(**row) for row in cur.fetchall()]
        else:
            response = requests.get(
                f"{cls._config.url}/rest/v1/{cls.table_name()}",
                headers={"apikey": cls._config.key},
            )
            return [cls(**item) for item in response.json()]

    def save(self):
        data = {name: getattr(self, name) for name in self.fields() if hasattr(self, name)}
        primary_key = self.__class__.primary_key()

        if hasattr(self, primary_key) and getattr(self, primary_key) is not None:
            # Update
            if self._config.is_local:
                set_clause = ", ".join([f"{k} = %s" for k in data.keys() if k != primary_key])
                query = f"UPDATE {self.table_name()} SET {set_clause} WHERE {primary_key} = %s"
                values = list(data[k] for k in data.keys() if k != primary_key) + [data[primary_key]]
                with psycopg2.connect(self._config.url) as conn:
                    with conn.cursor() as cur:
                        cur.execute(query, values)
                    conn.commit()
            else:
                response = requests.patch(
                    f"{self._config.url}/rest/v1/{self.table_name()}?{primary_key}=eq.{getattr(self, primary_key)}",
                    headers={
                        "apikey": self._config.key,
                        "Content-Type": "application/json",
                    },
                    data=json.dumps(data),
                )
                response.raise_for_status()
        else:
            # Insert
            if self._config.is_local:
                placeholders = ", ".join(["%s"] * len(data))
                columns = ", ".join(data.keys())
                query = f"INSERT INTO {self.table_name()} ({columns}) VALUES ({placeholders}) RETURNING *"
                with psycopg2.connect(self._config.url) as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute(query, list(data.values()))
                        result = cur.fetchone()
                    conn.commit()
                for key, value in result.items():
                    setattr(self, key, value)
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
                result = response.json()
                for key, value in result.items():
                    setattr(self, key, value)

    def delete(self):
        primary_key = self.__class__.primary_key()
        if not hasattr(self, primary_key):
            raise ValueError("Cannot delete unsaved object")

        if self._config.is_local:
            query = f"DELETE FROM {self.table_name()} WHERE {primary_key} = %s"
            with psycopg2.connect(self._config.url) as conn:
                with conn.cursor() as cur:
                    cur.execute(query, (getattr(self, primary_key),))
                conn.commit()
        else:
            response = requests.delete(
                f"{self._config.url}/rest/v1/{self.table_name()}?{primary_key}=eq.{getattr(self, primary_key)}",
                headers={"apikey": self._config.key},
            )
            response.raise_for_status()


class User(Model):
    id = Field("serial", primary_key=True)
    name = Field("text", nullable=False)
    email = Field("text", nullable=False)


if __name__ == "__main__":
    # Configure for local or cloud usage
    if os.environ.get("USE_LOCAL_DB"):
        User.set_config(SupabaseConfig("postgresql://localhost/testdb", "local_key", is_local=True))
        User.create_table()
    else:
        User.set_config(SupabaseConfig("https://your-project.supabase.co", "your-supabase-key"))

    # Create a new user
    new_user = User.create(name="John Doe", email="john@example.com")
    print(f"Created user: {new_user.id}, {new_user.name}, {new_user.email}")

    # Get a user by ID
    user = User.get(new_user.id)
    print(f"Retrieved user: {user.id}, {user.name}, {user.email}")

    # Update a user
    user.name = "Jane Doe"
    user.save()
    print(f"Updated user: {user.id}, {user.name}, {user.email}")

    # Filter users
    filtered_users = User.filter(name="Jane Doe")
    print(f"Filtered users: {[u.name for u in filtered_users]}")

    # Get all users
    all_users = User.all()
    print(f"All users: {[u.name for u in all_users]}")

    # Delete a user
    user.delete()
    print("User deleted")
