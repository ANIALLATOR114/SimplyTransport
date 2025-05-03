from pathlib import Path

from advanced_alchemy import NotFoundError
from litestar import Controller, MediaType, Response, get
from litestar.di import Provide
from litestar.params import Parameter
from litestar.response import Template

from ..domain.agency.model import AgencyModel
from ..domain.agency.repo import AgencyRepository, provide_agency_repo
from ..domain.services.map_service import MapService, provide_map_service
from ..lib.cache_keys import CacheKeys, key_builder_from_path, key_builder_from_query
from ..lib.constants import (
    MAPS_STATIC_ROUTES_DIR,
    MAPS_STATIC_STOPS_DIR,
    MAPS_TEMPLATES_ROUTES_DIR,
    MAPS_TEMPLATES_STOPS_DIR,
)
from ..lib.logging.logging import provide_logger

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
        cache_key_builder=key_builder_from_path(CacheKeys.StopMaps.STOP_MAP_KEY_TEMPLATE, "stop_id"),
    )
    async def map_for_stop(self, stop_id: str, map_service: MapService) -> Template | Response:
        try:
            stop_map = await map_service.generate_stop_map(stop_id)
        except NotFoundError:
            # This is an embed so cannot return the error page
            return Response(status_code=404, content="Stop map could not be generated.")

        if stop_map is None:
            return Response(status_code=404, content="Stop map could not be generated.")

        return Template(template_str=stop_map.render(), media_type=MediaType.HTML)

    @get(
        "/realtime/stop/nearby",
        cache=86400,
        cache_key_builder=key_builder_from_query(
            CacheKeys.StopMaps.STOP_MAP_NEARBY_KEY_TEMPLATE, "latitude", "longitude"
        ),
    )
    async def map_for_stop_nearby(
        self,
        map_service: MapService,
        latitude: float = Parameter(query="latitude", required=True, description="Latitude of the user"),
        longitude: float = Parameter(query="longitude", required=True, description="Longitude of the user"),
    ) -> Template | Response:
        try:
            stop_map = await map_service.generate_stop_map_nearby(latitude, longitude)
        except NotFoundError:
            return Response(status_code=404, content="Stop map could not be generated.")

        return Template(template_str=stop_map.render(), media_type=MediaType.HTML)

    @get(
        "/realtime/route/{route_id:str}/{direction:int}",
        cache=86400,
        cache_key_builder=key_builder_from_path(
            CacheKeys.RouteMaps.ROUTE_MAP_KEY_TEMPLATE, "route_id", "direction"
        ),
    )
    async def map_for_route(
        self, route_id: str, direction: int, map_service: MapService
    ) -> Template | Response:
        try:
            route_map = await map_service.generate_route_map(route_id, direction)
        except NotFoundError:
            # This is an embed so cannot return the error page
            return Response(status_code=404, content="Route map could not be generated.")

        return Template(template_str=route_map.render(), media_type=MediaType.HTML)

    @get("/agency/route/{agency_id:str}")
    async def agency_maps(self, agency_repo: AgencyRepository, agency_id: str) -> Template:
        template_path = Path(MAPS_STATIC_ROUTES_DIR) / f"{agency_id}.html"

        if agency_id != "All":
            agency = await agency_repo.get(agency_id)
        else:
            agency = AgencyModel(id="All", name="All Agencies Combined")

        try:
            # See if the file exists
            with open(template_path):
                pass
        except FileNotFoundError:
            logger.bind(
                agency_id=agency_id,
                path=template_path,
            ).error(f"Route map for agency {agency_id} not found")
            return Template(
                "maps/agency_route.html",
                context={"agency": agency, "error": "Sorry, this map is not available"},
            )

        return Template("maps/agency_route.html", context={"agency": agency})

    @get(
        "/static/agency/route/{agency_id:str}",
        cache=86400 * 7,
        cache_key_builder=key_builder_from_path(
            CacheKeys.StaticMaps.STATIC_MAP_AGENCY_ROUTE_KEY_TEMPLATE, "agency_id"
        ),
    )
    async def static_agency_route_map(self, agency_id: str) -> Template:
        return Template(f"{MAPS_TEMPLATES_ROUTES_DIR}/{agency_id}.html")

    @get("/stop/{map_type:str}")
    async def stop_maps(self, map_type: str) -> Template:
        template_path = Path(MAPS_STATIC_STOPS_DIR) / f"{map_type}.html"

        try:
            # See if the file exists
            with open(template_path):
                pass
        except FileNotFoundError:
            logger.bind(
                path=template_path,
            ).error(f"Stop map for type {map_type} not found")
            return Template(
                "maps/stop.html",
                context={"error": "Sorry, this map is not available", "map_type": map_type},
            )

        return Template("maps/stop.html", context={"map_type": map_type})

    @get(
        "/static/stop/{map_type:str}",
        cache=86400 * 7,
        cache_key_builder=key_builder_from_path(
            CacheKeys.StaticMaps.STATIC_MAP_STOP_KEY_TEMPLATE, "map_type"
        ),
    )
    async def static_stop_map(self, map_type: str) -> Template:
        return Template(f"{MAPS_TEMPLATES_STOPS_DIR}/{map_type}.html")
