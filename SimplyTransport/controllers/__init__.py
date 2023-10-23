from litestar import Router

from . import root, sample_api, agency, calendar

__all__ = ["create_api_router", "create_views_router"]


def create_views_router() -> Router:
    return Router(path="/", route_handlers=[root.RootController], security=[{}])


def create_api_router() -> Router:
    # This is an example of how to create a router with a subpath
    # This generates /api/v1/agency/...
    agency_route_handler = Router(
        path="/agency", tags=["Agency"], security=[{}], route_handlers=[agency.AgencyController]
    )
    calendar_route_handler = Router(
        path="/calendar",
        tags=["Calendar"],
        security=[{}],
        route_handlers=[calendar.CalendarController],
    )

    return Router(
        path="/api/v1",
        route_handlers=[
            sample_api.SampleController,
            agency_route_handler,
            calendar_route_handler,
        ],
    )
