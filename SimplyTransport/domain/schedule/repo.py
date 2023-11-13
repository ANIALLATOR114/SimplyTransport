from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.domain.schedule.model import DayOfWeek
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from SimplyTransport.domain.route.model import RouteModel
from SimplyTransport.domain.stop_times.model import StopTimeModel
from SimplyTransport.domain.trip.model import TripModel
from SimplyTransport.domain.stop.model import StopModel


class ScheduleRepository:
    """ScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_schedule_on_stop_for_day(self, stop_id: str, day: DayOfWeek):
        """Returns a list of schedules for the given stop and day"""
        conditions = []
        if day == DayOfWeek.MONDAY:
            conditions.append(CalendarModel.monday == 1)
        elif day == DayOfWeek.TUESDAY:
            conditions.append(CalendarModel.tuesday == 1)
        elif day == DayOfWeek.WEDNESDAY:
            conditions.append(CalendarModel.wednesday == 1)
        elif day == DayOfWeek.THURSDAY:
            conditions.append(CalendarModel.thursday == 1)
        elif day == DayOfWeek.FRIDAY:
            conditions.append(CalendarModel.friday == 1)
        elif day == DayOfWeek.SATURDAY:
            conditions.append(CalendarModel.saturday == 1)
        elif day == DayOfWeek.SUNDAY:
            conditions.append(CalendarModel.sunday == 1)
        else:
            raise ValueError(f"Invalid day of week {day}")

        conditions.append(StopModel.id == stop_id)

        statement = (
            select(StopTimeModel, RouteModel, CalendarModel)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(StopModel, StopModel.id == StopTimeModel.stop_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .join(CalendarModel, CalendarModel.id == TripModel.service_id)
            .where(
                *conditions,
            )
            .order_by(StopTimeModel.arrival_time)
        )
        return await self.session.execute(statement)


async def provide_schedule_repo(db_session: AsyncSession) -> ScheduleRepository:
    """This provides the Schedule repository."""

    return ScheduleRepository(session=db_session)
