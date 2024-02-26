from collections import defaultdict
from itertools import cycle
from typing import Dict, List
from ..maps.layers import Layer
from ..maps.polylines import PolyLineColors, RoutePolyLine
from ..shape.model import ShapeModel
from ..shape.repo import ShapeRepository
from ..trip.repo import TripRepository
from ..route.repo import RouteRepository
from ..maps.maps import Map
from ..maps.markers import StopMarker
from ..stop.repo import StopRepository

from sqlalchemy.ext.asyncio import AsyncSession


class MapService:
    def __init__(
        self,
        stop_repository: StopRepository,
        route_repository: RouteRepository,
        shape_repository: ShapeRepository,
        trip_repository: TripRepository,
    ):
        self.stop_repository = stop_repository
        self.route_repository = route_repository
        self.shape_repository = shape_repository
        self.trip_repository = trip_repository

    async def generate_stop_map(self, stop_id: str) -> Map:
        """
        Generates a map with a stop marker and route polylines for a given stop ID.

        Args:
            stop_id (str): The ID of the stop.

        Returns:
            Map: The generated map object.
        """

        stop = await self.stop_repository.get_by_id_with_stop_feature(stop_id)
        direction = await self.stop_repository.get_direction_of_stop(stop_id)
        routes = await self.route_repository.get_routes_by_stop_id_with_agency(stop_id)

        stop_map = Map(lat=stop.lat, lon=stop.lon, zoom=14, height=500)
        stop_map.setup_defaults()

        route_ids = [route.id for route in routes]
        trips = await self.trip_repository.get_first_trips_by_route_ids(route_ids, direction)
        other_stops_on_routes = await self.stop_repository.get_stops_by_route_ids(route_ids, direction)

        shape_ids = [trip.shape_id for trip in trips]
        shapes = await self.shape_repository.get_shapes_by_shape_ids(shape_ids)

        stop_marker = StopMarker(stop=stop, create_link=False, routes=routes)
        stop_marker.add_to(stop_map.map_base)

        shapes_dict: Dict[str, List[ShapeModel]] = defaultdict(list)
        for shape in shapes:
            shapes_dict[shape.shape_id].append(shape)

        route_colors = cycle(list(PolyLineColors))

        for route in routes:
            trip = next((trip for trip in trips if trip.route_id == route.id), None)
            if trip is None:
                continue
            trip_shapes = shapes_dict.get(trip.shape_id, [])
            locations = [(shape.lat, shape.lon) for shape in trip_shapes]
            route_poly = RoutePolyLine(route=route, locations=locations, route_color=next(route_colors))
            route_poly.add_with_layer_to(stop_map.map_base)

        other_stops_layer = Layer(name="Other Stops")
        for stop in other_stops_on_routes:
            stop_marker = StopMarker(stop=stop)
            stop_marker.add_to(other_stops_layer.base_layer, type_of_marker="circle")
        other_stops_layer.add_to(stop_map.map_base)

        stop_map.add_layer_control()
        return stop_map


async def provide_map_service(db_session: AsyncSession) -> MapService:
    """
    Provides a map service instance.

    Args:
        db_session (AsyncSession): The database session.

    Returns:
        MapService: An instance of the MapService class.
    """
    return MapService(
        StopRepository(session=db_session),
        RouteRepository(session=db_session),
        ShapeRepository(session=db_session),
        TripRepository(session=db_session),
    )
