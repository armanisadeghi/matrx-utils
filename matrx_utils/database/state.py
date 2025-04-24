# database/orm/core/state.py

from datetime import datetime, timedelta
from enum import Enum
import asyncio
from matrx_utils import vcprint
from matrx_utils.database.orm.exceptions import (
    ValidationError,
    DoesNotExist,
    ConfigurationError,
    StateError,
    CacheError,
)


class CachePolicy(Enum):
    PERMANENT = "permanent"
    LONG_TERM = "long_term"
    SHORT_TERM = "short_term"
    INSTANT = "instant"


class ModelState:
    def __init__(self, model_class):
        try:
            self.model_class = model_class
            self.policy = getattr(model_class, "_cache_policy", CachePolicy.SHORT_TERM)
            self.timeout = getattr(model_class, "_cache_timeout", None)
            self.realtime = getattr(model_class, "_realtime_updates", False)
            self._cache = {}
            self._cache_times = {}
            self._subscriptions = set()
            self._locks = {}
        except Exception as e:
            raise ConfigurationError(
                model=model_class,
                config_key="model_state",
                reason=f"Failed to initialize model state: {str(e)}",
            )

    def _get_cache_key(self, **kwargs):
        try:
            primary_keys = self.model_class._meta.primary_keys
            if all(pk in kwargs for pk in primary_keys):
                return "_".join(str(kwargs[pk]) for pk in primary_keys)
            return None
        except Exception as e:
            raise CacheError(
                model=self.model_class,
                operation="get_cache_key",
                details={"kwargs": kwargs},
                original_error=e,
            )

    def _get_record_cache_key(self, record):
        return "_".join(str(getattr(record, pk)) for pk in record._meta.primary_keys)

    async def get(self, **kwargs):
        """
        Get a record from cache with proper error handling.

        Args:
            **kwargs: Filter criteria for finding the record

        Returns:
            Record if found in cache and not stale, None otherwise

        Raises:
            CacheError: If there's an error accessing the cache
            ValidationError: If the lookup criteria are invalid
        """
        if not kwargs:
            raise ValidationError(
                model=self.model_class,  # Use self.model_class here
                reason="No lookup criteria provided",
            )

        try:
            # Get cache key and validate
            cache_key = self._get_cache_key(**kwargs)

            # Initialize lock if needed
            if cache_key not in self._locks:
                try:
                    self._locks[cache_key] = asyncio.Lock()
                except Exception as e:
                    raise CacheError(
                        model=self.model_class,  # Use self.model_class here
                        operation="create_lock",
                        details={"cache_key": cache_key},
                        original_error=e,
                    )

            # Use lock for thread safety
            async with self._locks[cache_key]:
                # Try direct cache key lookup first
                if cache_key and cache_key in self._cache:
                    record = self._cache[cache_key]
                    try:
                        if not self._is_stale(record):
                            vcprint(
                                f"[MODEL STATE {self.model_class.__name__}]✅  Returning cache key: {cache_key}",
                                color="pink",
                            )
                            return record
                    except Exception as e:
                        raise CacheError(
                            model=self.model_class,  # Use self.model_class here
                            operation="check_staleness",
                            details={
                                "cache_key": cache_key,
                                "record_id": getattr(record, "id", None),
                            },
                            original_error=e,
                        )

                # Try finding by criteria if direct lookup fails
                try:
                    cached_record = self._find_in_cache(**kwargs)
                    if cached_record and not self._is_stale(cached_record):
                        vcprint(
                            f"[MODEL STATE {self.model_class.__name__} ]✅  Returning cached record for kwargs: {kwargs}",
                            color="pink",
                        )
                        return cached_record
                except Exception as e:
                    raise CacheError(
                        model=self.model_class,  # Use self.model_class here
                        operation="find_in_cache",
                        details={"kwargs": kwargs},
                        original_error=e,
                    )

                return None

        except (CacheError, ValidationError):
            # Pass through our custom exceptions
            raise
        except asyncio.CancelledError:
            # Handle task cancellation
            raise CacheError(
                model=self.model_class,  # Use self.model_class here
                operation="get",
                details={"kwargs": kwargs},
                reason="Operation cancelled",
            )
        except Exception as e:
            # Catch all other exceptions
            raise CacheError(
                model=self.model_class,  # Use self.model_class here
                operation="get",
                details={"kwargs": kwargs, "error_type": type(e).__name__},
                original_error=e,
            )

    def _find_in_cache(self, **kwargs):
        for record in self._cache.values():
            if all(getattr(record, k) == v for k, v in kwargs.items()):
                return record
        return None

    def _is_stale(self, record):
        cache_key = self._get_record_cache_key(record)
        cache_time = self._cache_times.get(cache_key)
        if not cache_time:
            return True

        if self.timeout is not None:
            return (datetime.now() - cache_time).total_seconds() > self.timeout

        now = datetime.now()
        if self.policy == CachePolicy.PERMANENT:
            return False
        elif self.policy == CachePolicy.LONG_TERM:
            return now - cache_time > timedelta(hours=4)
        elif self.policy == CachePolicy.SHORT_TERM:
            return now - cache_time > timedelta(minutes=10)
        elif self.policy == CachePolicy.INSTANT:
            return now - cache_time > timedelta(minutes=1)
        return True

    async def cache(self, record):
        """Cache a record with proper error handling."""
        try:
            if not record:
                raise ValidationError(model=self.model_class, reason="Cannot cache None record")

            cache_key = self._get_record_cache_key(record)
            if not cache_key:
                raise ValidationError(
                    model=self.model_class,
                    reason="Could not generate cache key for record",
                )

            self._cache[cache_key] = record
            self._cache_times[cache_key] = datetime.now()

            if self.realtime and self.policy in (
                CachePolicy.PERMANENT,
                CachePolicy.LONG_TERM,
            ):
                await self._ensure_subscription(record)
        except (ValidationError, CacheError):
            raise
        except Exception as e:
            raise CacheError(
                model=self.model_class,
                operation="cache",
                details={"record_id": getattr(record, "id", None)},
                original_error=e,
            )

    async def remove(self, record):
        cache_key = self._get_record_cache_key(record)
        self._cache.pop(cache_key, None)
        self._cache_times.pop(cache_key, None)

    async def _ensure_subscription(self, record):
        cache_key = self._get_record_cache_key(record)
        if cache_key not in self._subscriptions:
            await self._setup_subscription(record)
            self._subscriptions.add(cache_key)

    async def _setup_subscription(self, record):
        pass

    def update_from_subscription(self, data):
        record = self.model_class.from_db_result(data)
        cache_key = self._get_record_cache_key(record)
        self._cache[cache_key] = record
        self._cache_times[cache_key] = datetime.now()

    def get_all_cached(self):
        """Returns all cached records as a list."""
        return list(self._cache.values())

    def count(self):
        """Returns the count of items in the cache."""
        return len(self._cache)

    def clear_cache(self):
        """Clears the entire cache for this model."""
        self._cache.clear()
        self._cache_times.clear()
        self._subscriptions.clear()


class StateManager:
    _states = {}

    @classmethod
    def register_model(cls, model_class):
        """Register a model class with error handling."""
        try:
            cls._states[model_class.__name__] = ModelState(model_class)
        except Exception as e:
            raise ConfigurationError(
                model=model_class,
                config_key="state_registration",
                reason=f"Failed to register model: {str(e)}",
            )

    @classmethod
    async def get(cls, model_class, **kwargs):
        """Fetch a single record with comprehensive error handling."""
        try:
            if model_class.__name__ not in cls._states:
                raise StateError(
                    model=model_class,
                    operation="get",
                    reason="Model not registered with StateManager",
                )

            state = cls._states[model_class.__name__]

            # Try cache first
            record = await state.get(**kwargs)
            if record:
                return record

            try:
                record = await model_class.get(use_cache=False, **kwargs)
            except DoesNotExist:
                # Don't cache None results
                raise
            except Exception as e:
                raise CacheError(
                    model=model_class,
                    operation="database_fetch",
                    details={"kwargs": kwargs},
                    original_error=e,
                )

            # Cache the record
            if record:
                await cls.cache(model_class, record)

            return record
        except (DoesNotExist, StateError, CacheError):
            raise
        except Exception as e:
            raise StateError(
                model=model_class,
                operation="get",
                details={"kwargs": kwargs},
                original_error=e,
            )

    @classmethod
    async def get_or_none(cls, model_class, **kwargs):
        """
        Fetch a single record, returning None if not found.
        Includes comprehensive error handling.
        """
        try:
            if model_class.__name__ not in cls._states:
                raise StateError(
                    model=model_class,
                    operation="get_or_none",
                    reason="Model not registered with StateManager",
                )

            state = cls._states[model_class.__name__]

            # Try cache first
            try:
                record = await state.get(**kwargs)
                if record:
                    return record
            except DoesNotExist:
                pass  # Continue to database lookup if not in cache

            # Fetch from database
            try:
                record = await model_class.get(use_cache=False, **kwargs)
                if record:
                    # Cache the record if found
                    await cls.cache(model_class, record)
                    return record
                return None
            except DoesNotExist:
                return None
            except Exception as e:
                vcprint(
                    f"Database error in get_or_none for {model_class.__name__}: {str(e)}",
                    color="red",
                )
                return None

        except StateError:
            return None
        except Exception as e:
            vcprint(
                f"Unexpected error in get_or_none for {model_class.__name__}: {str(e)}",
                color="red",
            )
            return None

    @classmethod
    async def get_all(cls, model_class, **kwargs):
        """Fetch multiple records, ensuring they are cached."""
        state = cls._states[model_class.__name__]

        # Step 1: Try getting cached records with the given filter
        cached_records = [record for record in state.get_all_cached() if all(getattr(record, key) == value for key, value in kwargs.items())]
        if cached_records:
            vcprint(
                f"[STATE MANAGER {model_class.__name__}] ✅ Returning {len(cached_records)} cached records",
                color="pink",
            )
            return cached_records

        # Step 2: Fetch from the database
        records = await model_class.filter(**kwargs).all()

        # Step 3: Cache all fetched records before returning
        if records:
            await cls.cache_bulk(model_class, records)

        return records

    @classmethod
    async def cache(cls, model_class, record):
        """Caches a record to ensure it's always accessible."""
        state = cls._states[model_class.__name__]
        await state.cache(record)

    @classmethod
    async def cache_bulk(cls, model_class, records):
        """Cache multiple records with error handling."""
        try:
            if not records:
                return

            state = cls._states.get(model_class.__name__)
            if not state:
                raise StateError(
                    model=model_class,
                    operation="cache_bulk",
                    reason="Model not registered with StateManager",
                )

            for record in records:
                try:
                    if not await state.get(id=getattr(record, "id", None)):
                        await state.cache(record)
                except Exception as e:
                    vcprint(f"Failed to cache record: {str(e)}", color="yellow")
                    continue
        except StateError:
            raise
        except Exception as e:
            raise StateError(
                model=model_class,
                operation="cache_bulk",
                details={"record_count": len(records)},
                original_error=e,
            )

    @classmethod
    async def remove(cls, model_class, record):
        """Removes a specific record from the cache."""
        state = cls._states[model_class.__name__]
        await state.remove(record)

    @classmethod
    async def remove_bulk(cls, model_class, records):
        """Removes multiple records from the cache."""
        state = cls._states[model_class.__name__]
        for record in records:
            await state.remove(record)

    @classmethod
    async def update(cls, model_class, record):
        """Ensures updates reflect in cache instantly."""
        state = cls._states[model_class.__name__]
        await state.cache(record)

    @classmethod
    async def clear_cache(cls, model_class):
        """Clears the cache for a specific model."""
        state = cls._states[model_class.__name__]
        state.clear_cache()

    @classmethod
    async def count(cls, model_class):
        """Returns the number of cached records for a model."""
        state = cls._states[model_class.__name__]
        return state.count()
