import hashlib
import pickle
from functools import wraps
from ..core.config import get_orm_config

class CacheManager:
    def __init__(self):
        self.config = get_orm_config().cache
        if self.config.backend == 'redis':
            import redis
            self.client = redis.Redis.from_url(self.config.url)
        else:
            self.cache = {}

    def get(self, key):
        if self.config.backend == 'redis':
            value = self.client.get(key)
            return pickle.loads(value) if value else None
        return self.cache.get(key)

    def set(self, key, value, timeout=None):
        if self.config.backend == 'redis':
            self.client.set(key, pickle.dumps(value), ex=timeout or self.config.timeout)
        else:
            self.cache[key] = value

    def delete(self, key):
        if self.config.backend == 'redis':
            self.client.delete(key)
        else:
            self.cache.pop(key, None)

    def clear(self):
        if self.config.backend == 'redis':
            self.client.flushdb()
        else:
            self.cache.clear()

cache_manager = CacheManager()

def cached_query(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = hashlib.md5(f"{func.__name__}:{args}:{kwargs}".encode()).hexdigest()
        result = cache_manager.get(key)
        if result is None:
            result = func(*args, **kwargs)
            cache_manager.set(key, result)
        return result
    return wrapper


if __name__ == '__main__':
    # Usage
    @cached_query
    def get_user_by_id(user_id):
        return User.objects.get(id=user_id)
