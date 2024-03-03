from enum import Enum

from litestar import Request


class CacheKeys(Enum):
    ALL_KEYS = "*"

    # Stop Maps
    STOP_MAP_KEY_TEMPLATE = "stop_map:{stop_id}"
    STOP_MAP_DELETE_ALL_KEY_TEMPLATE = "*stop_map:*"
    STOP_MAP_DELETE_KEY_TEMPLATE = "*stop_map:{stop_id}"

    # Schedules
    SCHEDULE_KEY_TEMPLATE = "schedule:{stop_id}:{day}"
    SCHEDULE_DELETE_ALL_KEY_TEMPLATE = "*schedule:*"
    SCHEDULE_DELETE_KEY_TEMPLATE = "*schedule:{stop_id}:*"


def key_builder_from_path(template: CacheKeys, *args):
    """
    Builds a cache key based on the provided template and IDs.

    Args:
        template (str): The template string containing the placeholders for the IDs.
        *args: Variable number of path parameter names.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """

    def _key_builder(request: Request):
        return template.value.format(**{arg: request.path_params.get(arg) for arg in args})

    return _key_builder


def key_builder_from_query(template: CacheKeys, *args):
    """
    Builds a cache key based on the provided template and query parameters.

    Args:
        template (CacheKeys): The template for the cache key.
        *args: Variable number of query parameter names.

    Returns:
        callable: A function that takes a request object and returns the cache key.
    """

    def _key_builder(request: Request):
        return template.value.format(**{arg: request.query_params.get(arg) for arg in args})

    return _key_builder


def key_builder_from_path_and_query(
    template: CacheKeys, path_args: list[str] = [], query_args: list[str] = []
):
    """
    Builds a cache key based on the provided template and IDs.

    Args:
        template (str): The template string containing the placeholders for the IDs.
        path_args (list[str]): The names of the path parameters.
        query_args (list[str]): The names of the query parameters.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """

    def _key_builder(request: Request):
        params = {arg: request.path_params.get(arg) for arg in path_args}
        params.update({arg: request.query_params.get(arg) for arg in query_args})
        return template.value.format(**params)

    return _key_builder


def key_builder_from_header(template: CacheKeys, *args):
    """
    Builds a cache key based on the provided template and header parameters.

    Args:
        template (CacheKeys): The template for the cache key.
        *args: Variable number of header parameter names.

    Returns:
        callable: A function that takes a request object and returns the cache key.
    """

    def _key_builder(request: Request):
        return template.value.format(**{arg: request.headers.get(arg) for arg in args})

    return _key_builder
