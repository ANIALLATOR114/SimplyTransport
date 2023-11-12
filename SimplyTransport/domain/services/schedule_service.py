from SimplyTransport.domain.schedule.repo import ScheduleRepository
from SimplyTransport.domain.schedule.model import StaticSchedule
from SimplyTransport.domain.schedule.model import DayOfWeek


class ScheduleService:
    def __init__(self, repository: ScheduleRepository):
        self.repository = repository

    async def get_schedule_on_stop_for_day(self, stop_id: str, day: DayOfWeek):
        """Returns a list of schedules for the given stop and day"""

        return await self.repository.get_schedule_on_stop_for_day(stop_id=stop_id, day=day)
