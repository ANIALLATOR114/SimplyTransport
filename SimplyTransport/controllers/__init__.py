from litestar import Router

from . import root, agency, calendar, calendar_date, route, trip, stop, shape

__all__ = ["create_api_router", "create_views_router"]


def create_views_router() -> Router:
    return Router(
        path="/", route_handlers=[root.RootController], security=[{}], include_in_schema=False
    )


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
    calendar_date_route_handler = Router(
        path="/calendardate",
        tags=["CalendarDate"],
        security=[{}],
        route_handlers=[calendar_date.CalendarDateController],
    )

    route_route_handler = Router(
        path="/route", tags=["Route"], security=[{}], route_handlers=[route.RouteController]
    )

    trip_route_handler = Router(
        path="/trip", tags=["Trip"], security=[{}], route_handlers=[trip.TripController]
    )

    stop_route_handler = Router(
        path="/stop", tags=["Stop"], security=[{}], route_handlers=[stop.StopController]
    )

    shape_route_handler = Router(
        path="/shape", tags=["Shape"], security=[{}], route_handlers=[shape.ShapeController]
    )

    return Router(
        path="/api/v1",
        route_handlers=[
            agency_route_handler,
            calendar_route_handler,
            calendar_date_route_handler,
            route_route_handler,
            trip_route_handler,
            stop_route_handler,
            shape_route_handler,
        ],
    )
