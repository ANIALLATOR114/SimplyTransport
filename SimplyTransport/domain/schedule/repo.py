from collections import namedtuple
from datetime import time

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..calendar.model import CalendarModel
from ..route.model import RouteModel
from ..enums import DayOfWeek
from ..stop.model import StopModel
from ..stop_times.model import StopTimeModel
from ..trip.model import TripModel

ScheduleTuple = namedtuple("ScheduleTuple", ["stop_time", "route", "calendar", "stop", "trip"])


class ScheduleRepository:
    """ScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_schedule_on_stop_for_day(self, stop_id: str, day: DayOfWeek) -> list[ScheduleTuple]:
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
            select(StopTimeModel, RouteModel, CalendarModel, StopModel, TripModel)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(StopModel, StopModel.id == StopTimeModel.stop_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .join(CalendarModel, CalendarModel.id == TripModel.service_id)
            .where(
                *conditions,
            )
            .order_by(StopTimeModel.arrival_time)
        )

        result = await self.session.execute(statement)
        return [ScheduleTuple(*row) for row in result]

    async def get_schedule_on_stop_for_day_between_times(
        self, stop_id: str, day: DayOfWeek, start_time: time, end_time: time
    ) -> list[ScheduleTuple]:
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

        if start_time > end_time:
            conditions.append(
                or_(
                    StopTimeModel.arrival_time >= start_time,
                    StopTimeModel.arrival_time <= end_time,
                )
            )
        else:
            conditions.append(StopTimeModel.arrival_time >= start_time)
            conditions.append(StopTimeModel.arrival_time <= end_time)

        statement = (
            select(StopTimeModel, RouteModel, CalendarModel, StopModel, TripModel)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(StopModel, StopModel.id == StopTimeModel.stop_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .join(CalendarModel, CalendarModel.id == TripModel.service_id)
            .where(
                *conditions,
            )
            .order_by(StopTimeModel.arrival_time)
        )
        result = await self.session.execute(statement)
        return [ScheduleTuple(*row) for row in result]

    async def get_by_trip_id(self, trip_id: str) -> list[ScheduleTuple]:
        """Returns a list of schedules for the given trip"""
        statement = (
            select(StopTimeModel, RouteModel, CalendarModel, StopModel, TripModel)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(StopModel, StopModel.id == StopTimeModel.stop_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .join(CalendarModel, CalendarModel.id == TripModel.service_id)
            .where(TripModel.id == trip_id)
            .order_by(StopTimeModel.arrival_time)
        )
        result = await self.session.execute(statement)
        return [ScheduleTuple(*row) for row in result]


async def provide_schedule_repo(db_session: AsyncSession) -> ScheduleRepository:
    """This provides the Schedule repository."""

    return ScheduleRepository(session=db_session)
