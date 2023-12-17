from litestar import Controller, get
from litestar.response import Template
from litestar.di import Provide
from litestar.params import Parameter
from litestar.exceptions import ValidationException
from advanced_alchemy.filters import LimitOffset

from SimplyTransport.domain.events.repo import EventRepository, provide_event_repo
from SimplyTransport.domain.events.event_types import EventType


__all__ = [
    "EventsController",
]


class EventsController(Controller):

    dependencies = {
        "event_repo": Provide(provide_event_repo),
    }
    
    @get("/")
    async def root(self) -> Template:
        event_types  = [event_type.value for event_type in EventType.__members__.values()]
        event_types.insert(0, "all.event.types")

        return Template(template_name="events/events_main.html", context={"event_types": event_types})
    
    @get("/search")
    async def search(self, event_repo: EventRepository, limit_offset: LimitOffset, type: str | None = Parameter(
            query="type", required=False, description="Search events by type"
        ),sort: str | None = Parameter(
            query="sort", required=False, description="Sort events ascending or descending by creation time"
        )) -> Template:

        if sort is None:
            sort = "desc"

        if type is None or type == "all.event.types":
            type = "all.event.types"
            events = await event_repo.get_paginated_events(limit_offset, order=sort)
        else:
            if type not in [event_type.value for event_type in EventType.__members__.values()]:
                raise ValidationException("Invalid event type")
        
            events = await event_repo.get_paginated_events_by_type(type, limit_offset, order=sort)

        events = [event.add_pretty_created_at() for event in events]

        return Template(template_name="events/list_of_events.html", context={"events": events, "type": type, "sort": sort})