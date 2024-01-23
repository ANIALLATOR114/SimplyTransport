from asyncio import gather

from litestar import Controller, get
from litestar.response import Template
from litestar.di import Provide
from advanced_alchemy.filters import LimitOffset
from advanced_alchemy import NotFoundError

from ..domain.events.repo import EventRepository, provide_event_repo
from ..domain.events.event_types import EventType
from ..domain.events.model import EventModel


__all__ = [
    "RootController",
]


async def get_single_pretty_event_by_type(
    event_repo: EventRepository, event_type: EventType
) -> EventModel | None:
    try:
        events = await event_repo.get_paginated_events_by_type(
            event_type=event_type, limit_offset=LimitOffset(limit=1, offset=0)
        )
    except NotFoundError:
        return None
    else:
        event = events[0][0]
        return event.add_pretty_created_at()


class RootController(Controller):
    dependencies = {
        "event_repo": Provide(provide_event_repo),
    }

    @get("/")
    async def root(
        self,
        event_repo: EventRepository,
    ) -> Template:
        (
            gtfs_updated_event,
            realtime_updated_event,
            vehicles_updated_event,
            stop_features_updated_event,
        ) = await gather(
            get_single_pretty_event_by_type(event_repo, EventType.GTFS_DATABASE_UPDATED),
            get_single_pretty_event_by_type(event_repo, EventType.REALTIME_DATABASE_UPDATED),
            get_single_pretty_event_by_type(event_repo, EventType.REALTIME_VEHICLES_DATABASE_UPDATED),
            get_single_pretty_event_by_type(event_repo, EventType.STOP_FEATURES_DATABASE_UPDATED),
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
        return "OK"

    @get("/stops")
    async def stop(self) -> Template:
        return Template("gtfs_search/stop_search.html")

    @get("/routes")
    async def route(self) -> Template:
        return Template("gtfs_search/route_search.html")
