from litestar.config.response_cache import ResponseCacheConfig
from litestar.stores.redis import RedisStore
from redis.asyncio import Redis
from . import settings

redis = Redis(host=settings.app.REDIS_HOST, port=settings.app.REDIS_PORT, db=0)
redis_store = RedisStore(redis)
cache_config = ResponseCacheConfig(store=redis_store)
