from datetime import date

from advanced_alchemy import NotFoundError
from advanced_alchemy.filters import OnBeforeAfter
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException

from ...domain.calendar.model import Calendar, CalendarWithTotal
from ...domain.calendar.repo import CalendarRepository, provide_calendar_repo

__all__ = ["CalendarController"]


class CalendarController(Controller):
    dependencies = {"repo": Provide(provide_calendar_repo)}

    @get("/", summary="All calendars")
    async def get_all_calendars(self, repo: CalendarRepository) -> list[Calendar]:
        result = await repo.list()
        return [Calendar.model_validate(obj) for obj in result]

    @get("/count", summary="All calendars with total count")
    async def get_all_calendars_and_count(self, repo: CalendarRepository) -> CalendarWithTotal:
        result, total = await repo.list_and_count()
        return CalendarWithTotal(total=total, calendars=[Calendar.model_validate(obj) for obj in result])

    @get("/{id:str}", summary="Calendar by service ID", raises=[NotFoundException])
    async def get_calendar_by_id(self, repo: CalendarRepository, id: str) -> Calendar:
        try:
            result = await repo.get(id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Calendar not found with id {id}") from e
        return Calendar.model_validate(result)

    @get(
        "/date/{date:date}",
        summary="All active calendars on a given date",
        description="Date format = YYYY-MM-DD",
    )
    async def get_active_calendars_on_date(self, repo: CalendarRepository, date: date) -> list[Calendar]:
        result = await repo.list(
            OnBeforeAfter(field_name="start_date", on_or_before=date, on_or_after=None),
            OnBeforeAfter(field_name="end_date", on_or_before=None, on_or_after=date),
        )
        return [Calendar.model_validate(obj) for obj in result]
