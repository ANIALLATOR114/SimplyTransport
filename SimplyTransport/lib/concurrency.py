"""
Redis-backed concurrency limiting for async callables (e.g. CLI jobs under asyncio.run).
"""

import functools
import uuid
from collections.abc import Awaitable, Callable
from typing import ParamSpec, TypeVar

import click
import redis.exceptions as redis_exc
from redis.asyncio import Redis

from . import settings
from .cache import redis_factory
from .logging.logging import provide_logger

P = ParamSpec("P")
R = TypeVar("R")

logger = provide_logger(__name__)

_MUTEX_RELEASE_LUA = """
if redis.call('GET', KEYS[1]) == ARGV[1] then
  return redis.call('DEL', KEYS[1])
else
  return 0
end
"""

_SEMAPHORE_ACQUIRE_LUA = """
local zkey = KEYS[1]
local limit = tonumber(ARGV[1])
local ttl_ms = tonumber(ARGV[2])
local token = ARGV[3]

local t = redis.call('TIME')
local now_ms = tonumber(t[1]) * 1000 + math.floor(tonumber(t[2]) / 1000)

redis.call('ZREMRANGEBYSCORE', zkey, '-inf', now_ms)
local count = redis.call('ZCARD', zkey)
if count < limit then
  local lease_until = now_ms + ttl_ms
  redis.call('ZADD', zkey, lease_until, token)
  return 1
else
  return 0
end
"""


async def _acquire_mutex(redis: Redis, key: str, ttl_ms: int) -> str | None:
    token = str(uuid.uuid4())
    acquired = await redis.set(key, token, nx=True, px=ttl_ms)
    if acquired:
        return token
    return None


async def _release_mutex(redis: Redis, key: str, token: str) -> None:
    # execute_command: correct runtime API; redis.eval() stubs use *keys_and_args: list (invalid for pyright).
    await redis.execute_command("EVAL", _MUTEX_RELEASE_LUA, 1, key, token)


async def _acquire_semaphore(redis: Redis, key: str, limit: int, ttl_ms: int) -> str | None:
    token = str(uuid.uuid4())
    result = await redis.execute_command(
        "EVAL", _SEMAPHORE_ACQUIRE_LUA, 1, key, str(limit), str(ttl_ms), token
    )
    if result is not None and int(result) == 1:
        return token
    return None


async def _release_semaphore(redis: Redis, key: str, token: str) -> None:
    await redis.zrem(key, token)


def concurrency(
    limit: int,
    *,
    name: str | None = None,
    ttl_seconds: int = 3600,
    skip_log: str | None = None,
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R | None]]]:
    """
    Limit concurrent runs of an async function using Redis. If the limit is reached, the
    call returns None without invoking the wrapped function.

    Use below @make_sync so asyncio.run executes acquire, the job, and release together.

    Args:
        limit: Maximum concurrent holders (1 = mutual exclusion).
        name: Redis key suffix; defaults to the wrapped function's __name__.
        ttl_seconds: Lock / lease TTL; must exceed worst-case runtime or another process
            may acquire while this job is still running.
        skip_log: Optional extra text appended to the warning when skipping.
    """
    if limit < 1:
        raise ValueError("limit must be >= 1")

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R | None]]:
        lock_name = name or func.__name__
        key = f"{settings.app.NAME}:concurrency:{lock_name}"

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
            client: Redis | None = None
            token: str | None = None
            try:
                client = redis_factory()
                ttl_ms = ttl_seconds * 1000
                if limit == 1:
                    token = await _acquire_mutex(client, key, ttl_ms)
                else:
                    token = await _acquire_semaphore(client, key, limit, ttl_ms)

                if token is None:
                    msg = f"Skipped {lock_name}: concurrency limit reached ({limit})"
                    if skip_log:
                        msg = f"{msg} — {skip_log}"
                    logger.warning(msg)
                    return None

                return await func(*args, **kwargs)

            except redis_exc.RedisError as e:
                logger.exception("Redis concurrency control failed")
                raise click.Abort() from e
            finally:
                if client is not None:
                    try:
                        if token is not None:
                            if limit == 1:
                                await _release_mutex(client, key, token)
                            else:
                                await _release_semaphore(client, key, token)
                    except redis_exc.RedisError:
                        logger.exception("Failed to release concurrency lock")
                    await client.aclose()

        return wrapper

    return decorator
