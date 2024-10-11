from litestar import Router

from . import root, search, realtime, events, maps, stats
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
    statistics,
    events as eventsAPI,
    delays,
)
from ..lib.openapi.tags import Tags

__all__ = ["create_api_router", "create_views_router"]


def create_views_router() -> Router:
    root_route_handler = Router(path="/", route_handlers=[root.RootController], include_in_schema=False)

    search_route_handler = Router(
        path="/search",
        route_handlers=[search.SearchController],
        include_in_schema=False,
    )

    realtime_route_handler = Router(
        path="/realtime",
        route_handlers=[realtime.RealtimeController],
        include_in_schema=False,
    )

    events_route_handler = Router(
        path="/events",
        route_handlers=[events.EventsController],
        include_in_schema=False,
    )

    maps_route_handler = Router(
        path="/maps",
        route_handlers=[maps.MapsController],
        include_in_schema=False,
    )

    static_route_handler = Router(
        path="/stats",
        route_handlers=[stats.StatsController],
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
            static_route_handler,
        ],
    )


def create_api_router() -> Router:
    tags = Tags()

    agency_route_handler = Router(
        path="/agency", tags=[tags.AGENCY.name], route_handlers=[agency.AgencyController]
    )
    calendar_route_handler = Router(
        path="/calendar",
        tags=[tags.CALENDAR.name],
        route_handlers=[calendar.CalendarController],
    )
    calendar_date_route_handler = Router(
        path="/calendardate",
        tags=[tags.CALENDAR_DATE.name],
        route_handlers=[calendar_date.CalendarDateController],
    )

    route_route_handler = Router(
        path="/route", tags=[tags.ROUTE.name], route_handlers=[route.RouteController]
    )

    trip_route_handler = Router(path="/trip", tags=[tags.TRIP.name], route_handlers=[trip.TripController])

    stop_route_handler = Router(path="/stop", tags=[tags.STOP.name], route_handlers=[stop.StopController])

    shape_route_handler = Router(
        path="/shape", tags=[tags.SHAPE.name], route_handlers=[shape.ShapeController]
    )

    stop_time_handler = Router(
        path="/stoptime",
        tags=[tags.STOP_TIME.name],
        route_handlers=[stoptime.StopTimeController],
    )

    realtime_route_handler = Router(
        path="/realtime",
        tags=[tags.REALTIME.name],
        route_handlers=[realtimeAPI.RealtimeController],
    )

    schedule_route_handler = Router(
        path="/schedule",
        tags=[tags.SCHEDULE.name],
        route_handlers=[scheduleAPI.ScheduleController],
    )

    maps_route_handler = Router(path="/map", tags=[tags.MAP.name], route_handlers=[map.MapController])

    statistics_route_handler = Router(
        path="/statistics",
        tags=[tags.STATISTICS.name],
        route_handlers=[statistics.StatisticsController],
    )

    events_route_handler = Router(
        path="/events",
        tags=[tags.EVENTS.name],
        route_handlers=[eventsAPI.EventsController],
    )

    delays_route_handler = Router(
        path="/delays",
        tags=[tags.DELAYS.name],
        route_handlers=[delays.DelaysController],
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
            stop_time_handler,
            realtime_route_handler,
            schedule_route_handler,
            maps_route_handler,
            statistics_route_handler,
            events_route_handler,
            delays_route_handler,
        ],
    )
