from SimplyTransport.domain.realtime.stop.repo import RTStopRepository
from SimplyTransport.domain.realtime.trip.repo import RTTripRepository
from SimplyTransport.domain.realtime.vehicle.repo import RTVehicleRepository


class RealTimeService:
    def __init__(
        self,
        rt_stop_repository: RTStopRepository,
        rt_trip_repository: RTTripRepository,
        rt_vehicle_repository: RTVehicleRepository,
    ):
        self.rt_stop_repository = rt_stop_repository
        self.rt_trip_repository = rt_trip_repository
        self.rt_vehicle_repository = rt_vehicle_repository
