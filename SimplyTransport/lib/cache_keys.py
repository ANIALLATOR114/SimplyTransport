from collections.abc import Callable
from enum import StrEnum

from litestar import Request


class CacheKeys:
    class Meta(StrEnum):
        ALL_KEYS = "*"

    class StopMaps(StrEnum):
        STOP_MAP_KEY_TEMPLATE = "stop_map:{stop_id}"
        STOP_MAP_DELETE_ALL_KEY_TEMPLATE = "*stop_map:*"
        STOP_MAP_DELETE_KEY_TEMPLATE = "*stop_map:{stop_id}"

    class RouteMaps(StrEnum):
        ROUTE_MAP_KEY_TEMPLATE = "route_map:{route_id}:{direction}"
        ROUTE_MAP_DELETE_ALL_KEY_TEMPLATE = "*route_map:*"
        ROUTE_MAP_DELETE_KEY_TEMPLATE = "*route_map:{route_id}:*"

    class Schedules(StrEnum):
        SCHEDULE_KEY_TEMPLATE = "schedule:{stop_id}:{day}"
        SCHEDULE_DELETE_ALL_KEY_TEMPLATE = "*schedule:*"
        SCHEDULE_DELETE_KEY_TEMPLATE = "*schedule:{stop_id}:*"

    class RealTime(StrEnum):
        REALTIME_STOP_KEY_TEMPLATE = "realtime:stop:{stop_id}"
        REALTIME_STOP_DELETE_ALL_KEY_TEMPLATE = "*realtime:stop:*"
        REALTIME_STOP_DELETE_KEY_TEMPLATE = "*realtime:stop:{stop_id}"
        REALTIME_TRIP_KEY_TEMPLATE = "realtime:trip:{trip_id}"
        REALTIME_TRIP_DELETE_ALL_KEY_TEMPLATE = "*realtime:trip:*"
        REALTIME_TRIP_DELETE_KEY_TEMPLATE = "*realtime:trip:{trip_id}"

    class StaticMaps(StrEnum):
        STATIC_MAP_AGENCY_ROUTE_KEY_TEMPLATE = "static_map:agency:route:{agency_id}"
        STATIC_MAP_AGENCY_ROUTE_DELETE_ALL_KEY_TEMPLATE = "*static_map:agency:route:*"
        STATIC_MAP_AGENCY_ROUTE_DELETE_KEY_TEMPLATE = "*static_map:agency:route:{agency_id}"
        STATIC_MAP_STOP_KEY_TEMPLATE = "static_map:stop:{map_type}"
        STATIC_MAP_STOP_DELETE_ALL_KEY_TEMPLATE = "*static_map:stop:*"
        STATIC_MAP_STOP_DELETE_KEY_TEMPLATE = "*static_map:stop:{map_type}"

    class Delays(StrEnum):
        DELAYS_AGGREGATED_SPECIFIC_KEY_TEMPLATE = (
            "delays_aggregated_specific:{stop_id}:{route_code}:{scheduled_time}"
        )
        DELAYS_AGGREGATED_SPECIFIC_DELETE_ALL_KEY_TEMPLATE = "*delays_aggregated_specific:*"
        DELAYS_AGGREGATED_SPECIFIC_DELETE_KEY_TEMPLATE = (
            "*delays_aggregated_specific:{stop_id}:{route_code}:*"
        )
        DELAYS_SPECIFIC_KEY_TEMPLATE = "delays_specific:{stop_id}:{route_code}:{scheduled_time}"
        DELAYS_SPECIFIC_DELETE_ALL_KEY_TEMPLATE = "*delays_specific:*"
        DELAYS_SPECIFIC_DELETE_KEY_TEMPLATE = "*delays_specific:{stop_id}:{route_code}:*"
        DELAYS_SPECIFIC_SLIM_KEY_TEMPLATE = "delays_specific_slim:{stop_id}:{route_code}:{scheduled_time}"
        DELAYS_SPECIFIC_SLIM_DELETE_ALL_KEY_TEMPLATE = "*delays_specific_slim:*"
        DELAYS_SPECIFIC_SLIM_DELETE_KEY_TEMPLATE = "*delays_specific_slim:{stop_id}:{route_code}:*"
        DELAYS_AGGREGATED_ROUTE_KEY_TEMPLATE = "delays_aggregated_route:{route_code}"
        DELAYS_AGGREGATED_ROUTE_DELETE_ALL_KEY_TEMPLATE = "*delays_aggregated_route:*"
        DELAYS_AGGREGATED_ROUTE_DELETE_KEY_TEMPLATE = "*delays_aggregated_route:{route_code}"
        DELAYS_HTML_ROUTE_KEY_TEMPLATE = "delays_html_route:{route_code}"
        DELAYS_HTML_ROUTE_DELETE_ALL_KEY_TEMPLATE = "*delays_html_route:*"
        DELAYS_HTML_ROUTE_DELETE_KEY_TEMPLATE = "*delays_html_route:{route_code}"


def key_builder_from_path(template: StrEnum, *args) -> Callable[[Request], str]:
    """
    Builds a cache key based on the provided template and IDs.

    Args:
        template (str): The template string containing the placeholders for the IDs.
        *args: Variable number of path parameter names.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """

    def _key_builder(request: Request) -> str:
        return template.value.format(**{arg: request.path_params.get(arg) for arg in args})

    return _key_builder


def key_builder_from_query(template: StrEnum, *args) -> Callable[[Request], str]:
    """
    Builds a cache key based on the provided template and query parameters.

    Args:
        template (CacheKeys): The template for the cache key.
        *args: Variable number of query parameter names.

    Returns:
        callable: A function that takes a request object and returns the cache key.
    """

    def _key_builder(request: Request) -> str:
        return template.value.format(**{arg: request.query_params.get(arg) for arg in args})

    return _key_builder


def key_builder_from_path_and_query(
    template: StrEnum, path_args: list[str] | None = None, query_args: list[str] | None = None
) -> Callable[[Request], str]:
    """
    Builds a cache key based on the provided template and IDs.

    Args:
        template (str): The template string containing the placeholders for the IDs.
        path_args (list[str]): The names of the path parameters.
        query_args (list[str]): The names of the query parameters.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """
    if path_args is None:
        path_args = []
    if query_args is None:
        query_args = []

    def _key_builder(request: Request) -> str:
        params = {arg: request.path_params.get(arg) for arg in path_args}
        params.update({arg: request.query_params.get(arg) for arg in query_args})
        return template.value.format(**params)

    return _key_builder


def key_builder_from_header(template: StrEnum, *args) -> Callable[[Request], str]:
    """
    Builds a cache key based on the provided template and header parameters.

    Args:
        template (CacheKeys): The template for the cache key.
        *args: Variable number of header parameter names.

    Returns:
        callable: A function that takes a request object and returns the cache key.
    """

    def _key_builder(request: Request) -> str:
        return template.value.format(**{arg: request.headers.get(arg) for arg in args})

    return _key_builder
