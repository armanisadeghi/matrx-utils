# database/orm/operations/update.py

from common import vcprint
from ..query.builder import QueryBuilder
from ..query.executor import QueryExecutor
from ..core.expressions import F

debug = False


async def update(model, filters, **kwargs):
    return await QueryBuilder(model).filter(**filters).update(**kwargs)


async def bulk_update(model, objects, fields):
    if not objects:
        return 0

    query = QueryBuilder(model)._build_query()
    query["objects"] = objects
    query["fields"] = fields

    executor = QueryExecutor(query)
    return await executor.adapter.bulk_update(query)


async def update_or_create(model, defaults=None, **kwargs):
    defaults = defaults or {}
    try:
        instance = await model.objects.get(**kwargs)
        for key, value in defaults.items():
            setattr(instance, key, value)
        await instance.save()
        return instance, False
    except model.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await model.objects.create(**params)
        return instance, True


async def increment(model, filters, **kwargs):
    updates = {}
    for field, amount in kwargs.items():
        updates[field] = F(field) + amount
    return await update(model, filters, **updates)


async def decrement(model, filters, **kwargs):
    updates = {}
    for field, amount in kwargs.items():
        updates[field] = F(field) - amount
    return await update(model, filters, **updates)


async def update_instance(instance, fields=None):
    model_class = instance.__class__
    pk_list = model_class._meta.primary_keys
    if not pk_list:
        raise ValueError(f"Cannot update {model_class.__name__} with no primary key.")
    pk_name = pk_list[0]
    pk_value = getattr(instance, pk_name, None)
    if pk_value is None:
        raise ValueError(f"Cannot update {model_class.__name__}, {pk_name} is None")

    update_data = {}
    # If fields is specified, only update those; otherwise, update all non-None fields
    field_names = fields if fields is not None else [f for f in model_class._fields if f != pk_name]
    for field_name in field_names:
        if field_name == pk_name:
            continue
        value = getattr(instance, field_name, None)
        if value is not None:  # Only include non-None values
            field = model_class._fields[field_name]
            update_data[field_name] = field.get_db_prep_value(value)

    filters = {pk_name: pk_value}

    if debug:
        vcprint(f"Updating instance with filters: {filters}", verbose=debug, color="cyan")
        vcprint(f"Update data: {update_data}", verbose=debug, color="cyan")

    result = await update(model_class, filters, **update_data)

    if result["rows_affected"] == 0:
        raise ValueError(f"No rows were updated for {model_class.__name__} with {pk_name}={pk_value}")

    if result["updated_rows"]:
        for key, value in result["updated_rows"][0].items():
            setattr(instance, key, value)

    return instance
