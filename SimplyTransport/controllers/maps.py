from advanced_alchemy import NotFoundError
from litestar import Controller, MediaType, get
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
        # cache=86400,
        # cache_key_builder=key_builder_from_path(CacheKeys.STOP_MAP_KEY_TEMPLATE, "stop_id"),
    )
    async def map_for_stop(self, stop_id: str, map_service: MapService) -> Template:
        try:
            stop_map = await map_service.generate_stop_map(stop_id)
        except NotFoundError:
            return "Stop not found"
        return Template(template_str=stop_map.render(), media_type=MediaType.HTML)
