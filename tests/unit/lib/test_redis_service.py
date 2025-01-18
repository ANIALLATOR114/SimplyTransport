from enum import StrEnum
from unittest.mock import AsyncMock

import pytest
from redis.asyncio import Redis
from SimplyTransport.lib.cache import (
    CacheKeys,
    RedisService,
    redis_factory,
    redis_service_cache_config_factory,
    redis_store_factory,
)


@pytest.fixture
def mock_redis() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def redis_service(mock_redis: AsyncMock) -> RedisService:
    service = RedisService()
    service.redis = mock_redis
    return service


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "keys, pattern, expected_calls",
    [
        (["key1", "key2"], CacheKeys.StopMaps.STOP_MAP_DELETE_KEY_TEMPLATE, 1),
        ([], CacheKeys.StopMaps.STOP_MAP_DELETE_KEY_TEMPLATE, 0),
        (["key1", "key2"], CacheKeys.Meta.ALL_KEYS, 1),
    ],
)
async def test_delete_keys(
    keys: list, pattern: StrEnum, expected_calls: int, redis_service: RedisService, mock_redis: Redis
):
    # Arrange
    mock_redis.keys.return_value = keys

    # Act
    await redis_service.delete_keys(pattern)

    # Assert
    mock_redis.keys.assert_called_once_with(pattern.value)
    assert mock_redis.delete.call_count == expected_calls


@pytest.mark.asyncio
async def test_delete_key(redis_service: RedisService, mock_redis: Redis):
    await redis_service.delete_key(CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE, "stop_id")
    mock_redis.delete.assert_called_once_with(
        CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE.value.format(stop_id="stop_id")
    )


@pytest.mark.asyncio
async def test_delete_all_keys(redis_service: RedisService, mock_redis: Redis):
    mock_redis.keys.return_value = ["key1", "key2", "key3"]
    await redis_service.delete_all_keys()
    mock_redis.delete.assert_called_once_with("key1", "key2", "key3")


@pytest.mark.asyncio
async def test_delete_all_no_keys_present(redis_service: RedisService, mock_redis: Redis):
    await redis_service.delete_all_keys()
    mock_redis.delete.assert_called_once_with()


@pytest.mark.asyncio
async def test_count_all_keys(redis_service: RedisService, mock_redis: Redis):
    mock_redis.keys.return_value = ["key1", "key2", "key3"]
    count = await redis_service.count_all_keys()
    assert count == 3


@pytest.mark.asyncio
async def test_set(redis_service: RedisService, mock_redis: Redis):
    await redis_service.set(CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE, "stop_id", "value")
    mock_redis.set.assert_called_once_with(
        CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE.value.format(stop_id="stop_id"), "value", ex=60
    )


def test_redis_factory():
    redis = redis_factory()
    assert redis.connection_pool.connection_kwargs["host"] == "127.0.0.1"
    assert redis.connection_pool.connection_kwargs["port"] == 6379
    assert redis.connection_pool.connection_kwargs["db"] == 0


def test_redis_service_cache_config_factory():
    config = redis_service_cache_config_factory()
    assert config.default_expiration == 60


def test_redis_store_factory():
    redis_store = redis_store_factory("test_name")
    assert redis_store.namespace is not None and "test_name" in redis_store.namespace
