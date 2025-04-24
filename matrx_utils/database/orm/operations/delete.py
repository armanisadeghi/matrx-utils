from .update import update
from ..query.builder import QueryBuilder


async def delete(model, **kwargs):
    return await QueryBuilder(model).filter(**kwargs).delete()


async def bulk_delete(model, objects):
    if not objects:
        return 0
    ids = [obj.id for obj in objects if obj.id is not None]
    return await delete(model, id__in=ids)


async def soft_delete(model, **kwargs):
    from datetime import datetime

    return await update(model, deleted_at=datetime.now(), **kwargs)


async def restore(model, **kwargs):
    return await update(model, deleted_at=None, **kwargs)


async def purge(model, **kwargs):
    return await delete(model, deleted_at__isnull=False, **kwargs)


async def delete_instance(instance):
    model_class = instance.__class__
    pk_list = model_class._meta.primary_keys
    if not pk_list:
        raise ValueError(f"Cannot delete {model_class.__name__} with no primary key.")
    pk_name = pk_list[0]
    pk_value = getattr(instance, pk_name, None)
    if pk_value is None:
        raise ValueError(f"Cannot delete {model_class.__name__}, {pk_name} is None")

    await delete(model_class, **{pk_name: pk_value})
