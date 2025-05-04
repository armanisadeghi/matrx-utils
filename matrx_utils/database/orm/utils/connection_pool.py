# matrx_utils\database\orm\utils\connection_pool.py
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from threading import Lock
from database.orm.core.config import get_orm_config


class ConnectionPool:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        config = get_orm_config().database
        self.pool = ThreadedConnectionPool(
            minconn=1,
            maxconn=config.connection_pool_size,
            host=config.host,
            port=config.port,
            dbname=config.name,
            user=config.user,
            password=config.password,
        )

    def get_connection(self):
        return self.pool.getconn()

    def return_connection(self, conn):
        self.pool.putconn(conn)

    def close_all(self):
        self.pool.closeall()


class PooledConnection:
    def __init__(self):
        self.pool = ConnectionPool()
        self.connection = None

    def __enter__(self):
        self.connection = self.pool.get_connection()
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pool.return_connection(self.connection)


# Usage
def execute_query(sql, params=None):
    with PooledConnection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()
