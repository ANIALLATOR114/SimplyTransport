from pydantic import BaseModel as _BaseModel

from ..route.model import Route, RouteModel
from ..stop_times.model import StopTime, StopTimeModel
from ..calendar.model import CalendarModel
from ..calendar_dates.model import CalendarDateModel
from ..stop.model import StopModel
from ..trip.model import Trip, TripModel
import datetime as DateTime


class BaseModel(_BaseModel):
    """Extend Pydantic's BaseModel to enable ORM mode"""

    model_config = {"from_attributes": True}


class StaticScheduleModel:
    def __init__(
        self,
        route: RouteModel,
        stop_time: StopTimeModel,
        calendar: CalendarModel,
        stop: StopModel,
        trip: TripModel,
    ):
        self.route = route
        self.stop_time = stop_time
        self.calendar = calendar
        self.stop = stop
        self.trip = trip

    def true_if_active(self, date: DateTime.date):
        return self.calendar.true_if_active(date)

    def true_if_active_between_times(
        self, date: DateTime.date, start_time: DateTime.time, end_time: DateTime.time
    ):
        return self.calendar.true_if_active(date) and self.stop_time.true_if_active_between_times(
            start_time=start_time, end_time=end_time
        )

    def in_exceptions(self, list_of_exceptions: list[CalendarDateModel]):
        """This assumes that the exceptions passed are active on the given date"""

        return self.calendar.in_exceptions(list_of_exceptions)


class StaticSchedule(BaseModel):
    route: Route
    stop_time: StopTime
    trip: Trip
