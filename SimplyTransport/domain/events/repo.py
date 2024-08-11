from datetime import datetime, timedelta, UTC
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from advanced_alchemy.filters import OrderBy, LimitOffset
from advanced_alchemy import NotFoundError
from typing import List, Literal, Tuple

from .model import EventModel
from .event_types import EventType
from ...lib.db.database import async_session_factory


class EventRepository(SQLAlchemyAsyncRepository[EventModel]):
    """Event repository."""

    async def create_event(
        self, event_type: EventType, description: str, attributes: dict, expiry_time: datetime | None = None
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

    async def get_paginated_events_by_type_with_total(
        self,
        event_type: EventType,
        limit_offset: LimitOffset,
        order: Literal["asc", "desc"] = "desc",
    ) -> Tuple[List[EventModel], int]:
        """Get paginated events by type with total."""

        results, total = await self.list_and_count(
            EventModel.event_type == event_type, OrderBy(EventModel.created_at, order), limit_offset
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_single_pretty_event_by_type(self, event_type: EventType) -> EventModel | None:
        try:
            events = await self.get_paginated_events_by_type_with_total(
                event_type=event_type, limit_offset=LimitOffset(limit=1, offset=0), order="desc"
            )
        except NotFoundError:
            return None
        else:
            event = events[0][0]
            return event.add_pretty_created_at()
        
    async def get_most_recent_event_by_type(self, event_type: EventType) -> EventModel | None:
        try:
            events = await self.get_paginated_events_by_type_with_total(
                event_type=event_type, limit_offset=LimitOffset(limit=1, offset=0), order="desc"
            )
        except NotFoundError:
            return None
        else:
            return events[0][0]

    async def get_paginated_events_with_total(
        self, limit_offset: LimitOffset, order="desc"
    ) -> Tuple[List[EventModel], int]:
        """Get paginated events with total."""

        results, total = await self.list_and_count(OrderBy(EventModel.created_at, order), limit_offset)

        if total == 0:
            raise NotFoundError()
        
        return results, total
    
    async def get_paginated_events(
        self, limit_offset: LimitOffset, order="desc"
    ) -> List[EventModel]:
        """Get paginated events."""

        results = await self.list(
            OrderBy(EventModel.created_at, order), limit_offset
        )

        return results

    async def cleanup_events(self, event_type: EventType = None) -> int:
        """Cleanup events that have expired. If event_type is provided, only cleanup events of that type."""

        if event_type:
            events_to_delete = await self.list(
                EventModel.event_type == event_type, EventModel.expiry_time < datetime.now(tz=UTC)
            )
            total_events_deleted = len(events_to_delete)
            await self.delete_many([event.id for event in events_to_delete])
        else:
            events_to_delete = await self.list(EventModel.expiry_time < datetime.now(tz=UTC))
            total_events_deleted = len(events_to_delete)
            await self.delete_many([event.id for event in events_to_delete])
        await self.session.commit()

        return total_events_deleted

    model_type = EventModel


async def provide_event_repo(db_session: AsyncSession) -> EventRepository:
    """This provides the Event repository."""

    return EventRepository(session=db_session)


async def create_event_with_session(
    event_type: EventType, description: str, attributes: dict, expiry_time: datetime = None
):
    async with async_session_factory() as db_session:
        event_repo = await provide_event_repo(db_session=db_session)
        await event_repo.create_event(event_type, description, attributes, expiry_time)
