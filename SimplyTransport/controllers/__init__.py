from litestar import Router

from . import root, sample_api

__all__ = ["create_api_router", "create_views_router"]


def create_views_router() -> Router:
    return Router(path="/", route_handlers=[root.RootController], tags=["public"], security=[{}])


def create_api_router() -> Router:
    return Router(
        path="/api/v1",
        route_handlers=[sample_api.SampleController],
    )
