from advanced_alchemy import NotFoundError
from litestar import Controller, MediaType, Response, get
from litestar.di import Provide
from litestar.response import Template

from ..domain.services.map_service import MapService, provide_map_service
from ..lib.cache_keys import CacheKeys, key_builder_from_path


__all__ = [
    "MapsController",
]


class MapsController(Controller):
    dependencies = {
        "map_service": Provide(provide_map_service),
    }

    @get(
        "/realtime/stop/{stop_id:str}",
        cache=86400,
        cache_key_builder=key_builder_from_path(CacheKeys.STOP_MAP_KEY_TEMPLATE, "stop_id"),
    )
    async def map_for_stop(self, stop_id: str, map_service: MapService) -> Template | Response:
        try:
            stop_map = await map_service.generate_stop_map(stop_id)
        except NotFoundError:
            return Response(status_code=404, content="Stop map could not be generated.")

        return Template(template_str=stop_map.render(), media_type=MediaType.HTML)

    @get(
        "/realtime/route/{route_id:str}/{direction:int}",
        cache=86400,
        cache_key_builder=key_builder_from_path(CacheKeys.ROUTE_MAP_KEY_TEMPLATE, "route_id", "direction"),
    )
    async def map_for_route(
        self, route_id: str, direction: int, map_service: MapService
    ) -> Template | Response:
        try:
            route_map = await map_service.generate_route_map(route_id, direction)
        except NotFoundError:
            return Response(status_code=404, content="Route map could not be generated.")

        return Template(template_str=route_map.render(), media_type=MediaType.HTML)
