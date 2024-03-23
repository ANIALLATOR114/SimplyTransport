from pathlib import Path
from advanced_alchemy import NotFoundError
from litestar import Controller, MediaType, Response, get
from litestar.di import Provide
from litestar.response import Template

from ..domain.agency.model import AgencyModel
from ..domain.agency.repo import AgencyRepository, provide_agency_repo
from ..lib.constants import MAPS_STATIC_DIR, MAPS_TEMPLATES_DIR
from ..lib.logging.logging import provide_logger

from ..domain.services.map_service import MapService, provide_map_service
from ..lib.cache_keys import CacheKeys, key_builder_from_path


__all__ = [
    "MapsController",
]

logger = provide_logger(__name__)


class MapsController(Controller):
    dependencies = {
        "map_service": Provide(provide_map_service),
        "agency_repo": Provide(provide_agency_repo),
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

    @get("/agency/route/{agency_id:str}")
    async def maps(self, agency_repo: AgencyRepository, agency_id: str) -> Template:
        if agency_id != "All":
            agency = await agency_repo.get(agency_id)
        else:
            agency = AgencyModel(id="All", name="All Agencies Combined")

        try:
            # See if the file exists
            with open(Path(MAPS_STATIC_DIR) / f"{agency_id}.html"):
                pass
        except FileNotFoundError:
            logger.bind(agency_id=agency_id, path=f"{MAPS_TEMPLATES_DIR}/{agency_id}.html").error(
                f"Route map for agency {agency_id} not found"
            )
            return Template(
                "maps/agency_route.html",
                context={"agency": agency, "error": "Sorry, this map is not available"},
            )

        return Template("maps/agency_route.html", context={"agency": agency})

    @get(
        "/static/agency/route/{agency_id:str}",
        cache=86400 * 7,
        cache_key_builder=key_builder_from_path(CacheKeys.STATIC_MAP_AGENCY_ROUTE_KEY_TEMPLATE, "agency_id"),
    )
    async def static_agency_route_map(self, agency_id: str) -> Template:
        return Template(f"{MAPS_TEMPLATES_DIR}/{agency_id}.html")
