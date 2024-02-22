from litestar import Controller, Response, get
from litestar.response import Template
from litestar.di import Provide
from SimplyTransport.domain.maps.maps import Map

from ..domain.services.map_service import MapService

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
        "map": Provide(Map, sync_to_thread=False),
    }

    @get("/", cache=60)
    async def root(
        self,
        event_repo: EventRepository,
    ) -> Template:

        gtfs_updated_event = await event_repo.get_single_pretty_event_by_type(
            EventType.GTFS_DATABASE_UPDATED
        )
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
