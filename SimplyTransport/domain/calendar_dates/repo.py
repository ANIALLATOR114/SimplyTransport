from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import CalendarDateModel


class CalendarDateRepository(SQLAlchemyAsyncRepository[CalendarDateModel]):
    """Calendar repository."""

    model_type = CalendarDateModel


async def provide_calendar_date_repo(db_session: AsyncSession) -> CalendarDateRepository:
    """This provides the Calendar repository."""
    return CalendarDateRepository(session=db_session)
