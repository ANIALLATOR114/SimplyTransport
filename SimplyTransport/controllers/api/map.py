from advanced_alchemy import NotFoundError
from litestar import Controller, MediaType, Response, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.response import Template

from SimplyTransport.domain.services.map_service import MapService, provide_map_service
from SimplyTransport.lib.cache_keys import CacheKeys, key_builder_from_path

__all__ = ["MapController"]


class MapController(Controller):
    dependencies = {
        "map_service": Provide(provide_map_service),
    }

    @get(
        "/stop/{stop_id:str}",
        cache=86400,
        cache_key_builder=key_builder_from_path(CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE, "stop_id"),
        summary="Get a map for a stop",
        description="Will return an iframe with a map centered on the stop",
        raises=[NotFoundException],
    )
    async def map_for_stop(self, stop_id: str, map_service: MapService) -> Response | Template:
        try:
            stop_map = await map_service.generate_stop_map(stop_id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Stop not found with id {stop_id}") from e

        return Template(template_str=stop_map.render(), media_type=MediaType.HTML)

    @get(
        "/route/{route_id:str}/{direction:int}",
        cache=86400,
        cache_key_builder=key_builder_from_path(
            CacheKeys.RouteMaps.ROUTE_MAP_KEY_TEMPLATE, "route_id", "direction"
        ),
        summary="Get a map for a route",
        description="Will return an iframe with a map centered on the first stop on the route",
        raises=[NotFoundException],
    )
    async def map_for_route(
        self, route_id: str, direction: int, map_service: MapService
    ) -> Response | Template:
        try:
            route_map = await map_service.generate_route_map(route_id, direction)
        except NotFoundError as e:
            raise NotFoundException(
                detail=f"Route not found with id {route_id} and direction {direction}"
            ) from e

        return Template(template_str=route_map.render(), media_type=MediaType.HTML)
