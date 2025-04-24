# database/orm/core/async_db_manager.py

import os
import asyncio
import traceback
import asyncpg
from contextlib import asynccontextmanager
from matrx_utils.database.orm.core.config import get_database_config, DatabaseConfigError
from matrx_utils.database.orm.exceptions import (
    DatabaseError,
    ConnectionError,
    ConfigurationError,
    IntegrityError,
    ParameterError,
    QueryError,
    StateError,
    AdapterError,
    UnknownDatabaseError,
    ValidationError,
)
from matrx_utils.database.orm.error_handling import handle_orm_operation
from matrx_utils import vcprint


class AsyncDatabaseManager:
    _instance = None
    _pools = {}
    _locks = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def get_pool(cls, config_name):
        """Get or create a connection pool for the specified database with error handling."""
        if config_name not in cls._locks:
            cls._locks[config_name] = asyncio.Lock()

        async with cls._locks[config_name]:
            if config_name not in cls._pools:
                async with handle_orm_operation(
                    operation_name="create_connection_pool",
                    model=None,
                    config_name=config_name,
                ):
                    try:
                        config = get_database_config(config_name)
                        pool = await asyncpg.create_pool(
                            host=config["host"],
                            port=config["port"],
                            database=config["database_name"],
                            user=config["user"],
                            password=config["password"],
                            min_size=5,
                            max_size=20,
                            command_timeout=10,
                            ssl="require",
                            statement_cache_size=0,
                        )
                        cls._pools[config_name] = pool
                    except DatabaseConfigError as e:
                        raise ConfigurationError(
                            model=None,
                            config_key=config_name,
                            reason=f"Invalid or missing configuration: {str(e)}",
                        )
                    except asyncpg.exceptions.ConnectionFailureError as e:
                        raise ConnectionError(
                            model=None,
                            db_url=f"{config.get('host')}:{config.get('port')}/{config.get('database_name')}",
                            original_error=e,
                        )
                    except asyncpg.exceptions.InvalidAuthorizationSpecificationError as e:
                        raise ConnectionError(
                            model=None,
                            db_url=f"{config.get('host')}:{config.get('port')}/{config.get('database_name')}",
                            original_error=e,
                        )
                    except Exception as e:
                        raise AdapterError(model=None, adapter_name="asyncpg", original_error=e)
            return cls._pools[config_name]

    @classmethod
    @asynccontextmanager
    async def get_connection(cls, config_name, timeout=10.0):
        """Get a connection from the pool with a timeout and error handling."""
        pool = await cls.get_pool(config_name)
        try:
            async with asyncio.timeout(timeout):
                conn = await pool.acquire()
                try:
                    yield conn
                finally:
                    await pool.release(conn)
        except asyncio.TimeoutError:
            async with handle_orm_operation(
                operation_name="acquire_connection",
                model=None,
                config_name=config_name,
                timeout=timeout,
            ):
                raise DatabaseError(
                    model=None,
                    message=f"Timeout acquiring connection after {timeout}s",
                    details={"config_name": config_name, "timeout": timeout},
                )
        except asyncpg.exceptions.InterfaceError as e:
            async with handle_orm_operation(
                operation_name="acquire_connection",
                model=None,
                config_name=config_name,
                timeout=timeout,
            ):
                raise StateError(
                    model=None,
                    operation="acquire_connection",
                    reason="Connection pool issue",
                    details={"config_name": config_name},
                    original_error=e,
                )

    @classmethod
    async def execute_query(cls, config_name, query, *args, timeout=10.0):
        """Execute a query and return results with error handling."""
        async with handle_orm_operation(
            operation_name="execute_query",
            model=None,
            config_name=config_name,
            query=query,
            args=args,
            timeout=timeout,
        ):
            async with cls.get_connection(config_name, timeout) as conn:
                try:
                    results = await conn.fetch(query, *args)
                    return results
                except asyncpg.exceptions.PostgresSyntaxError as e:
                    raise QueryError(
                        model=None,
                        message=f"Invalid SQL syntax: {str(e)}",
                        details={
                            "query": query,
                            "args": args,
                            "config_name": config_name,
                        },
                    )
                except asyncpg.exceptions.UniqueViolationError as e:
                    raise IntegrityError(
                        model=None,
                        constraint="unknown",
                        original_error=e,
                    )
                except asyncpg.exceptions.ConnectionDoesNotExistError as e:
                    raise ConnectionError(
                        model=None,
                        db_url=config_name,
                        original_error=e,
                    )
                except asyncpg.exceptions.DataError as e:
                    raise ParameterError(model=None, query=query, args=args, reason=str(e))
                except Exception as e:
                    tb = traceback.format_exc()
                    raise UnknownDatabaseError(
                        model=None,
                        operation="execute_query",
                        query=query,
                        args=args,
                        traceback=tb,
                        original_error=e,
                    )

    @classmethod
    async def cleanup(cls):
        """Close all connection pools with error handling."""
        async with handle_orm_operation(operation_name="cleanup_pools", model=None, active_pools=len(cls._pools)):
            for config_name, pool in list(cls._pools.items()):
                try:
                    await pool.close()
                except Exception as e:
                    raise StateError(
                        model=None,
                        operation="cleanup_pools",
                        reason=f"Failed to close pool for {config_name}",
                        details={"config_name": config_name},
                        original_error=e,
                    )
            cls._pools.clear()
            cls._locks.clear()


async def main():
    db = AsyncDatabaseManager()
    try:
        results = await db.execute_query(
            "supabase_automation_matrix",
            "SELECT * FROM data_broker WHERE id = $1",
            "0fc49b4c-fc8b-467e-9dda-f43dedf74a9d",
        )
        print(results)
    except DatabaseError as e:
        print(f"Database error: {e}")
    finally:
        await db.cleanup()


async def cause_error():
    db = AsyncDatabaseManager()
    try:
        results = await db.execute_query(
            "supabase_automation_matrix",
            "SELECT * FROM data_broker WHERE id = $1",
            "aaaa0fc49b4c-fc8b-467e-9dda-f43dedf74a9d",
        )
        print(results)
    except DatabaseError as e:
        print(f"Database error")
    finally:
        await db.cleanup()


if __name__ == "__main__":
    os.system("cls")
    asyncio.run(cause_error())
