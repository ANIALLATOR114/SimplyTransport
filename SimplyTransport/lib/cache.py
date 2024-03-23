from litestar.config.response_cache import ResponseCacheConfig
from litestar.stores.redis import RedisStore
from redis.asyncio import Redis

from .cache_keys import CacheKeys
from . import settings

from opentelemetry.instrumentation.redis import RedisInstrumentor

RedisInstrumentor().instrument()


def redis_factory() -> Redis:
    """
    Creates and returns a Redis instance.

    Returns:
        Redis: The Redis instance.
    """
    return Redis(host=settings.app.REDIS_HOST, port=settings.app.REDIS_PORT, db=0)


def redis_store_factory(name: str) -> RedisStore:
    """
    Factory function that creates and returns a RedisStore object.

    Returns:
        RedisStore: The created RedisStore object.
    """
    return RedisStore(redis_factory(), namespace=f"{settings.app.NAME}:{name}")


def redis_service_cache_config_factory() -> ResponseCacheConfig:
    """
    Factory function that returns a ResponseCacheConfig object for Redis service cache.

    Returns:
        ResponseCacheConfig: The cache configuration object.
    """
    return ResponseCacheConfig(default_expiration=60)


class RedisService:
    def __init__(self, default_expiration: int = 60) -> None:
        self.redis = redis_factory()
        self.default_expiration = default_expiration

    async def delete_keys(self, pattern: CacheKeys) -> None:
        """
        Delete keys from the cache based on the given pattern.

        Args:
            pattern (CacheKeys): The pattern to match the keys.

        Returns:
            None
        """
        keys = await self.redis.keys(pattern.value)
        if keys:
            await self.redis.delete(*keys)

    async def delete_key(self, template: CacheKeys, id: str) -> None:
        """
        Delete a key from the cache.

        Args:
            key (CacheKeys): The key to delete from the cache.

        Returns:
            None
        """
        key = template.value.format(**{id: id})
        await self.redis.delete(key)

    async def delete_all_keys(self) -> None:
        """
        Deletes all keys from the cache.
        """
        await self.delete_keys(CacheKeys.ALL_KEYS)

    async def count_all_keys(self) -> int:
        """
        Counts all keys in the cache.

        Returns:
            int: The number of keys in the cache.
        """
        return len(await self.redis.keys(CacheKeys.ALL_KEYS.value))

    async def set(self, template: CacheKeys, id: str, value: str, expiration: int = None) -> None:
        """
        Set a value in the cache.

        Args:
            template (CacheKeys): The cache key template.
            id (str): The identifier used in the cache key template.
            value (str): The value to be stored in the cache.
            expiration (int, optional): The expiration time in seconds. Defaults to None.
        """
        key = template.value.format(**{id: id})
        await self.redis.set(key, value, ex=expiration or self.default_expiration)


def provide_redis_service() -> RedisService:
    """
    Provides a RedisService instance.

    Returns:
        RedisService: An instance of the RedisService class.
    """
    return RedisService()
