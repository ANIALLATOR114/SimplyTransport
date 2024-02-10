from litestar import Controller, Response, get
from litestar.response import Template
from litestar.di import Provide

from SimplyTransport.domain.maps.polylines import PolyLineColors, RoutePolyLine

from ..domain.services.mapservice import MapService
from ..domain.maps.markers import BusMarker, MarkerColors, StopMarker

from ..domain.events.repo import EventRepository, provide_event_repo
from ..domain.events.event_types import EventType
from litestar.exceptions import HTTPException
from ..lib.db.services import test_database_connection
from ..lib.logging import logger


__all__ = [
    "RootController",
]


class RootController(Controller):
    dependencies = {
        "event_repo": Provide(provide_event_repo),
        "map_service": Provide(MapService, sync_to_thread=False),
    }

    @get("/")
    async def root(
        self,
        event_repo: EventRepository,
    ) -> Template:

        gtfs_updated_event = await event_repo.get_single_pretty_event_by_type(EventType.GTFS_DATABASE_UPDATED)
        realtime_updated_event = await event_repo.get_single_pretty_event_by_type(
            EventType.REALTIME_DATABASE_UPDATED
        )
        vehicles_updated_event = await event_repo.get_single_pretty_event_by_type(
            EventType.REALTIME_VEHICLES_DATABASE_UPDATED
        )
        stop_features_updated_event = await event_repo.get_single_pretty_event_by_type(
            EventType.STOP_FEATURES_DATABASE_UPDATED
        )

        return Template(
            template_name="index.html",
            context={
                "gtfs_updated": gtfs_updated_event,
                "realtime_updated": realtime_updated_event,
                "vehicles_updated": vehicles_updated_event,
                "stop_features_updated": stop_features_updated_event,
            },
        )

    @get("/about")
    async def about(self) -> Template:
        return Template(template_name="about.html")

    @get("/apidocs")
    async def api_docs(self) -> Template:
        return Template(template_name="api_docs.html")

    @get("/healthcheck")
    async def healthcheck(self) -> str:
        try:
            test_database_connection()
        except Exception as e:
            logger.error("Database connection refused on healthcheck", exc_info=e)
            raise HTTPException(status_code=500)
        return "OK"

    @get("/exception")
    async def exception(self) -> Response:
        raise HTTPException(status_code=500, detail="Test exception")

    @get("/stops")
    async def stop(self) -> Template:
        return Template("gtfs_search/stop_search.html")

    @get("/routes")
    async def route(self) -> Template:
        return Template("gtfs_search/route_search.html")

    @get("/test/map")
    async def map(self, map_service: MapService) -> Template:
        map_service.setup_defaults()
        marker1 = StopMarker("Test Stop", "123", "TST", 53.0, -7.0, color=MarkerColors.RED)
        marker1.add_to(map_service.map, type_of_marker="circle")

        marker2 = StopMarker("Test Stop 2", "124", "TST2", 53.1, -7.1, create_links=False)
        marker2.add_to(map_service.map, type_of_marker="regular")

        route1 = RoutePolyLine(
            "1", "Test Route", "Test Operator", [(53.0, -7.0), (53.1, -7.1)], route_color=PolyLineColors.BLUE
        )
        route1.add_to(map_service.map)

        bus1 = BusMarker("Test Bus", "1", "Test Operator", 53.2, -7.2, color=MarkerColors.GREEN)
        bus1.add_to(map_service.map)

        return Template(
            template_name="map.html",
            context={
                "map": map_service.render(),
            },
        )
