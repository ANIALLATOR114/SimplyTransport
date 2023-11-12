from datetime import datetime

from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template
from SimplyTransport.domain.stop.repo import StopRepository, provide_stop_repo
from SimplyTransport.domain.route.repo import RouteRepository, provide_route_repo
from SimplyTransport.domain.services.schedule_service import ScheduleService
from SimplyTransport.domain.schedule.model import DayOfWeek
from SimplyTransport.domain.trip.model import Direction
from sqlalchemy.ext.asyncio import AsyncSession
from SimplyTransport.domain.schedule.repo import ScheduleRepository


__all__ = [
    "RealtimeController",
]

def provide_schedule_service(db_session: AsyncSession) -> ScheduleService:
    """Constructs repository and service objects for the request."""
    return ScheduleService(ScheduleRepository(session=db_session))

class RealtimeController(Controller):
    dependencies = {
        "stop_repo": Provide(provide_stop_repo),
        "route_repo": Provide(provide_route_repo),
        "schedule_service": Provide(provide_schedule_service),
    }

    @get("/stop/{stop_id:str}")
    async def realtime_stop(
        self, stop_id: str, stop_repo: StopRepository, route_repo: RouteRepository, schedule_service: ScheduleService, day: DayOfWeek = datetime.now().weekday(),
    ) -> Template:
        stop = await stop_repo.get(stop_id)
        routes = await route_repo.get_by_stop_id(stop.id)
        schedules = await schedule_service.get_schedule_on_stop_for_day(stop_id=stop_id, day=day)
        current_time = datetime.now()
        return Template(
            template_name="realtime/stop.html",
            context={"stop": stop, "current_time": current_time, "routes": routes, "schedules": schedules},
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
