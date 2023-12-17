from datetime import datetime, timedelta, UTC, date
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from advanced_alchemy.filters import OrderBy, LimitOffset

from .model import EventModel
from SimplyTransport.domain.events.event_types import EventType

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

    async def get_events_by_type(self, event_type: EventType, order = "desc") -> list[EventModel]:
        """Get events by type."""

        return await self.list(EventModel.event_type == event_type, OrderBy(EventModel.created_at, order))

    async def get_paginated_events_by_type(
        self, event_type: EventType, limit_offset: LimitOffset, order = "desc"
    ) -> list[EventModel]:
        """Get paginated events by type."""

        return await self.list(
            EventModel.event_type == event_type, OrderBy(EventModel.created_at, order), limit_offset
        )

    async def get_paginated_events(self, limit_offset: LimitOffset, order = "desc") -> list[EventModel]:
        """Get paginated events."""

        return await self.list(OrderBy(EventModel.created_at, order), limit_offset)

    async def get_events_by_type_on_date(self, event_type: EventType, date: date, order = "desc") -> list[EventModel]:
        """Get events by type on date."""

        start_of_day = datetime.combine(date, datetime.min.time())
        start_of_next_day = datetime.combine(date, datetime.min.time()) + timedelta(days=1)

        return await self.list(
            EventModel.event_type == event_type,
            EventModel.created_at >= start_of_day,
            EventModel.created_at < start_of_next_day,
            OrderBy(EventModel.created_at, order),
        )

    model_type = EventModel


async def provide_event_repo(db_session: AsyncSession) -> EventRepository:
    """This provides the Event repository."""

    return EventRepository(session=db_session)
