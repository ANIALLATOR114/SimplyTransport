from datetime import datetime, timedelta

from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template

from SimplyTransport.domain.route.repo import RouteRepository, provide_route_repo
from SimplyTransport.domain.enums import DayOfWeek
from SimplyTransport.domain.services.schedule_service import (
    ScheduleService,
    provide_schedule_service,
)
from SimplyTransport.domain.services.realtime_service import (
    RealTimeService,
    provide_realtime_service,
)
from SimplyTransport.domain.stop.repo import StopRepository, provide_stop_repo
from SimplyTransport.domain.trip.model import Direction

__all__ = [
    "RealtimeController",
]


class RealtimeController(Controller):
    dependencies = {
        "stop_repo": Provide(provide_stop_repo),
        "route_repo": Provide(provide_route_repo),
        "schedule_service": Provide(provide_schedule_service),
        "realtime_service": Provide(provide_realtime_service),
    }

    @get("/stop/{stop_id:str}")
    async def realtime_stop(
        self,
        stop_id: str,
        stop_repo: StopRepository,
        route_repo: RouteRepository,
        schedule_service: ScheduleService,
        realtime_service: RealTimeService,
    ) -> Template:
        stop = await stop_repo.get(stop_id)
        routes = await route_repo.get_by_stop_id(stop.id)

        current_time = datetime.now()
        start_time_difference = -10
        end_time_difference = 60
        start_time = (current_time + timedelta(minutes=start_time_difference)).time()
        end_time = (current_time + timedelta(minutes=end_time_difference)).time()

        schedules = await schedule_service.get_schedule_on_stop_for_day_between_times(
            stop_id=stop_id,
            day=datetime.now().weekday(),
            start_time=start_time,
            end_time=end_time,
        )
        schedules = await schedule_service.remove_exceptions_and_inactive_calendars(schedules)
        schedules = await schedule_service.add_in_added_exceptions(schedules)  # TODO
        schedules = await schedule_service.apply_custom_23_00_sorting(schedules)

        return Template(
            template_name="realtime/stop.html",
            context={
                "stop": stop,
                "current_time": current_time,
                "routes": routes,
                "day_string": DayOfWeek(current_time.weekday()).name.capitalize(),
                "schedules": schedules,
                "start_time_difference": start_time_difference,
                "end_time_difference": end_time_difference,
            },
        )

    @get("/stop/{stop_id:str}/schedule")
    async def realtime_stop_schedule(
        self,
        stop_id: str,
        schedule_service: ScheduleService,
        day: DayOfWeek = datetime.now().weekday(),
    ) -> Template:
        schedules = await schedule_service.get_schedule_on_stop_for_day(stop_id=stop_id, day=day)
        schedules = await schedule_service.remove_exceptions_and_inactive_calendars(schedules)
        schedules = await schedule_service.add_in_added_exceptions(schedules)  # TODO

        return Template(
            template_name="realtime/stop_schedule.html",
            context={
                "schedules": schedules,
                "day_string": DayOfWeek(day).name.capitalize(),
            },
        )

    @get("/route/{route_id:str}/{direction:int}")
    async def realtime_route(
        self,
        route_id: str,
        direction: Direction,
        route_repo: RouteRepository,
        stop_repo: StopRepository,
    ) -> Template:
        route = await route_repo.get_by_id_with_agency(route_id)
        stops_and_sequences = await stop_repo.get_by_route_id_with_sequence(route.id, direction)
        return Template(
            template_name="realtime/route.html",
            context={"route": route, "stops": stops_and_sequences, "direction": direction},
        )

    @get("/trip/{trip_id:str}")
    async def realtime_trip(
        self,
        trip_id: str,
        schedule_service: ScheduleService,
    ) -> Template:
        schedules = await schedule_service.get_by_trip_id(trip_id=trip_id)

        if len(schedules) == 0:
            return str("No schedules found for trip")  # TODO 404
            # accessing list position 0 here so will throw an error if there arent any schedules

        direction_value = schedules[0].trip.direction
        direction_string = "Southbound" if direction_value == 0 else "Northbound"

        return Template(
            template_name="realtime/trip.html",
            context={
                "schedules": schedules,
                "direction_string": direction_string,
            },
        )
