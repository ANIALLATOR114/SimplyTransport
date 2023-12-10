from datetime import date

from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy.filters import OnBeforeAfter

from SimplyTransport.domain.calendar_dates.model import CalendarDate, CalendarDateWithTotal
from SimplyTransport.domain.calendar_dates.repo import (
    provide_calendar_date_repo,
    CalendarDateRepository,
)

__all__ = ["CalendarDateController"]


class CalendarDateController(Controller):
    dependencies = {"repo": Provide(provide_calendar_date_repo)}

    @get("/", summary="All calendar dates")
    async def get_all_calendars(self, repo: CalendarDateRepository) -> list[CalendarDate]:
        result = await repo.list()
        return [CalendarDate.model_validate(obj) for obj in result]

    @get("/count", summary="All calendar dates with total count")
    async def get_all_calendars_and_count(self, repo: CalendarDateRepository) -> CalendarDateWithTotal:
        result, total = await repo.list_and_count()
        return CalendarDateWithTotal(
            total=total, calendar_dates=[CalendarDate.model_validate(obj) for obj in result]
        )

    @get("/{service_id:str}", summary="CalendarDates by service ID", raises=[NotFoundException])
    async def get_calendar_dates_by_id(
        self, repo: CalendarDateRepository, service_id: str
    ) -> list[CalendarDate]:
        result = await repo.list(service_id=service_id)
        if result is None or len(result) == 0:
            raise NotFoundException(detail=f"CalendarDate nots found with service_id {service_id}")
        return [CalendarDate.model_validate(obj) for obj in result]

    @get(
        "/date/{date:date}",
        summary="All calendar dates on a given date",
        description="Date format = YYYY-MM-DD",
    )
    async def get_active_calendar_dates_on_date(
        self, repo: CalendarDateRepository, date: date
    ) -> list[CalendarDate]:
        result = await repo.list(
            OnBeforeAfter(field_name="date", on_or_before=date, on_or_after=None),
            OnBeforeAfter(field_name="date", on_or_before=None, on_or_after=date),
        )
        return [CalendarDate.model_validate(obj) for obj in result]
