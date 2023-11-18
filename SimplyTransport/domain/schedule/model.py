from SimplyTransport.domain.route.model import RouteModel
from SimplyTransport.domain.stop_times.model import StopTimeModel
from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.domain.calendar_dates.model import CalendarDateModel
from SimplyTransport.domain.stop.model import StopModel
from SimplyTransport.domain.trip.model import TripModel
import datetime as DateTime


class StaticSchedule:
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


