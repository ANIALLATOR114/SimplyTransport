from litestar import Router
from litestar.exceptions import HTTPException

from SimplyTransport.lib import exception_handlers
from SimplyTransport.lib import settings

from . import root, search, realtime, events, maps
from .api import (
    agency,
    calendar,
    calendar_date,
    route,
    trip,
    stop,
    shape,
    stoptime,
    realtime as realtimeAPI,
    schedule as scheduleAPI,
    map,
)

__all__ = ["create_api_router", "create_views_router"]


def create_views_router() -> Router:
    root_route_handler = Router(
        path="/", route_handlers=[root.RootController], security=[{}], include_in_schema=False
    )

    search_route_handler = Router(
        path="/search",
        route_handlers=[search.SearchController],
        security=[{}],
        include_in_schema=False,
    )

    realtime_route_handler = Router(
        path="/realtime",
        route_handlers=[realtime.RealtimeController],
        security=[{}],
        include_in_schema=False,
    )

    events_route_handler = Router(
        path="/events",
        route_handlers=[events.EventsController],
        security=[{}],
        include_in_schema=False,
    )

    maps_route_handler = Router(
        path="/maps",
        route_handlers=[maps.MapsController],
        security=[{}],
        include_in_schema=False,
    )

    return Router(
        path="/",
        route_handlers=[
            root_route_handler,
            search_route_handler,
            realtime_route_handler,
            events_route_handler,
            maps_route_handler,
        ],
    )


def create_api_router() -> Router:
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

    stop_time_handler = Router(
        path="/stoptime",
        tags=["StopTime"],
        security=[{}],
        route_handlers=[stoptime.StopTimeController],
    )

    realtime_route_handler = Router(
        path="/realtime", tags=["Realtime"], security=[{}], route_handlers=[realtimeAPI.RealtimeController]
    )

    schedule_route_handler = Router(
        path="/schedule", tags=["Schedule"], security=[{}], route_handlers=[scheduleAPI.ScheduleController]
    )

    maps_route_handler = Router(path="/map", tags=["Map"], security=[{}], route_handlers=[map.MapController])

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
            stop_time_handler,
            realtime_route_handler,
            schedule_route_handler,
            maps_route_handler,
        ],
    )
