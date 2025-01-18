from typing import Literal

from SimplyTransport.domain.maps.enums import StaticStopMapTypes
from SimplyTransport.domain.services.map_service import provide_map_service

from ..lib.db.database import async_session_factory
from .constants import MAPS_STATIC_ROUTES_DIR, MAPS_STATIC_STOPS_DIR
from .logging.logging import provide_logger

logger = provide_logger(__name__)


async def build_route_map(map_name: str | Literal["All"]) -> None:
    """
    Builds a route map for the specified agency.

    Args:
        map_name (str | Literal["All"]): The name of the agency for which to build the route map.

    Returns:
        None
    """
    logger.info(f"Building route map for agency {map_name}")

    async with async_session_factory() as session:
        map_service = await provide_map_service(session)
        built_map = await map_service.generate_agency_route_map(agency_id=map_name)

    with open(f"{MAPS_STATIC_ROUTES_DIR}/{map_name}.html", "w", encoding="utf-8") as file:
        file.write(built_map.render())

    logger.info(f"Route map for {map_name} built")


async def build_stop_map(map_name: StaticStopMapTypes) -> None:
    """
    Builds a stop map for the specified map name.

    Args:
        map_name (str): The name of the map.

    Returns:
        None
    """
    logger.info(f"Building stop map for type {map_name}")

    async with async_session_factory() as session:
        map_service = await provide_map_service(session)
        built_map = await map_service.generate_static_stop_map(map_type=map_name)

    with open(f"{MAPS_STATIC_STOPS_DIR}/{map_name.value}.html", "w", encoding="utf-8") as file:
        file.write(built_map.render())

    logger.info(f"Stop map for {map_name} built")
