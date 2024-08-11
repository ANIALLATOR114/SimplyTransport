from typing import Literal
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter
from advanced_alchemy.filters import LimitOffset

from SimplyTransport.domain.events.event_types import EventType
from SimplyTransport.domain.events.model import Event, EventsWithTotal

from ...domain.events.repo import EventRepository, provide_event_repo

__all__ = ["EventsController"]


class EventsController(Controller):
    dependencies = {"repo": Provide(provide_event_repo)}

    @get(
        "/",
        summary="Get paginated events",
        raises=[NotFoundException],
    )
    async def get_events(
        self,
        repo: EventRepository,
        limit_offset: LimitOffset,
        order: Literal["desc", "asc"] = Parameter(
            required=False, description="Order by descending or ascending", default="desc"
        ),
    ) -> EventsWithTotal:
        result, total = await repo.get_paginated_events_with_total(limit_offset, order)

        if not result:
            raise NotFoundException(detail="Events not found")

        return EventsWithTotal(total=total, events=[Event.model_validate(obj) for obj in result])

    @get(
        "/{type:str}",
        summary="Get paginated events by type",
        raises=[NotFoundException],
    )
    async def get_events_by_type(
        self,
        repo: EventRepository,
        type: EventType,
        limit_offset: LimitOffset,
        order: Literal["desc", "asc"] = Parameter(
            required=False, description="Order by descending or ascending", default="desc"
        ),
    ) -> EventsWithTotal:

        result, total = await repo.get_paginated_events_by_type_with_total(type, limit_offset, order)

        if not result:
            raise NotFoundException(detail=f"Events not found for {type.value}")

        return EventsWithTotal(total=total, events=[Event.model_validate(obj) for obj in result])

    @get(
        "/{type:str}/most-recent",
        summary="Get most recent event by type",
        raises=[NotFoundException],
    )
    async def get_most_recent_event_by_type(
        self,
        repo: EventRepository,
        type: EventType,
    ) -> Event:
        result = await repo.get_most_recent_event_by_type(type)

        if result is None:
            raise NotFoundException(detail=f"Events not found for {type.value}")

        return Event.model_validate(result)
