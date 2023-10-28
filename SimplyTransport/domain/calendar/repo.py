from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import CalendarModel


class CalendarRepository(SQLAlchemyAsyncRepository[CalendarModel]):
    """Calendar repository."""

    model_type = CalendarModel


async def provide_calendar_repo(db_session: AsyncSession) -> CalendarRepository:
    """This provides the Calendar repository."""

    return CalendarRepository(session=db_session)
