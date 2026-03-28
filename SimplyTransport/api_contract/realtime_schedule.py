from datetime import time

from SimplyTransport.api_contract.base import ApiBaseModel
from SimplyTransport.domain.realtime.enums import OnTimeStatus
from SimplyTransport.domain.realtime.stop_time.model import RTStopTime
from SimplyTransport.domain.realtime.trip.model import RTTrip


class RealTimeSchedule(ApiBaseModel):
    rt_stop_time: RTStopTime | None
    rt_trip: RTTrip | None
    delay: str
    delay_in_seconds: int
    real_arrival_time: time
    real_eta_text: str
    on_time_status: OnTimeStatus
    is_trip_removed: bool
