from sqlalchemy.ext.asyncio import AsyncSession

from SimplyTransport.domain.realtime.stop_time.repo import RTStopTimeRepository
from SimplyTransport.domain.realtime.trip.repo import RTTripRepository
from SimplyTransport.domain.realtime.vehicle.repo import RTVehicleRepository
from SimplyTransport.domain.realtime.realtime_schedule.repo import RealtimeScheduleRepository
from SimplyTransport.domain.realtime.realtime_schedule.model import RealTimeSchedule
from SimplyTransport.domain.schedule.model import StaticSchedule


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


    async def get_realtime_schedules_for_static_schedules(self, schedules:list[StaticSchedule]) -> list[RealTimeSchedule]:
        """Returns a list of RealTimeSchedule objects for the given list of StaticSchedule objects.
        Assumes that all schedules are for the same stop."""
        
        if not schedules:
            return []
        
        trip_ids = [schedule.trip.id for schedule in schedules]
        stop_id = schedules[0].stop.id
        realtime_schedules_from_db = await self.realtime_schedule_repository.get_realtime_schedules_for_trips(trips=trip_ids, stop_id=stop_id)
        for result in realtime_schedules_from_db:
            print(result)

        realtime_schedules = []
        schedules_with_realtime = {realtime.RTTripModel.trip_id: realtime for realtime in realtime_schedules_from_db}
        for schedule in schedules:
            print(schedule.trip.id)
            print(schedules_with_realtime)
            if schedule.trip.id in schedules_with_realtime:
                print("yes")
            else:
                print("no")
                

    
        return realtime_schedules




async def provide_realtime_service(db_session: AsyncSession) -> RealTimeService:
    """Constructs repository and service objects for the realtime service."""

    return RealTimeService(
        rt_stop_repository=RTStopTimeRepository(session=db_session),
        rt_trip_repository=RTTripRepository(session=db_session),
        rt_vehicle_repository=RTVehicleRepository(session=db_session),
        realtime_schedule_repository=RealtimeScheduleRepository(session=db_session),
    )
