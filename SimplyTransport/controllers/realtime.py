from datetime import datetime

from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template
from SimplyTransport.domain.stop.repo import StopRepository, provide_stop_repo
from SimplyTransport.domain.route.repo import RouteRepository, provide_route_repo


__all__ = [
    "RealtimeController",
]


class RealtimeController(Controller):
    dependencies = {
        "stop_repo": Provide(provide_stop_repo),
        "route_repo": Provide(provide_route_repo),
    }

    @get("/stop/{stop_id:str}")
    async def realtime_stop(
        self, stop_id: str, stop_repo: StopRepository, route_repo: RouteRepository
    ) -> Template:
        stop = await stop_repo.get(stop_id)
        routes = await route_repo.get_by_stop_id(stop.id)
        current_time = datetime.now()
        return Template(
            template_name="realtime/stop.html",
            context={"stop": stop, "current_time": current_time, "routes": routes},
        )

    @get("/route/{route_id:str}")
    async def realtime_route(self, route_id: str, route_repo: RouteRepository) -> Template:
        route = await route_repo.get(route_id)
        return Template(template_name="realtime/route.html", context={"route": route})
