from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List

from ..realtime.stop_time.repo import RTStopTimeRepository
from ..realtime.trip.repo import RTTripRepository
from ..realtime.vehicle.repo import RTVehicleRepository
from ..realtime.realtime_schedule.repo import RealtimeScheduleRepository
from ..realtime.realtime_schedule.model import RealTimeScheduleModel
from ..schedule.model import StaticScheduleModel
from ..realtime.stop_time.model import RTStopTimeModel
from ..realtime.trip.model import RTTripModel


class RealTimeService:
    def __init__(
        self,
        rt_stop_repository: RTStopTimeRepository,
        rt_trip_repository: RTTripRepository,
        rt_vehicle_repository: RTVehicleRepository,
        realtime_schedule_repository: RealtimeScheduleRepository,
    ):
        self.rt_stop_repository = rt_stop_repository
        self.rt_trip_repository = rt_trip_repository
        self.rt_vehicle_repository = rt_vehicle_repository
        self.realtime_schedule_repository = realtime_schedule_repository

    def parse_most_recent_realtime_update(
        self, realtime_updates: List[Tuple[RTStopTimeModel, RTTripModel]]
    ) -> List[Tuple[RTStopTimeModel, RTTripModel]]:
        """Returns a list of RealTimeSchedule objects that are the most recent update for each trip according to the stop_sequence"""

        if not realtime_updates:
            return []

        most_recent_realtime_updates = {}

        for stop_time, trip in realtime_updates:
            trip_id = trip.trip_id
            most_recent_update = most_recent_realtime_updates.get(trip_id)

            if most_recent_update is None or stop_time.stop_sequence > most_recent_update[0].stop_sequence:
                most_recent_realtime_updates[trip_id] = (stop_time, trip)

        return list(most_recent_realtime_updates.values())

    async def get_realtime_schedules_for_static_schedules(
        self, schedules: list[StaticScheduleModel]
    ) -> list[RealTimeScheduleModel]:
        """Returns a list of RealTimeSchedule objects for the given list of StaticSchedule objects"""

        if not schedules:
            return []

        trip_ids = [schedule.trip.id for schedule in schedules]
        realtime_schedules_from_db = await self.realtime_schedule_repository.get_realtime_schedules_for_trips(
            trips=trip_ids
        )

        only_most_recent_realtime_schedules = self.parse_most_recent_realtime_update(
            realtime_schedules_from_db
        )

        # Create a dictionary for quick lookup
        most_recent_realtime_dict = {
            trip.trip_id: (stop_time, trip) for stop_time, trip in only_most_recent_realtime_schedules
        }

        realtime_schedules = []
        for static in schedules:
            trip_id = static.trip.id
            if trip_id in most_recent_realtime_dict:
                stop_time, trip = most_recent_realtime_dict[trip_id]
                realtime_schedules.append(
                    RealTimeScheduleModel(static_schedule=static, rt_trip=trip, rt_stop_time=stop_time)
                )
            else:
                realtime_schedules.append(RealTimeScheduleModel(static_schedule=static))

        return realtime_schedules

    async def apply_custom_23_00_sorting(
        self, realtime_schedules: list[RealTimeScheduleModel]
    ) -> list[RealTimeScheduleModel]:
        """Sorts the realtime schedules by realtime arrival time"""

        def custom_sort_key(realtime_schedule: RealTimeScheduleModel):
            arrival_time = realtime_schedule.real_arrival_time

            # Handle the exception case where times in the range 00:00 to 02:00 sort after times in the range 23:00 to 23:59
            if 0 <= arrival_time.hour <= 2:
                return (24, arrival_time.hour, arrival_time.minute, arrival_time.second)
            else:
                return (arrival_time.hour, arrival_time.minute, arrival_time.second)

        sorted_schedules = sorted(realtime_schedules, key=custom_sort_key)

        return sorted_schedules

    def filter_to_only_due_schedules(
        self, realtime_schedules: list[RealTimeScheduleModel]
    ) -> list[RealTimeScheduleModel]:
        """Filters the realtime schedules to only those that are due"""

        due_schedules = [schedule for schedule in realtime_schedules if schedule.is_due]
        return due_schedules

    def filter_to_only_schedules_with_updates(
        self, realtime_schedules: list[RealTimeScheduleModel]
    ) -> list[RealTimeScheduleModel]:
        """Filters the realtime schedules to only those that have realtime updates"""

        realtime_schedules = [
            schedule
            for schedule in realtime_schedules
            if schedule.rt_stop_time is not None and schedule.rt_trip is not None
        ]
        return realtime_schedules

    async def get_distinct_realtime_trips(self) -> List[str]:
        """Returns all distinct trips."""

        return await self.realtime_schedule_repository.get_distinct_realtime_trips()


async def provide_realtime_service(db_session: AsyncSession) -> RealTimeService:
    """Constructs repository and service objects for the realtime service."""

    return RealTimeService(
        rt_stop_repository=RTStopTimeRepository(session=db_session),
        rt_trip_repository=RTTripRepository(session=db_session),
        rt_vehicle_repository=RTVehicleRepository(session=db_session),
        realtime_schedule_repository=RealtimeScheduleRepository(session=db_session),
    )
