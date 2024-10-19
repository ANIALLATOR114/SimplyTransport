from unittest.mock import AsyncMock, PropertyMock
from litestar import Request
from SimplyTransport.lib.cache_keys import (
    CacheKeys,
    key_builder_from_header,
    key_builder_from_path,
    key_builder_from_path_and_query,
    key_builder_from_query,
)


def test_key_builder_from_path():
    template = CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE
    key_builder = key_builder_from_path(template, "stop_id")
    request = AsyncMock(spec=Request)
    type(request).path_params = PropertyMock(return_value={"stop_id": "123"})

    assert key_builder(request) == "stop_map:123"


def test_key_builder_from_path_with_multiple_args():
    template = CacheKeys.Schedules.SCHEDULE_KEY_TEMPLATE
    key_builder = key_builder_from_path(template, "stop_id", "day")
    request = AsyncMock(spec=Request)
    type(request).path_params = PropertyMock(return_value={"stop_id": "123", "day": "1"})

    assert key_builder(request) == "schedule:123:1"


def test_key_builder_from_path_with_missing_args():
    template = CacheKeys.Schedules.SCHEDULE_KEY_TEMPLATE
    key_builder = key_builder_from_path(template, "stop_id", "day")
    request = AsyncMock(spec=Request)
    type(request).path_params = PropertyMock(return_value={"stop_id": "123"})

    assert key_builder(request) == "schedule:123:None"


def test_key_builder_from_query():
    template = CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE
    key_builder = key_builder_from_query(template, "stop_id")
    request = AsyncMock(spec=Request)
    type(request).query_params = PropertyMock(return_value={"stop_id": "123"})

    assert key_builder(request) == "stop_map:123"


def test_key_builder_from_query_with_multiple_args():
    template = CacheKeys.Schedules.SCHEDULE_KEY_TEMPLATE
    key_builder = key_builder_from_query(template, "stop_id", "day")
    request = AsyncMock(spec=Request)
    type(request).query_params = PropertyMock(return_value={"stop_id": "123", "day": "1"})

    assert key_builder(request) == "schedule:123:1"


def test_key_builder_from_query_with_missing_args():
    template = CacheKeys.Schedules.SCHEDULE_KEY_TEMPLATE
    key_builder = key_builder_from_query(template, "stop_id", "day")
    request = AsyncMock(spec=Request)
    type(request).query_params = PropertyMock(return_value={"stop_id": "123"})

    assert key_builder(request) == "schedule:123:None"


def test_key_builder_from_path_and_query():
    template = CacheKeys.Schedules.SCHEDULE_KEY_TEMPLATE
    key_builder = key_builder_from_path_and_query(template, path_args=["stop_id"], query_args=["day"])
    request = AsyncMock(spec=Request)
    type(request).path_params = PropertyMock(return_value={"stop_id": "123"})
    type(request).query_params = PropertyMock(return_value={"day": "1"})

    assert key_builder(request) == "schedule:123:1"


def test_key_builder_from_path_and_query_with_missing_args():
    template = CacheKeys.Schedules.SCHEDULE_KEY_TEMPLATE
    key_builder = key_builder_from_path_and_query(template, path_args=["stop_id"], query_args=["day"])
    request = AsyncMock(spec=Request)
    type(request).path_params = PropertyMock(return_value={"stop_id": "123"})
    type(request).query_params = PropertyMock(return_value={})

    assert key_builder(request) == "schedule:123:None"


def test_key_builder_from_header():
    template = CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE
    key_builder = key_builder_from_header(template, "stop_id")
    request = AsyncMock(spec=Request)
    type(request).headers = PropertyMock(return_value={"stop_id": "123"})

    assert key_builder(request) == "stop_map:123"


def test_key_builder_from_header_with_missing_args():
    template = CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE
    key_builder = key_builder_from_header(template, "stop_id")
    request = AsyncMock(spec=Request)
    type(request).headers = PropertyMock(return_value={})

    assert key_builder(request) == "stop_map:None"
