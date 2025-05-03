from datetime import date

from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from ..enums import ExceptionType
from .model import CalendarDateModel


class CalendarDateRepository(SQLAlchemyAsyncRepository[CalendarDateModel]):  # type: ignore
    """Calendar repository."""

    async def get_removed_exceptions_on_date(self, date: date) -> list[CalendarDateModel]:
        """Returns a list of removed exceptions for the given date"""

        return await self.list(
            CalendarDateModel.date == date,
            CalendarDateModel.exception_type == ExceptionType.removed,
        )

    async def get_added_exceptions_on_date(self, date: date) -> list[CalendarDateModel]:
        """Returns a list of added exceptions for the given date"""

        return await self.list(
            CalendarDateModel.date == date,
            CalendarDateModel.exception_type == ExceptionType.added,
        )

    model_type = CalendarDateModel


async def provide_calendar_date_repo(db_session: AsyncSession) -> CalendarDateRepository:
    """This provides the Calendar Date repository."""

    return CalendarDateRepository(session=db_session)
