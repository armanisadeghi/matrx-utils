from ..core.fields import Field
from ..query.builder import QueryBuilder
from ..query.executor import QueryExecutor


async def create(model, **kwargs):
    instance = model(**kwargs)
    return await save(instance)


async def save(instance):
    data = {}
    for field_name, field in instance.__class__._fields.items():
        if isinstance(field, Field):
            value = getattr(instance, field_name)
            if value is None and field.default is not None:
                value = field.get_default()
            if value is not None:
                data[field_name] = field.get_db_prep_value(value)

    query = QueryBuilder(instance.__class__)._build_query()
    query["data"] = data

    executor = QueryExecutor(query)
    result = await executor.insert(query)

    # Convert DB values back to Python objects
    for key, value in result.items():
        field = instance.__class__._fields.get(key)
        if field and isinstance(field, Field):
            value = field.to_python(value)
        setattr(instance, key, value)

    return instance


async def bulk_create(model, objects):
    instances = [model(**obj) for obj in objects]
    query = QueryBuilder(model)._build_query()
    query["data"] = [
        {
            field_name: field.get_db_prep_value(getattr(instance, field_name))
            for field_name, field in model._fields.items()
            if isinstance(field, Field) and (getattr(instance, field_name) is not None or not field.nullable)
        }
        for instance in instances
    ]

    executor = QueryExecutor(query)
    results = await executor.bulk_insert(query)

    for instance, result in zip(instances, results):
        for key, value in result.items():
            setattr(instance, key, value)

    return instances


async def get_or_create(model, defaults=None, **kwargs):
    defaults = defaults or {}
    try:
        instance = await model.objects.get(**kwargs)
        return instance, False
    except model.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model, **params)
        return instance, True


async def update_or_create(model, defaults=None, **kwargs):
    defaults = defaults or {}
    try:
        instance = await model.objects.get(**kwargs)
        for key, value in defaults.items():
            setattr(instance, key, value)
        await save(instance)
        return instance, False
    except model.DoesNotExist:
        params = {**kwargs, **defaults}
        instance = await create(model, **params)
        return instance, True


async def create_instance(model_class, **kwargs):
    """
    This matches the reference in Model.save() for creating a brand new record.
    Uses the existing 'create' function to do the heavy lifting.
    """
    return await create(model_class, **kwargs)
