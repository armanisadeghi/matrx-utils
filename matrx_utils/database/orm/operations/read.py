from ..query.builder import QueryBuilder


async def get(model, *args, **kwargs):
    return await QueryBuilder(model).filter(*args, **kwargs).get()


async def filter(model, *args, **kwargs):
    return QueryBuilder(model).filter(*args, **kwargs)


async def exclude(model, *args, **kwargs):
    return QueryBuilder(model).exclude(*args, **kwargs)


async def all(model):
    return QueryBuilder(model)


async def count(model, *args, **kwargs):
    return await QueryBuilder(model).filter(*args, **kwargs).count()


async def exists(model, *args, **kwargs):
    return await QueryBuilder(model).filter(*args, **kwargs).exists()


async def first(model, *args, **kwargs):
    return await QueryBuilder(model).filter(*args, **kwargs).first()


async def last(model, *args, **kwargs):
    return await QueryBuilder(model).filter(*args, **kwargs).last()


async def values(model, *fields, **kwargs):
    return await QueryBuilder(model).filter(**kwargs).values(*fields)


async def values_list(model, *fields, flat=False, **kwargs):
    return await QueryBuilder(model).filter(**kwargs).values_list(*fields, flat=flat)


async def in_bulk(model, id_list, field="id"):
    objects = await QueryBuilder(model).filter(**{f"{field}__in": id_list}).all()
    # Turn that list into a dict
    return {getattr(obj, field): obj for obj in objects}


async def iterator(model, chunk_size=2000, **kwargs):
    qb = QueryBuilder(model).filter(**kwargs)
    start, end = 0, chunk_size
    while True:
        chunk = await qb[start:end]
        if not chunk:
            break
        for item in chunk:
            yield item
        start, end = end, end + chunk_size
