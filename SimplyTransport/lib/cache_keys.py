from enum import Enum

from litestar import Request

class CacheKeys(Enum):
    ALL_KEYS = '*'

    # Stop Maps
    STOP_MAP_KEY_TEMPLATE = 'stop_map:{stop_id}'
    STOP_MAP_DELETE_ALL_KEY_TEMPLATE = '*stop_map:*'
    STOP_MAP_DELETE_KEY_TEMPLATE = '*stop_map:{stop_id}'


def key_builder_from_path(template: CacheKeys, id: str):
    """
    Builds a cache key based on the provided template and ID.

    Args:
        template (str): The template string containing the placeholder for the ID.
        id (str): The name of the ID parameter.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """
    def _key_builder(request: Request):
        return template.value.format(**{id: request.path_params.get(id)})
    return _key_builder


def key_builder_from_query(template: CacheKeys, id: str):
    """
    Builds a cache key based on the provided template and ID.

    Args:
        template (str): The template string containing the placeholder for the ID.
        id (str): The name of the ID parameter.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """
    def _key_builder(request: Request):
        return template.value.format(**{id: request.query_params.get(id)})
    return _key_builder


def key_builder_from_header(template: CacheKeys, id: str):
    """
    Builds a cache key based on the provided template and ID.

    Args:
        template (str): The template string containing the placeholder for the ID.
        id (str): The name of the ID parameter.

    Returns:
        callable: A function that takes a `Request` object and returns the cache key.
    """
    def _key_builder(request: Request):
        return template.value.format(**{id: request.headers.get(id)})
    return _key_builder