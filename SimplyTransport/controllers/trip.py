from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.trip.model import Trip, TripsWithTotal
from SimplyTransport.domain.trip.repo import TripRepository, provide_trip_repo

__all__ = ["tripController"]


class TripController(Controller):
    dependencies = {"repo": Provide(provide_trip_repo)}

    @get("/{id:str}", summary="Trip by ID", raises=[NotFoundException])
    async def get_trip_by_id(self, repo: TripRepository, id: str) -> Trip:
        try:
            result = await repo.get(id)
        except NotFoundError:
            raise NotFoundException(detail=f"Trip not found with id {id}")
        return Trip.model_validate(result)


    @get(
        "/route/{route_id:str}",
        summary="All trips by route id",
        raises=[NotFoundException],
    )
    async def get_all_trips_by_route_id(self, repo: TripRepository, route_id: str) -> list[Trip]:
        try:
            result = await repo.list(route_id=route_id)
        except NotFoundError:
            raise NotFoundException(detail=f"Trips not found with route id {route_id}")
        return [Trip.model_validate(obj) for obj in result]


    @get(
        "/route/count/{route_id:str}",
        summary="All trips by route_id with total count",
        raises=[NotFoundException],
    )
    async def get_all_trips_by_route_id_and_count(
        self, repo: TripRepository, route_id: str
    ) -> TripsWithTotal:
        try:
            result, total = await repo.list_and_count(route_id=route_id)
        except NotFoundError:
            raise NotFoundException(detail=f"Trips not found with route id {route_id}")
        return TripsWithTotal(
            total=total, trips=[Trip.model_validate(obj) for obj in result]
        )
