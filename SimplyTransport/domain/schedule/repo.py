from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.domain.schedule.model import DayOfWeek
from sqlalchemy.ext.asyncio import AsyncSession
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from SimplyTransport.domain.route.model import RouteModel
from SimplyTransport.domain.stop_times.model import StopTimeModel
from SimplyTransport.domain.trip.model import TripModel


class ScheduleRepository:
    """ScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_schedule_on_stop_for_day(self, stop_id: str, day: DayOfWeek):
        """Returns a list of schedules for the given stop and day"""
        conditions = []
        if day == day.MONDAY:
            conditions.append(CalendarModel.monday == 1)
        if day == day.TUESDAY:
            conditions.append(CalendarModel.tuesday == 1)
        if day == day.WEDNESDAY:
            conditions.append(CalendarModel.wednesday == 1)
        if day == day.THURSDAY:
            conditions.append(CalendarModel.thursday == 1)
        if day == day.FRIDAY:
            conditions.append(CalendarModel.friday == 1)
        if day == day.SATURDAY:
            conditions.append(CalendarModel.saturday == 1)
        if day == day.SUNDAY:
            conditions.append(CalendarModel.sunday == 1)
        else:
            raise ValueError(f"Invalid day of week {day}")

        statement = (
            select(StopTimeModel)
            .options(joinedload(StopTimeModel.trip))
            .where(
                StopTimeModel.stop_id == stop_id,
                StopTimeModel.trip_id == TripModel.id,
                TripModel.service_id == CalendarModel.id,
                TripModel.route_id == RouteModel.id,
                *conditions,
            )
            .order_by(StopTimeModel.arrival_time)
        )
        result = await self.session.execute(statement)
        for res in result:
            print(res)


async def provide_schedule_repo(db_session: AsyncSession) -> ScheduleRepository:
    """This provides the Schedule repository."""

    return ScheduleRepository(session=db_session)
