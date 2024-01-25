from datetime import datetime, timedelta, time

from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import ValidationException
from litestar.params import Parameter

from ...lib.time_date_conversions import return_time_difference
from ...domain.enums import DayOfWeek

from ...domain.services.schedule_service import (
    ScheduleService,
    provide_schedule_service,
)
from ...domain.schedule.model import StaticSchedule


__all__ = ["ScheduleController"]


class ScheduleController(Controller):
    dependencies = {
        "schedule_service": Provide(provide_schedule_service),
    }

    @get("/{stop_id:str}", summary="Get schedule for a stop", raises=[ValidationException])
    async def get_schedule_by_stop_id(
        self,
        schedule_service: ScheduleService,
        stop_id: str,
        start_time: time
        | None = Parameter(required=False, description="Start time, defaults to 10 minutes ago\n\nExample: 10:00:00"),
        end_time: time
        | None = Parameter(required=False, description="End time, defaults to 60 minutes from now\n\nExample: 11:00:00"),
        day: DayOfWeek | None = Parameter(required=False, description="Day of week, defaults to today"),
    ) -> list[StaticSchedule]:
        """Returns a list of schedules for the given stop_id"""

        if start_time is None:
            start_time = (datetime.now() - timedelta(minutes=10)).time()

        if end_time is None:
            end_time = (datetime.now() + timedelta(minutes=60)).time()

        if day is None:
            day = DayOfWeek(datetime.now().weekday())

        if start_time == end_time:
            raise ValidationException("Start time cannot be equal to end time")

        max_hours_apart = 6
        difference = return_time_difference(start_time,end_time)
        if difference > max_hours_apart:
            raise ValidationException(f"The difference of hours between start and end time must be at most {max_hours_apart} hours",extra={"start_time":start_time,"end_time":end_time,"hours_difference":difference})

        schedules = await schedule_service.get_schedule_on_stop_for_day_between_times(
            stop_id=stop_id,
            day=day.value,
            start_time=start_time,
            end_time=end_time,
        )

        schedules = await schedule_service.remove_exceptions_and_inactive_calendars(schedules)
        schedules = await schedule_service.add_in_added_exceptions(schedules)  # TODO
        schedules = await schedule_service.apply_custom_23_00_sorting(schedules)

        return [StaticSchedule.model_validate(schedule) for schedule in schedules]
