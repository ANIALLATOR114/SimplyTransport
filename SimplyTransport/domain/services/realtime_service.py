from sqlalchemy.ext.asyncio import AsyncSession

from SimplyTransport.domain.realtime.stop_time.repo import RTStopTimeRepository
from SimplyTransport.domain.realtime.trip.repo import RTTripRepository
from SimplyTransport.domain.realtime.vehicle.repo import RTVehicleRepository
from SimplyTransport.domain.realtime.schedule_update.repo import ScheduleUpdateRepository


class RealTimeService:
    def __init__(
        self,
        rt_stop_repository: RTStopTimeRepository,
        rt_trip_repository: RTTripRepository,
        rt_vehicle_repository: RTVehicleRepository,
        schedule_update_repository: ScheduleUpdateRepository,
    ):
        self.rt_stop_repository = rt_stop_repository
        self.rt_trip_repository = rt_trip_repository
        self.rt_vehicle_repository = rt_vehicle_repository
        self.schedule_update_repository = schedule_update_repository


async def provide_realtime_service(db_session: AsyncSession) -> RealTimeService:
    """Constructs repository and service objects for the realtime service."""
    return RealTimeService(
        rt_stop_repository=RTStopTimeRepository(session=db_session),
        rt_trip_repository=RTTripRepository(session=db_session),
        rt_vehicle_repository=RTVehicleRepository(session=db_session),
        schedule_update_repository=ScheduleUpdateRepository(session=db_session),
    )
