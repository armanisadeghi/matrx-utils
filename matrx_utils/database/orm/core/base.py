# database/orm/core/base.py

import asyncio
import re
from dataclasses import dataclass
from uuid import UUID
from matrx_utils.common import vcprint
from matrx_utils.database.orm.exceptions import (
    DoesNotExist,
    MultipleObjectsReturned,
    ValidationError,
)
from .fields import Field, ForeignKey
from .relations import ForeignKeyReference, InverseForeignKeyReference
from matrx_utils.database.orm.operations import create, update, delete
from matrx_utils.database.orm.query.builder import QueryBuilder
from matrx_utils.database.state import CachePolicy, StateManager

file_name = "database/orm/core/base.py"


def _to_snake_case(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def formated_error(message, class_name=None, method_name=None, context=None):
    vcprint("\n" + "=" * 80 + "\n", color="red")
    if class_name and method_name:
        vcprint(f"[ERROR in {file_name}: {class_name}.{method_name}()]\n", color="red")
        if context:
            vcprint(context, "Context", color="red", pretty=True)
    else:
        vcprint(f"[ERROR in {file_name}]\n", color="red")
        if context:
            vcprint(context, "Context", color="red", pretty=True)
    print()
    vcprint(message, color="red")
    vcprint("\n" + "=" * 80 + "\n", color="red")
    return


# https://grok.com/chat/f5581dd5-2684-445a-b2bd-40a2e7b63955 - DTO and eliminating the


class RuntimeContainer:
    def __init__(self):
        self._data = {}
        self._relationships = {}  # Store fetched relationships
        self.dto = None  # Reference to the DTO

    def __getattr__(self, name):
        # Check relationships first, then data
        if name in self._relationships:
            return self._relationships[name]
        return self._data.get(name)

    def __setattr__(self, name, value):
        if name in ("_data", "_relationships", "dto"):
            super().__setattr__(name, value)
        elif name in self._relationships:
            self._relationships[name] = value
        else:
            self._data[name] = value

    def set_relationship(self, name, value):
        """Store a fetched relationship."""
        self._relationships[name] = value
        if self.dto:
            setattr(self.dto, name, value)  # Sync with DTO

    def to_dict(self):
        data_dict = {k: str(v) if isinstance(v, UUID) else v for k, v in self._data.items()}
        rel_dict = {}
        for k, v in self._relationships.items():
            if isinstance(v, list):
                rel_dict[k] = [item.to_dict() if hasattr(item, "to_dict") else str(item) for item in v]
            elif v and hasattr(v, "to_dict"):
                rel_dict[k] = v.to_dict()
            else:
                rel_dict[k] = str(v) if v else None
        return {**data_dict, **rel_dict}


class RuntimeMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.runtime = RuntimeContainer()
        self._initialize_runtime()

    def _initialize_runtime(self):
        """Override in model-specific classes"""
        pass

    def to_dict(self):
        base_dict = super().to_dict()
        runtime_dict = self.runtime.to_dict()
        return {**base_dict, **runtime_dict}


@dataclass
class ModelOptions:
    table_name: str
    database: str
    fields: dict
    primary_keys: list
    unique_fields: set
    foreign_keys: dict
    inverse_foreign_keys: dict
    indexes: list
    unique_together: list
    constraints: list


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        if name == "Model":
            return super().__new__(mcs, name, bases, attrs)

        fields = {}
        foreign_keys = {}
        inverse_foreign_keys = {}
        unique_fields = set()
        primary_keys = []
        dynamic_fields = set()

        for key, value in attrs.items():
            if isinstance(value, Field):
                fields[key] = value
                if getattr(value, "unique", False):
                    unique_fields.add(key)
                if getattr(value, "primary_key", False):
                    primary_keys.append(key)
                if isinstance(value, ForeignKey):
                    foreign_keys[key] = ForeignKeyReference(
                        column_name=key,
                        to_model=value.to_model,
                        to_column=value.to_column,
                        related_name=value.related_name,
                        on_delete=value.on_delete,
                        on_update=value.on_update,
                    )
                    dynamic_fields.add(f"_{key}_related")

            elif isinstance(value, InverseForeignKeyReference):
                inverse_foreign_keys[key] = value
                dynamic_fields.add(f"_{key}_relation")

        if "_primary_keys" in attrs and attrs["_primary_keys"]:
            if primary_keys:
                error_message = f"Model {name} cannot have both fields with primary_key=True " "and _primary_keys defined"
                formated_error(error_message, class_name="Model", method_name="__new__")
                raise ValueError(error_message)

            primary_keys = attrs["_primary_keys"]

            for pk in primary_keys:
                if pk not in fields:
                    error_message = f"Primary key field '{pk}' not found in model {name}"
                    formated_error(error_message, class_name="Model", method_name="__new__")
                    raise ValueError(error_message)

        if not primary_keys:
            error_message = f"Model {name} must define at least one primary key field"
            formated_error(error_message, class_name="Model", method_name="__new__")
            raise ValueError(error_message)

        if "_inverse_foreign_keys" in attrs:
            for key, value in attrs["_inverse_foreign_keys"].items():
                if "referenced_field" not in value:
                    error_message = f"Inverse foreign key '{key}' must specify 'referenced_field'"
                    formated_error(error_message, class_name="Model", method_name="__new__")
                    raise ValueError(error_message)
                inverse_foreign_keys[key] = InverseForeignKeyReference(**value)
                dynamic_field_name = f"_{key}_relation"
                dynamic_fields.add(dynamic_field_name)

        table_name = attrs.get("_table_name")
        if not table_name:
            table_name = _to_snake_case(name)

        options = ModelOptions(
            table_name=table_name,
            database=attrs.get("_database"),
            fields=fields,
            primary_keys=primary_keys,
            unique_fields=unique_fields,
            foreign_keys=foreign_keys,
            inverse_foreign_keys=inverse_foreign_keys,
            indexes=attrs.get("_indexes", []),
            unique_together=attrs.get("_unique_together", []),
            constraints=attrs.get("_constraints", []),
        )

        attrs["_meta"] = options
        attrs["_fields"] = fields
        attrs["_dynamic_fields"] = dynamic_fields

        def __init__(self, **kwargs):
            super(Model, self).__init__()
            for field_name, field in self._fields.items():
                value = kwargs.get(field_name, field.get_default())
                if hasattr(field, "to_python"):  # Only change: apply to_python()
                    value = field.to_python(value)
                setattr(self, field_name, value)
            self._extra_data = {k: v for k, v in kwargs.items() if k not in self._fields}

            self._dynamic_data = {}
            for field in self._dynamic_fields:
                if field.endswith("_related"):
                    self._dynamic_data[field] = {}
                elif field.endswith("_relation"):
                    self._dynamic_data[field] = []

        def get_related(self, field_name):
            regular_field = f"_{field_name}_related"
            if regular_field in self._dynamic_fields:
                return self._dynamic_data[regular_field]

            relation_field = f"_{field_name}_relation"
            if relation_field in self._dynamic_fields:
                return self._dynamic_data[relation_field]

            error_message = f"No related field for {field_name}"
            formated_error(error_message, class_name="Model", method_name="__init__")
            raise AttributeError(error_message)

        def set_related(self, field_name, value, is_inverse=False):
            if is_inverse:
                field = f"_{field_name}_relation"
            else:
                field = f"_{field_name}_related"

            if field not in self._dynamic_fields:
                error_message = f"No related field for {field_name}"
                formated_error(error_message, class_name="Model", method_name="__init__")
                raise AttributeError(error_message)
            self._dynamic_data[field] = value

        attrs["__init__"] = __init__
        attrs["get_related"] = get_related
        attrs["set_related"] = set_related

        cls = super().__new__(mcs, name, bases, attrs)
        if name != "Model":
            StateManager.register_model(cls)

        return cls


class Model(RuntimeMixin, metaclass=ModelMeta):
    DoesNotExist = DoesNotExist
    MultipleObjectsReturned = MultipleObjectsReturned
    ValidationError = ValidationError

    _meta = None
    _fields = None
    _cache_policy = CachePolicy.SHORT_TERM
    _cache_timeout = None
    _realtime_updates = False
    _table_name = None
    _database = None
    _indexes = None
    _unique_together = None
    _constraints = None
    _inverse_foreign_keys = {}

    def __init__(self, **kwargs):
        for field_name, field in self._fields.items():
            value = kwargs.get(field_name, field.get_default())
            setattr(self, field_name, value)
        self._extra_data = {k: v for k, v in kwargs.items() if k not in self._fields}

    @classmethod
    async def create(cls, **kwargs):
        instance = await create.create_instance(cls, **kwargs)
        await StateManager.cache(cls, instance)
        return instance

    @classmethod
    async def get(cls, use_cache=True, **kwargs):
        if use_cache:
            return await StateManager.get(cls, **kwargs)
        else:
            return await QueryBuilder(model=cls).filter(**kwargs).get()

    @classmethod
    def get_sync(cls, use_cache=True, **kwargs):
        """
        Synchronous wrapper for get(). Runs the async get() method in the current event loop.
        Use this in synchronous contexts to avoid RuntimeWarning for unawaited coroutines.
        """
        # Check if there's an active event loop
        try:
            loop = asyncio.get_running_loop()
            # If we're in an async context, warn the user to use async get
            raise RuntimeError(
                "Model.get_sync() called in an async context. Use await Model.get() instead."
            )
        except RuntimeError as e:
            if "no running event loop" not in str(e):
                raise  # Re-raise if it's not the expected "no running loop" error

        # No running loop: safe to run synchronously
        return asyncio.run(cls.get(use_cache=use_cache, **kwargs))



    @classmethod
    async def get_or_none(cls, use_cache=True, **kwargs):
        try:
            if use_cache:
                return await StateManager.get_or_none(cls, **kwargs)
            else:
                return await QueryBuilder(model=cls).filter(**kwargs).get_or_none()
        except DoesNotExist:
            return None
        except Exception as e:
            vcprint(f"Error in get_or_none for {cls.__name__}: {str(e)}", color="red")
            return None

    @classmethod
    def filter(cls, **kwargs):
        return QueryBuilder(model=cls).filter(**kwargs)

    @classmethod
    async def all(cls):
        results = await QueryBuilder(model=cls).all()
        await StateManager.cache_bulk(cls, results)
        return results

    async def save(self, **kwargs):
        """Save the current state of the model instance."""
        if kwargs:
            error_message = f"Error for {self.__class__.__name__}: For updating fields, use update() instead of save()"
            formated_error(error_message, class_name="Model", method_name="save", context=kwargs)
            raise TypeError(error_message)

        is_update = hasattr(self, "id") and self.id is not None
        if is_update:
            await update.update_instance(self)
        else:
            await create.create_instance(self.__class__, **self.__dict__)
        await StateManager.cache(self.__class__, self)
        return self

    async def update(self, **kwargs):
        """
        Update specific fields and save in one operation.
        Returns the updated instance.
        """
        # Validate fields
        invalid_fields = [k for k in kwargs if k not in self._fields]
        if invalid_fields:
            vcprint(self._fields, "Model Fields", color="yellow")
            error_message = f"Invalid fields for {self.__class__.__name__}: {invalid_fields}"
            formated_error(error_message, class_name="Model", method_name="update", context=kwargs)
            raise ValueError(error_message)

        # Update instance attributes
        for field, value in kwargs.items():
            setattr(self, field, value)

        # Save only the specified fields
        await update.update_instance(self, fields=kwargs.keys())  # Pass specific fields
        return self

    @classmethod
    async def update_fields(cls, instance_or_id, **kwargs):
        """
        Static method to update an instance or create it if it doesn't exist.
        Merges the provided fields with existing values.
        """
        try:
            if isinstance(instance_or_id, cls):
                instance = instance_or_id
            else:
                instance = await cls.filter(id=instance_or_id).first()
                if instance is None:
                    raise DoesNotExist(
                        model=cls,
                        filters={"id": instance_or_id},
                        class_name="Model",
                        method_name="update_fields",
                    )

            # Validate fields first
            invalid_fields = [k for k in kwargs if k not in cls._fields]
            if invalid_fields:
                raise ValidationError(
                    model=cls,
                    field="multiple",
                    value=invalid_fields,
                    reason="Invalid fields provided",
                    class_name="Model",
                    method_name="update_fields",
                )

            # Update the instance
            for field, value in kwargs.items():
                setattr(instance, field, value)

            await instance.save()
            return instance

        except DoesNotExist as e:
            # Just print the formatted message and return None
            print(str(e))
            return None
        except ValidationError as e:
            # These we want to raise as they indicate developer error
            raise e

    async def delete(self):
        await delete.delete_instance(self)
        await StateManager.remove(self.__class__, self)

    def get_cache_key(self):
        return "_".join(str(getattr(self, pk)) for pk in self._meta.primary_keys)

    @property
    def table_name(self):
        return self._meta.table_name

    @classmethod
    def get_field(cls, field_name):
        return cls._fields.get(field_name)

    @classmethod
    def get_relation(cls, field_name):
        field = cls.get_field(field_name)
        if isinstance(field, (ForeignKeyReference, InverseForeignKeyReference)):
            return field
        error_message = f"{field_name} is not a relation field"
        formated_error(error_message, class_name="Model", method_name="get_relation")
        raise ValueError(error_message)

    def to_dict(self):
        data = {}
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = field.to_python(value)

        if hasattr(self, "runtime"):
            data["runtime"] = self.runtime.to_dict()
        if hasattr(self, "dto"):
            data["dto"] = self.dto.to_dict()
        return data

    def to_flat_dict(self):
        data = {}
        for field_name, field in self._fields.items():
            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = field.to_python(value)

        runtime_data = self.runtime.to_dict() if hasattr(self, "runtime") else {}

        dto_data = self.dto.to_dict() if hasattr(self, "dto") else {}

        return {**data, **runtime_data, **dto_data}

    @classmethod
    def from_db_result(cls, data):
        instance = cls()
        for field_name, value in data.items():
            if field_name in cls._fields:
                field = cls._fields[field_name]
                setattr(instance, field_name, field.from_db_value(value))
            else:
                instance._extra_data[field_name] = value
        return instance

    async def fetch_fk(self, field_name):
        """Fetch a single foreign key relationship"""
        if field_name not in self._meta.foreign_keys:
            error_message = f"No foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="fetch_fk")
            raise ValueError(error_message)

        fk_ref = self._meta.foreign_keys[field_name]
        value = getattr(self, field_name)
        if value is not None:
            return await fk_ref.fetch_data(self, value)
        return None

    async def fetch_ifk(self, field_name):
        """Fetch a single inverse foreign key relationship"""
        if field_name not in self._meta.inverse_foreign_keys:
            error_message = f"No inverse foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="fetch_ifk")
            raise ValueError(error_message)

        ifk_ref = self._meta.inverse_foreign_keys[field_name]
        referenced_value = getattr(self, ifk_ref.referenced_field)
        if referenced_value is not None:
            return await ifk_ref.fetch_data(self)
        return []

    async def fetch_one_relation(self, field_name: str):
        if field_name in self._meta.foreign_keys:
            return await self.fetch_fk(field_name)

        if field_name in self._meta.inverse_foreign_keys:
            return await self.fetch_ifk(field_name)

        # proper error message
        error_message = f"'{field_name}' is not a valid relationship field. " "Field must be one of: " f"{', '.join(self._meta.foreign_keys | self._meta.inverse_foreign_keys)}"
        formated_error(error_message, class_name="Model", method_name="fetch_one_relation")
        raise ValueError(error_message)

    async def fetch_fks(self):
        """Fetch all foreign key relationships"""
        results = {}
        for field_name in self._meta.foreign_keys:
            results[field_name] = await self.fetch_fk(field_name)
        return results

    async def fetch_ifks(self):
        """Fetch all inverse foreign key relationships"""
        results = {}
        for field_name in self._meta.inverse_foreign_keys:
            results[field_name] = await self.fetch_ifk(field_name)
        return results

    async def fetch_all_related(self):
        """Fetch all related data (both FKs and inverse FKs)"""
        fk_results = await self.fetch_fks()
        ifk_results = await self.fetch_ifks()
        return {"foreign_keys": fk_results, "inverse_foreign_keys": ifk_results}

    async def filter_fk(self, field_name, **kwargs):
        if field_name not in self._meta.foreign_keys:
            error_message = f"No foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="filter_fk")
            raise ValueError(error_message)
        fk_ref = self._meta.foreign_keys[field_name]
        value = getattr(self, field_name)
        if value is not None:
            return await fk_ref.related_model.filter(**{fk_ref.to_column: value}, **kwargs).all()
        return []

    async def filter_ifk(self, field_name, **kwargs):
        """Filter inverse foreign key relationships with additional criteria"""
        if field_name not in self._meta.inverse_foreign_keys:
            error_message = f"No inverse foreign key found for field {field_name}"
            formated_error(error_message, class_name="Model", method_name="filter_ifk")
            raise ValueError(error_message)

        ifk_ref = self._meta.inverse_foreign_keys[field_name]
        referenced_value = getattr(self, ifk_ref.referenced_field)
        vcprint(referenced_value, pretty=True, color="yellow")
        if referenced_value is not None:
            return await ifk_ref.related_model.filter(**{ifk_ref.from_field: referenced_value}, **kwargs).all()
        return []

    async def filter_one_relation(self, field_name: str, **kwargs):
        """
        Filter a relationship by field name with additional criteria,
        automatically determining whether it's a FK or IFK relationship
        """
        if field_name in self._meta.foreign_keys:
            return await self.filter_fk(field_name, **kwargs)

        if field_name in self._meta.inverse_foreign_keys:
            return await self.filter_ifk(field_name, **kwargs)

        error_message = f"'{field_name}' is not a valid relationship field. " "Field must be one of: " f"{', '.join(self._meta.foreign_keys | self._meta.inverse_foreign_keys)}"
        formated_error(error_message, class_name="Model", method_name="filter_one_relation")
        raise ValueError(error_message)

    # ===== I'm not sure if this adds any value because when we try to 'fetch', the database will returned cached data, even if we don't tell it to.

    def get_related(self, field_name):
        regular_field = f"_{field_name}_related"
        inverse_field = f"_{field_name}_relation"
        if regular_field in self._dynamic_fields:
            return self._dynamic_data[regular_field]
        elif inverse_field in self._dynamic_fields:
            return self._dynamic_data[inverse_field]
        error_message = f"No related field for {field_name}"
        formated_error(error_message, class_name="Model", method_name="get_related")
        raise AttributeError(error_message)

    def has_related(self, field_name):
        """Check if related data is already loaded"""
        try:
            data = self.get_related(field_name)
            if isinstance(data, dict):
                return bool(data)
            return bool(data)
        except AttributeError:
            return False

    @classmethod
    async def get_by_id(cls, id_value, use_cache=True):
        pk_field = cls._meta.primary_keys[0]
        return await cls.get(use_cache=use_cache, **{pk_field: id_value})

    @classmethod
    async def get_many(cls, **kwargs):
        return await QueryBuilder(model=cls).filter(**kwargs).all()
