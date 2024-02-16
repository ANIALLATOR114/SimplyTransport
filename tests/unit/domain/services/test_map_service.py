from unittest.mock import AsyncMock

from SimplyTransport.domain.services.map_service import MapService


def test_map_service_init():
    stop_repository = AsyncMock()
    route_repository = AsyncMock()
    shape_repository = AsyncMock()
    trip_repository = AsyncMock()

    map_service = MapService(
        stop_repository=stop_repository,
        route_repository=route_repository,
        shape_repository=shape_repository,
        trip_repository=trip_repository,
    )
    assert map_service.stop_repository is stop_repository
    assert map_service.route_repository is route_repository
    assert map_service.shape_repository is shape_repository
    assert map_service.trip_repository is trip_repository
