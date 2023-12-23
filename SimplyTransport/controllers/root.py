from litestar import Controller, get
from litestar.response import Template
from litestar.di import Provide
from advanced_alchemy.filters import LimitOffset
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.events.repo import EventRepository, provide_event_repo
from SimplyTransport.domain.events.event_types import EventType


__all__ = [
    "RootController",
]


class RootController(Controller):
    dependencies = {
        "event_repo": Provide(provide_event_repo),
    }

    @get("/")
    async def root(
        self,
        event_repo: EventRepository,
    ) -> Template:
        try:
            gtfs_updated_events = await event_repo.get_paginated_events_by_type(
                event_type=EventType.GTFS_DATABASE_UPDATED, limit_offset=LimitOffset(limit=1, offset=0)
            )
        except NotFoundError:
            gtfs_updated_event = None
        else:
            gtfs_updated_event = gtfs_updated_events[0][0]
            gtfs_updated_event.add_pretty_created_at()

        try:
            realtime_updated_events = await event_repo.get_paginated_events_by_type(
                event_type=EventType.REALTIME_DATABASE_UPDATED, limit_offset=LimitOffset(limit=1, offset=0)
            )
        except NotFoundError:
            realtime_updated_event = None
        else:
            realtime_updated_event = realtime_updated_events[0][0]
            realtime_updated_event.add_pretty_created_at()

        return Template(
            template_name="index.html",
            context={"gtfs_updated": gtfs_updated_event, "realtime_updated": realtime_updated_event},
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
