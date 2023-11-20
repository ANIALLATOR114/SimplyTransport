from datetime import date, time

from sqlalchemy.ext.asyncio import AsyncSession

from SimplyTransport.domain.calendar_dates.repo import CalendarDateRepository
from SimplyTransport.domain.enums import DayOfWeek
from SimplyTransport.domain.schedule.model import StaticSchedule
from SimplyTransport.domain.schedule.repo import ScheduleRepository


class ScheduleService:
    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        calendar_date_repository: CalendarDateRepository,
    ):
        self.schedule_repository = schedule_repository
        self.calendar_date_respository = calendar_date_repository

    async def get_schedule_on_stop_for_day(
        self, stop_id: str, day: DayOfWeek
    ) -> list[StaticSchedule]:
        """Returns a list of schedules for the given stop and day"""
        schedules_from_db = await self.schedule_repository.get_schedule_on_stop_for_day(
            stop_id=stop_id, day=day
        )
        static_schedules = [
            StaticSchedule(
                route=schedule.RouteModel,
                stop_time=schedule.StopTimeModel,
                calendar=schedule.CalendarModel,
                stop=schedule.StopModel,
                trip=schedule.TripModel,
            )
            for schedule in schedules_from_db
        ]

        return static_schedules

    async def get_schedule_on_stop_for_day_between_times(
        self, stop_id: str, day: DayOfWeek, start_time: time, end_time: time
    ) -> list[StaticSchedule]:
        """Returns a list of schedules for the given stop and day"""
        schedules_from_db = (
            await self.schedule_repository.get_schedule_on_stop_for_day_between_times(
                stop_id=stop_id, day=day, start_time=start_time, end_time=end_time
            )
        )
        static_schedules = [
            StaticSchedule(
                route=schedule.RouteModel,
                stop_time=schedule.StopTimeModel,
                calendar=schedule.CalendarModel,
                stop=schedule.StopModel,
                trip=schedule.TripModel,
            )
            for schedule in schedules_from_db
        ]

        return static_schedules

    async def apply_custom_23_00_sorting(
        self, static_schedules: list[StaticSchedule]
    ) -> list[StaticSchedule]:
        """Sorts the schedules in a custom way"""

        def custom_sort_key(static_schedule: StaticSchedule):
            arrival_time = static_schedule.stop_time.arrival_time

            # Handle the exception case where times in the range 00:00 to 02:00 sort after times in the range 23:00 to 23:59
            if 0 <= arrival_time.hour <= 2:
                return (24, arrival_time.hour, arrival_time.minute, arrival_time.second)
            else:
                return (arrival_time.hour, arrival_time.minute, arrival_time.second)

        sorted_schedules = sorted(static_schedules, key=custom_sort_key)

        return sorted_schedules

    async def remove_exceptions_and_inactive_calendars(
        self, static_schedules: list[StaticSchedule]
    ) -> list[StaticSchedule]:
        """Removes exceptions from the list of schedules"""
        current_day = date.today()
        exceptions_from_db = await self.calendar_date_respository.get_removed_exceptions_on_date(
            date=current_day
        )

        static_schedules_filtered = []
        for schedule in static_schedules:
            if not schedule.true_if_active(date=current_day):
                continue
            elif schedule.in_exceptions(list_of_exceptions=exceptions_from_db):
                continue
            else:
                static_schedules_filtered.append(schedule)
                
        return static_schedules_filtered

    async def add_in_added_exceptions(
        self, static_schedules: list[StaticSchedule]
    ) -> list[StaticSchedule]:
        """Adds in added exceptions from the list of schedules"""
        pass  # TODO

        return static_schedules

    async def get_by_trip_id(self, trip_id: str) -> list[StaticSchedule]:
        """Returns a list of schedules for the given trip_id"""
        schedules_from_db = await self.schedule_repository.get_by_trip_id(trip_id=trip_id)
        static_schedules = [
            StaticSchedule(
                route=schedule.RouteModel,
                stop_time=schedule.StopTimeModel,
                calendar=schedule.CalendarModel,
                stop=schedule.StopModel,
                trip=schedule.TripModel,
            )
            for schedule in schedules_from_db
        ]

        return static_schedules


async def provide_schedule_service(db_session: AsyncSession) -> ScheduleService:
    """Constructs repository and service objects for the schedule service."""
    return ScheduleService(
        ScheduleRepository(session=db_session), CalendarDateRepository(session=db_session)
    )