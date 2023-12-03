from sqlalchemy.ext.asyncio import AsyncSession
from typing import Tuple, List
from sqlalchemy import Result

from SimplyTransport.domain.realtime.stop_time.repo import RTStopTimeRepository
from SimplyTransport.domain.realtime.trip.repo import RTTripRepository
from SimplyTransport.domain.realtime.vehicle.repo import RTVehicleRepository
from SimplyTransport.domain.realtime.realtime_schedule.repo import RealtimeScheduleRepository
from SimplyTransport.domain.realtime.realtime_schedule.model import RealTimeSchedule
from SimplyTransport.domain.schedule.model import StaticSchedule
from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel


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


    def parse_most_recent_realtime_update(self, realtime_updates :Result[Tuple[RTStopTimeModel, RTTripModel]]) -> List[Tuple[RTStopTimeModel, RTTripModel]]:
        """Returns a list of RealTimeSchedule objects that are the most recent update for each trip according to the stop_sequence"""
            
        if not realtime_updates:
            return []
        
        most_recent_realtime_updates = {}

        for stop_time, trip in realtime_updates:
            most_recent_update = most_recent_realtime_updates.get(trip.trip_id)

            if most_recent_update is None or stop_time.stop_sequence > most_recent_update[0].stop_sequence:
                most_recent_realtime_updates[trip.trip_id] = (stop_time, trip)

        return list(most_recent_realtime_updates.values())

        
    async def get_realtime_schedules_for_static_schedules(self, schedules:list[StaticSchedule]) -> list[RealTimeSchedule]:
        """Returns a list of RealTimeSchedule objects for the given list of StaticSchedule objects"""
        
        if not schedules:
            return []

        trip_ids = [schedule.trip.id for schedule in schedules]
        realtime_schedules_from_db = await self.realtime_schedule_repository.get_realtime_schedules_for_trips(trips=trip_ids)

        only_most_recent_realtime_schedules = self.parse_most_recent_realtime_update(realtime_schedules_from_db)

        realtime_schedules = []
        for static in schedules:
            found_realtime_schedule = any(trip.trip_id == static.trip.id for _, trip in only_most_recent_realtime_schedules)

            if found_realtime_schedule:
                stop_time, trip = next((st, t) for st, t in only_most_recent_realtime_schedules if t.trip_id == static.trip.id)
                realtime_schedules.append(RealTimeSchedule(static_schedule=static, rt_trip=trip, rt_stop_time=stop_time))
            else:
                realtime_schedules.append(RealTimeSchedule(static_schedule=static))

        return realtime_schedules


async def provide_realtime_service(db_session: AsyncSession) -> RealTimeService:
    """Constructs repository and service objects for the realtime service."""

    return RealTimeService(
        rt_stop_repository=RTStopTimeRepository(session=db_session),
        rt_trip_repository=RTTripRepository(session=db_session),
        rt_vehicle_repository=RTVehicleRepository(session=db_session),
        realtime_schedule_repository=RealtimeScheduleRepository(session=db_session),
    )
