from contextlib import asynccontextmanager
from typing import Callable, Any
from .exceptions import (
    TransactionError, DatabaseError, ConfigurationError,
    ConnectionError
)
from .core.config import get_orm_config

class Transaction:
    def __init__(self, connection):
        self.connection = connection
        self.is_active = False
        self._savepoints = set()

    async def begin(self):
        """Begin a new transaction."""
        try:
            if self.is_active:
                raise TransactionError(
                    model=None,
                    operation="begin",
                    reason="Transaction is already active"
                )
            await self.connection.begin()
            self.is_active = True
        except Exception as e:
            raise TransactionError(
                model=None,
                operation="begin",
                original_error=e
            )

    async def commit(self):
        """Commit the current transaction."""
        try:
            if not self.is_active:
                raise TransactionError(
                    model=None,
                    operation="commit",
                    reason="No active transaction to commit"
                )
            await self.connection.commit()
            self.is_active = False
            self._savepoints.clear()
        except Exception as e:
            raise TransactionError(
                model=None,
                operation="commit",
                original_error=e
            )

    async def rollback(self):
        """Rollback the current transaction."""
        try:
            if not self.is_active:
                raise TransactionError(
                    model=None,
                    operation="rollback",
                    reason="No active transaction to rollback"
                )
            await self.connection.rollback()
            self.is_active = False
            self._savepoints.clear()
        except Exception as e:
            raise TransactionError(
                model=None,
                operation="rollback",
                original_error=e
            )

class TransactionManager:
    def __init__(self):
        try:
            self.config = get_orm_config()
            self.adapter = self._get_adapter()
        except Exception as e:
            raise ConfigurationError(
                model=None,
                config_key="transaction_manager",
                reason=str(e)
            )

    def _get_adapter(self):
        """Get the appropriate database adapter."""
        try:
            if self.config.use_supabase:
                from .adapters.supabase import SupabaseAdapter
                return SupabaseAdapter()
            from .adapters.postgresql import PostgreSQLAdapter
            return PostgreSQLAdapter()
        except ImportError as e:
            raise ConfigurationError(
                model=None,
                config_key="adapter",
                reason=f"Failed to import adapter: {str(e)}"
            )

    @asynccontextmanager
    async def transaction(self):
        """Async context manager for database transactions."""
        transaction = None
        try:
            connection = await self.adapter.get_connection()
            transaction = Transaction(connection)
            await transaction.begin()
            yield transaction
            await transaction.commit()
        except TransactionError:
            # Re-raise transaction-specific errors
            if transaction and transaction.is_active:
                await transaction.rollback()
            raise
        except Exception as e:
            if transaction and transaction.is_active:
                await transaction.rollback()
            raise TransactionError(
                model=None,
                operation="transaction",
                original_error=e
            )

    def atomic(self, func: Callable[..., Any]) -> Callable[..., Any]:
        """Decorator to make a function atomic (run in a transaction)."""
        async def wrapper(*args, **kwargs):
            async with self.transaction():
                return await func(*args, **kwargs)
        return wrapper

    async def run_in_transaction(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Run a function within a transaction."""
        async with self.transaction() as transaction:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                raise TransactionError(
                    model=None,
                    operation="run_in_transaction",
                    original_error=e
                )

    async def savepoint(self, name: str):
        """Create a savepoint within the current transaction."""
        try:
            if not self.adapter.in_transaction():
                raise TransactionError(
                    model=None,
                    operation="savepoint",
                    reason="Cannot create savepoint outside of a transaction"
                )
            await self.adapter.execute_raw(f"SAVEPOINT {name}")
            self._current_transaction._savepoints.add(name)
        except Exception as e:
            raise TransactionError(
                model=None,
                operation=f"create_savepoint:{name}",
                original_error=e
            )

    async def rollback_to_savepoint(self, name: str):
        """Rollback to a savepoint within the current transaction."""
        try:
            if not self.adapter.in_transaction():
                raise TransactionError(
                    model=None,
                    operation="rollback_to_savepoint",
                    reason="Cannot rollback to savepoint outside of a transaction"
                )
            if name not in self._current_transaction._savepoints:
                raise TransactionError(
                    model=None,
                    operation="rollback_to_savepoint",
                    reason=f"Savepoint '{name}' does not exist"
                )
            await self.adapter.execute_raw(f"ROLLBACK TO SAVEPOINT {name}")
        except Exception as e:
            raise TransactionError(
                model=None,
                operation=f"rollback_to_savepoint:{name}",
                original_error=e
            )

    async def release_savepoint(self, name: str):
        """Release a savepoint within the current transaction."""
        try:
            if not self.adapter.in_transaction():
                raise TransactionError(
                    model=None,
                    operation="release_savepoint",
                    reason="Cannot release savepoint outside of a transaction"
                )
            if name not in self._current_transaction._savepoints:
                raise TransactionError(
                    model=None,
                    operation="release_savepoint",
                    reason=f"Savepoint '{name}' does not exist"
                )
            await self.adapter.execute_raw(f"RELEASE SAVEPOINT {name}")
            self._current_transaction._savepoints.remove(name)
        except Exception as e:
            raise TransactionError(
                model=None,
                operation=f"release_savepoint:{name}",
                original_error=e
            )

# Global instance
transaction_manager = TransactionManager()