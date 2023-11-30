from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel
from SimplyTransport.domain.schedule.model import StaticSchedule
from SimplyTransport.domain.realtime.enums import OnTimeStatus

from datetime import datetime, timedelta


class RealTimeSchedule:
    def __init__(
        self,
        static_schedule: StaticSchedule,
        rt_stop_time: RTStopTimeModel,
        rt_trip: RTTripModel,
    ):
        self.static_schedule = static_schedule
        self.rt_stop_time = rt_stop_time
        self.rt_trip = rt_trip

        self.real_arrival_time = None
        self.real_eta_text = None
        self.on_time = None
        self.delay = None

    def set_real_arrival_time(self):
        delay = max(self.rt_stop_time.arrival_delay or 0, self.rt_stop_time.departure_delay or 0)
        self.real_arrival_time = self.static_schedule.stop_time.arrival_time + timedelta(seconds=delay)

    def set_real_eta_text(self):
        current_time = datetime.now()
        arrival_time = self.real_arrival_time

        seconds_between_times = (arrival_time - current_time).seconds