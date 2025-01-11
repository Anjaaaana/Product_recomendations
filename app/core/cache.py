from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def init_cache():
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
