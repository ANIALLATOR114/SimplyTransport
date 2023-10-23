from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Response
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.agency.model import Agency
from SimplyTransport.domain.agency.repo import provide_agency_repo, AgencyRepository

__all__ = ["agencyController"]


class AgencyController(Controller):
    dependencies = {"repo": Provide(provide_agency_repo)}

    @get("/")
    async def get_all_agencies(self, repo: AgencyRepository) -> list[Agency]:
        result = await repo.list()
        return [Agency.model_validate(obj) for obj in result]

    @get("/{id:str}")
    async def get_agency_by_id(self, repo: AgencyRepository, id: str) -> Agency:
        try:
            result = await repo.get(id)
        except NotFoundError:
            return Response(status_code=404, content={"message": "Agency not found"})
        return Agency.model_validate(result)
