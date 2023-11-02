from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.stop_times.model import StopTime
from SimplyTransport.domain.stop_times.repo import StopTimeRepository, provide_stop_time_repo
from advanced_alchemy.filters import LimitOffset
from litestar.pagination import OffsetPagination
from litestar.params import Parameter

__all__ = ["stopTimeController"]


class StopTimeController(Controller):
    dependencies = {"repo": Provide(provide_stop_time_repo)}

    @get("/trip/{trip_id:str}", summary="StopTimes by trip ID", raises=[NotFoundException])
    async def get_stop_time_by_trip_id(self, repo: StopTimeRepository, trip_id: str) -> list[StopTime]:
        results = await repo.list(trip_id=trip_id)
        if results is None or len(results) == 0:
            raise NotFoundException(detail=f"StopTimes not found for trip id {id}")
        return [StopTime.model_validate(obj) for obj in results]
    
    @get("/stop/{stop_id:str}", summary="StopTimes by stop ID", raises=[NotFoundException])
    async def get_stop_time_by_stop_id(self, repo: StopTimeRepository, stop_id: str) -> list[StopTime]:
        results = await repo.list(stop_id=stop_id)
        if results is None or len(results) == 0:
            raise NotFoundException(detail=f"StopTimes not found for stop id {id}")
        return [StopTime.model_validate(obj) for obj in results]