from SimplyTransport.domain.schedule.repo import ScheduleRepository
from SimplyTransport.domain.calendar_dates.repo import CalendarDateRepository
from SimplyTransport.domain.schedule.model import StaticSchedule
from SimplyTransport.domain.schedule.model import DayOfWeek
from datetime import date, timedelta


class ScheduleService:
    def __init__(
        self,
        schedule_repository: ScheduleRepository,
        calendar_date_respository: CalendarDateRepository,
    ):
        self.schedule_repository = schedule_repository
        self.calendar_date_respository = calendar_date_respository

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
            )
            for schedule in schedules_from_db
        ]

        return static_schedules

    async def remove_exceptions_and_inactive_calendars(
        self, static_schedules: list[StaticSchedule]
    ) -> list[StaticSchedule]:
        """Removes exceptions from the list of schedules"""
        current_day = date.today() + timedelta(days=1)
        exceptions_from_db = await self.calendar_date_respository.get_removed_exceptions_on_date(
            date=current_day
        )
        for schedule in static_schedules:
            if not schedule.true_if_active(date=current_day):
                static_schedules.remove(schedule)
            elif schedule.in_exceptions(list_of_exceptions=exceptions_from_db):
                static_schedules.remove(schedule)

        return static_schedules

    async def add_in_added_exceptions(
        self, static_schedules: list[StaticSchedule]
    ) -> list[StaticSchedule]:
        """Adds in added exceptions from the list of schedules"""
        pass  # TODO

        return static_schedules
