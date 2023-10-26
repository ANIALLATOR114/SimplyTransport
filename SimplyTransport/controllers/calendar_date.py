from datetime import date

from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy import NotFoundError
from advanced_alchemy.filters import OnBeforeAfter

from SimplyTransport.domain.calendar_dates.model import CalendarDate, CalendarDateWithTotal
from SimplyTransport.domain.calendar_dates.repo import (
    provide_calendar_date_repo,
    CalendarDateRepository,
)

__all__ = ["calendarDateController"]


class CalendarDateController(Controller):
    dependencies = {"repo": Provide(provide_calendar_date_repo)}

    @get("/", summary="Get all calendars")
    async def get_all_calendars(self, repo: CalendarDateRepository) -> list[CalendarDate]:
        result = await repo.list()
        return [CalendarDate.model_validate(obj) for obj in result]

    @get("/count", summary="Get all calendars with total count")
    async def get_all_calendars_and_count(
        self, repo: CalendarDateRepository
    ) -> CalendarDateWithTotal:
        result, total = await repo.list_and_count()
        return CalendarDateWithTotal(
            total=total, calendars=[CalendarDate.model_validate(obj) for obj in result]
        )

    @get("/{id:int}", summary="Get a CalendarDate by its ID", raises=[NotFoundException])
    async def get_calendar_by_id(self, repo: CalendarDateRepository, id: int) -> CalendarDate:
        try:
            result = await repo.get(id)
        except NotFoundError:
            raise NotFoundException(detail=f"CalendarDate not found with id {id}")
        return CalendarDate.model_validate(result)

    @get(
        "/date/{date:date}",
        summary="Get all calendar dates on a given date",
        description="Date format = YYYY-MM-DD",
    )
    async def get_active_calendars_on_date(
        self, repo: CalendarDateRepository, date: date
    ) -> CalendarDate:
        result = await repo.list(
            OnBeforeAfter(field_name="date", on_or_before=date, on_or_after=None),
            OnBeforeAfter(field_name="date", on_or_before=None, on_or_after=date),
        )
        return [CalendarDate.model_validate(obj) for obj in result]
