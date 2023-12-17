from datetime import datetime, timedelta, UTC
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from advanced_alchemy.filters import OrderBy, LimitOffset
from advanced_alchemy import NotFoundError
from typing import List, Tuple

from .model import EventModel
from SimplyTransport.domain.events.event_types import EventType
from SimplyTransport.lib.db.database import async_session_factory


class EventRepository(SQLAlchemyAsyncRepository[EventModel]):
    """Event repository."""

    async def create_event(
        self, event_type: EventType, description: str, attributes: dict, expiry_time: datetime = None
    ) -> EventModel:
        """Create event."""

        if expiry_time is None:
            # Set the default expiry
            expiry_time = datetime.now(tz=UTC) + timedelta(days=90)

        event = EventModel(
            event_type=event_type, description=description, expiry_time=expiry_time, attributes=attributes
        )
        new_event = await self.add(event)
        await self.session.commit()
        return new_event

    async def get_events_by_type(self, event_type: EventType, order="desc") -> list[EventModel]:
        """Get events by type."""

        return await self.list(EventModel.event_type == event_type, OrderBy(EventModel.created_at, order))

    async def get_paginated_events_by_type(
        self, event_type: EventType, limit_offset: LimitOffset, order="desc"
    ) -> Tuple[List[EventModel], int]:
        """Get paginated events by type."""

        results, total = await self.list_and_count(
            EventModel.event_type == event_type, OrderBy(EventModel.created_at, order), limit_offset
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_paginated_events(
        self, limit_offset: LimitOffset, order="desc"
    ) -> Tuple[List[EventModel], int]:
        """Get paginated events."""

        results, total = await self.list_and_count(OrderBy(EventModel.created_at, order), limit_offset)
        if total == 0:
            raise NotFoundError()
        return results, total

    model_type = EventModel


async def provide_event_repo(db_session: AsyncSession) -> EventRepository:
    """This provides the Event repository."""

    return EventRepository(session=db_session)


async def create_event_with_session(event_type: EventType, description: str, attributes: dict, expiry_time: datetime = None):
    async with async_session_factory() as db_session:
        event_repo = await provide_event_repo(db_session=db_session)
        await event_repo.create_event(event_type, description, attributes, expiry_time)