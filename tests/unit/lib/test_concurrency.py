from unittest.mock import AsyncMock, patch

import click
import pytest
import redis.exceptions
from SimplyTransport.lib import concurrency as concurrency_mod


@pytest.mark.asyncio
async def test_concurrency_mutex_runs_when_acquired():
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.execute_command = AsyncMock(return_value=1)

    ran = False

    async def inner() -> int:
        nonlocal ran
        ran = True
        return 7

    with patch.object(concurrency_mod, "redis_factory", return_value=mock_redis):
        wrapped = concurrency_mod.concurrency(1, name="test_job")(inner)
        result = await wrapped()

    assert ran is True
    assert result == 7
    mock_redis.set.assert_called_once()
    mock_redis.execute_command.assert_called_once()
    mock_redis.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrency_mutex_skips_when_locked():
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(return_value=None)

    ran = False

    async def inner() -> None:
        nonlocal ran
        ran = True

    with patch.object(concurrency_mod, "redis_factory", return_value=mock_redis):
        wrapped = concurrency_mod.concurrency(1, name="test_job")(inner)
        result = await wrapped()

    assert ran is False
    assert result is None
    mock_redis.set.assert_called_once()
    mock_redis.execute_command.assert_not_called()
    mock_redis.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrency_semaphore_acquires_when_under_limit():
    mock_redis = AsyncMock()
    mock_redis.execute_command = AsyncMock(return_value=1)
    mock_redis.zrem = AsyncMock()

    async def inner() -> str:
        return "ok"

    with patch.object(concurrency_mod, "redis_factory", return_value=mock_redis):
        wrapped = concurrency_mod.concurrency(2, name="sem")(inner)
        result = await wrapped()

    assert result == "ok"
    mock_redis.execute_command.assert_called_once()
    mock_redis.zrem.assert_awaited_once()
    mock_redis.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrency_semaphore_skips_when_full():
    mock_redis = AsyncMock()
    mock_redis.execute_command = AsyncMock(return_value=0)

    ran = False

    async def inner() -> None:
        nonlocal ran
        ran = True

    with patch.object(concurrency_mod, "redis_factory", return_value=mock_redis):
        wrapped = concurrency_mod.concurrency(2, name="sem")(inner)
        result = await wrapped()

    assert ran is False
    assert result is None
    mock_redis.execute_command.assert_called_once()
    mock_redis.zrem.assert_not_called()
    mock_redis.aclose.assert_awaited_once()


@pytest.mark.asyncio
async def test_concurrency_redis_error_aborts():
    mock_redis = AsyncMock()
    mock_redis.set = AsyncMock(side_effect=redis.exceptions.ConnectionError("down"))

    async def inner() -> None:
        raise AssertionError("should not run")

    with patch.object(concurrency_mod, "redis_factory", return_value=mock_redis):
        wrapped = concurrency_mod.concurrency(1)(inner)
        with pytest.raises(click.Abort):
            await wrapped()

    mock_redis.aclose.assert_awaited_once()


def test_concurrency_limit_must_be_positive():
    async def inner() -> None:
        pass

    with pytest.raises(ValueError, match="limit"):
        concurrency_mod.concurrency(0)(inner)
