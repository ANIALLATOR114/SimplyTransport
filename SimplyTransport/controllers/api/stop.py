from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy import NotFoundError

from ...domain.stop.model import Stop
from ...domain.stop.repo import StopRepository, provide_stop_repo
from advanced_alchemy.filters import LimitOffset
from litestar.pagination import OffsetPagination
from litestar.params import Parameter

__all__ = ["StopController"]


class StopController(Controller):
    dependencies = {"repo": Provide(provide_stop_repo)}

    @get("/{id:str}", summary="Stop by ID", raises=[NotFoundException])
    async def get_stop_by_id(self, repo: StopRepository, id: str) -> Stop:
        try:
            result = await repo.get(id)
        except NotFoundError:
            raise NotFoundException(detail=f"Stop not found with id {id}")
        return Stop.model_validate(result)

    @get("/code/{code:str}", summary="Stop by code", raises=[NotFoundException])
    async def get_stop_by_code(self, repo: StopRepository, code: str) -> Stop:
        try:
            result = await repo.get_by_code(code)
        except NotFoundError:
            raise NotFoundException(detail=f"Stop not found with code {code}")
        return Stop.model_validate(result)

    @get(
        "/search",
        summary="Search stops by name or code",
        description="Search is case insensitive",
        raises=[NotFoundException],
    )
    async def search_stops_by_name_or_code(
        self,
        repo: StopRepository,
        limit_offset: LimitOffset,
        search: str = Parameter(
            query="search", required=True, description="Search string to search by name or code"
        ),
    ) -> OffsetPagination[Stop]:
        try:
            results, total = await repo.list_by_name_or_code(search=search, limit_offset=limit_offset)
        except NotFoundError:
            raise NotFoundException(detail=f"Stops not found with name/code beginning with {search}")
        return OffsetPagination[Stop](
            total=total,
            items=[Stop.model_validate(obj) for obj in results],
            limit=limit_offset.limit,
            offset=limit_offset.offset,
        )
