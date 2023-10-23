from datetime import date

from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Response
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.calendar.model import Calendar
from SimplyTransport.domain.calendar.repo import provide_calendar_repo, CalendarRepository

__all__ = ["calendarController"]


class CalendarController(Controller):
    dependencies = {"repo": Provide(provide_calendar_repo)}

    @get("/")
    async def get_all_calendars(self, repo: CalendarRepository) -> list[Calendar]:
        result = await repo.list()
        return [Calendar.model_validate(obj) for obj in result]

    @get("/{id:str}")
    async def get_calendar_by_id(self, repo: CalendarRepository, id: str) -> Calendar:
        try:
            result = await repo.get(id)
        except NotFoundError:
            return Response(status_code=404, content={"message": "Calendar not found"})
        return Calendar.model_validate(result)

    @get("/date/{date:date}")
    async def get_active_calendars_on_date(
        self, repo: CalendarRepository, date: date
    ) -> Calendar:
        # figure out how to filter this
        result = await repo.list()
        return [Calendar.model_validate(obj) for obj in result]
