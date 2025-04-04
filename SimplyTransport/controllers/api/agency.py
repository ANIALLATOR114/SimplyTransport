from advanced_alchemy import NotFoundError
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException

from ...domain.agency.model import Agency, AgencyWithTotal
from ...domain.agency.repo import AgencyRepository, provide_agency_repo

__all__ = ["AgencyController"]


class AgencyController(Controller):
    dependencies = {"repo": Provide(provide_agency_repo)}

    @get("/", summary="All agencies")
    async def get_all_agencies(self, repo: AgencyRepository) -> list[Agency]:
        result = await repo.list()
        return [Agency.model_validate(obj) for obj in result]

    @get("/count", summary="All agencies with total count")
    async def get_all_agencies_and_count(self, repo: AgencyRepository) -> AgencyWithTotal:
        result, total = await repo.list_and_count()
        return AgencyWithTotal(total=total, agencies=[Agency.model_validate(obj) for obj in result])

    @get("/{id:str}", summary="Agency by ID", raises=[NotFoundException])
    async def get_agency_by_id(self, repo: AgencyRepository, id: str) -> Agency:
        try:
            result = await repo.get(id)
        except NotFoundError as e:
            raise NotFoundException(detail=f"Agency not found with id {id}") from e
        return Agency.model_validate(result)
