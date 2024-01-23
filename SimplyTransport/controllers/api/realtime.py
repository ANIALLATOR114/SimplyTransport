from datetime import datetime, timedelta, time

from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from ...domain.services.schedule_service import (
    ScheduleService,
    provide_schedule_service,
)
from ...domain.services.realtime_service import (
    RealTimeService,
    provide_realtime_service,
)
from ...domain.realtime.realtime_schedule.model import RealTimeSchedule
from ...domain.enums import DayOfWeek


__all__ = ["RealtimeController"]


class RealtimeController(Controller):
    dependencies = {
        "schedule_service": Provide(provide_schedule_service),
        "realtime_service": Provide(provide_realtime_service),
    }

    @get("/{stop_id:str}", summary="Get realtime schedule for a stop", raises=[NotFoundException])
    async def get_realtime_schedule_by_stop_id(
        self,
        schedule_service: ScheduleService,
        realtime_service: RealTimeService,
        stop_id: str,
        start_time: time | None = Parameter(required=False, description="Start time, defaults to 10 minutes ago"),
        end_time: time | None = Parameter(required=False, description="End time, defaults to 60 minutes from now"),
        day: DayOfWeek= Parameter(required=False, description="Day of week"),
    ) -> list[RealTimeSchedule]:
        """Returns a list of realtime schedules for the given stop_id"""

        if start_time is None:
            start_time = (datetime.now() - timedelta(minutes=10)).time()

        if end_time is None:
            end_time = (datetime.now() + timedelta(minutes=60)).time()

        if day is None:
            day = DayOfWeek(datetime.now().weekday())

        if start_time > end_time:
            raise NotFoundException("Start time cannot be after end time")
        
        if start_time == end_time:
            raise NotFoundException("Start time cannot be equal to end time")
        
        max_hours_apart = 3
        if (end_time.hour - start_time.hour) > max_hours_apart:
            raise NotFoundException(f"Start time and end time cannot be more than {max_hours_apart} hours apart")

        schedules = await schedule_service.get_schedule_on_stop_for_day_between_times(
            stop_id=stop_id,
            day=datetime.now().weekday(),
            start_time=start_time,
            end_time=end_time,
        )
        schedules = await schedule_service.remove_exceptions_and_inactive_calendars(schedules)
        schedules = await schedule_service.add_in_added_exceptions(schedules)  # TODO
        schedules = await schedule_service.apply_custom_23_00_sorting(schedules)

        realtime_schedules = await realtime_service.get_realtime_schedules_for_static_schedules(schedules)
        realtime_schedules = await realtime_service.apply_custom_23_00_sorting(realtime_schedules)
                
        return [RealTimeSchedule.model_validate(realtime) for realtime in realtime_schedules]
