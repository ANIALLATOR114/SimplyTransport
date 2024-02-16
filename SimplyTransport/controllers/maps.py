from advanced_alchemy import NotFoundError
from litestar import Controller, get
from litestar.di import Provide

from ..domain.services.map_service import MapService, provide_map_service


__all__ = [
    "MapsController",
]


class MapsController(Controller):
    dependencies = {
        "map_service": Provide(provide_map_service),
    }

    @get("/realtime/stop/{stop_id:str}")
    async def map_for_stop(self, stop_id: str, map_service: MapService) -> str:
        try:
            stop_map = await map_service.generate_stop_map(stop_id)
        except NotFoundError:
            return "Stop not found"
        return stop_map.render()
