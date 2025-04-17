import psycopg2
from psycopg2.extras import RealDictCursor


class Model:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def create_table(cls):
        columns = [f"{name} {attr.db_type}" for name, attr in cls.__dict__.items() if isinstance(attr, Field)]
        query = f"CREATE TABLE IF NOT EXISTS {cls.__name__.lower()} ({', '.join(columns)})"
        cls.execute(query)

    @classmethod
    def execute(cls, query, params=None):
        with psycopg2.connect("dbname=testdb user=postgres password=password") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                if query.lower().startswith("select"):
                    return [cls(**row) for row in cur.fetchall()]
                conn.commit()

    @classmethod
    def all(cls):
        return cls.execute(f"SELECT * FROM {cls.__name__.lower()}")

    def save(self):
        fields = [name for name, attr in self.__class__.__dict__.items() if isinstance(attr, Field)]
        values = [getattr(self, field) for field in fields]
        placeholders = ", ".join(["%s"] * len(fields))
        query = f"INSERT INTO {self.__class__.__name__.lower()} ({', '.join(fields)}) VALUES ({placeholders})"
        self.execute(query, values)


class Field:
    def __init__(self, db_type):
        self.db_type = db_type


class CharField(Field):
    def __init__(self, max_length=255):
        super().__init__(f"VARCHAR({max_length})")


class IntegerField(Field):
    def __init__(self):
        super().__init__("INTEGER")


# Example usage
class User(Model):
    name = CharField(max_length=100)
    age = IntegerField()


# Create table
User.create_table()

# Create a new user
user = User(name="John Doe", age=30)
user.save()

# Fetch all users
all_users = User.all()
for user in all_users:
    print(f"Name: {user.name}, Age: {user.age}")
