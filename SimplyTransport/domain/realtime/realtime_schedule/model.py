from pydantic import BaseModel as _BaseModel
from typing import Optional

from ..stop_time.model import RTStopTimeModel, RTStopTime
from ..trip.model import RTTripModel, RTTrip
from ...schedule.model import StaticScheduleModel
from ..enums import OnTimeStatus

from datetime import datetime, timedelta, time


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class RealTimeScheduleModel:
    def __init__(
        self,
        static_schedule: StaticScheduleModel,
        rt_stop_time: RTStopTimeModel = None,
        rt_trip: RTTripModel = None,
    ):
        self.static_schedule = static_schedule
        self.rt_stop_time = rt_stop_time
        self.rt_trip = rt_trip

        self.delay = None
        self.delay_in_seconds = None
        self.real_arrival_time = None
        self.real_eta_text = None
        self.on_time_status = None

        if rt_stop_time is None and rt_trip is None:
            # No realtime data
            self.delay = "-"
            self.delay_in_seconds = 0
            self.real_arrival_time = static_schedule.stop_time.arrival_time
            self.set_real_eta_text()
            self.on_time_status = OnTimeStatus.UNKNOWN
        else:
            self.set_delay()
            self.set_real_arrival_time()
            self.set_real_eta_text()
            self.set_on_time_status()

    def set_delay(self):
        delay = max(self.rt_stop_time.arrival_delay or 0, self.rt_stop_time.departure_delay or 0)
        self.delay_in_seconds = delay
        self.delay = f"{delay // 60} min"

    def set_real_arrival_time(self):
        static_time = self.static_schedule.stop_time.arrival_time
        combined_time = datetime.combine(datetime.now().date(), static_time) + timedelta(
            seconds=self.delay_in_seconds
        )

        self.real_arrival_time = combined_time.time()

    def set_real_eta_text(self):
        now = datetime.now()
        arrival_time = self.real_arrival_time
        dt_arrival_time = datetime.combine(datetime.now().date(), arrival_time)

        if dt_arrival_time.hour == 23 and now.hour == 0:
            time_difference = (dt_arrival_time - now).total_seconds() / 60 - 1440
        elif dt_arrival_time.hour == 0 and now.hour == 23:
            time_difference = (dt_arrival_time - now).total_seconds() / 60 + 1440
        else:
            time_difference = (dt_arrival_time - now).total_seconds() / 60

        if time_difference <= -1:
            self.real_eta_text = "Left"
        elif time_difference < 0:
            self.real_eta_text = "Due"
        elif time_difference < 1:
            self.real_eta_text = "<1 min"
        else:
            self.real_eta_text = f"{int(time_difference)} min"

    def set_on_time_status(self):
        dt_arrival_time = datetime.combine(datetime.now().date(), self.real_arrival_time)
        dt_scheduled_time = datetime.combine(
            datetime.now().date(), self.static_schedule.stop_time.arrival_time
        )

        if dt_arrival_time.hour == 23 and dt_scheduled_time.hour == 0:
            time_difference = (dt_arrival_time - dt_scheduled_time).total_seconds() / 60 - 1440
        elif dt_arrival_time.hour == 0 and dt_scheduled_time.hour == 23:
            time_difference = (dt_arrival_time - dt_scheduled_time).total_seconds() / 60 + 1440
        else:
            time_difference = (dt_arrival_time - dt_scheduled_time).total_seconds() / 60

        if time_difference < -1:
            self.on_time_status = OnTimeStatus.EARLY
        elif time_difference > 5:
            self.on_time_status = OnTimeStatus.LATE
        else:
            self.on_time_status = OnTimeStatus.ON_TIME


class RealTimeSchedule(BaseModel):
    rt_stop_time: Optional[RTStopTime]
    rt_trip: Optional[RTTrip]
    delay: str
    delay_in_seconds: int
    real_arrival_time: time
    real_eta_text: str
    on_time_status: OnTimeStatus
