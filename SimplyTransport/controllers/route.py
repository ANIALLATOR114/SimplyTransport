from datetime import date

from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from advanced_alchemy import NotFoundError

from SimplyTransport.domain.route.model import Route, RouteWithTotal
from SimplyTransport.domain.route.repo import RouteRepository, provide_route_repo

__all__ = ["calendarController"]


class RouteController(Controller):
    dependencies = {"repo": Provide(provide_route_repo)}

    @get(
        "/",
        summary="All routes",
        description="Can be filtered by agency id",
        raises=[NotFoundException],
    )
    async def get_all_routes(self, repo: RouteRepository, agency_id: str | None) -> list[Route]:
        if agency_id:
            result = await repo.list(agency_id=agency_id)
            if not result or len(result) == 0:
                raise NotFoundException(detail=f"Routes not found with agency id {agency_id}")
        else:
            result = await repo.list()
        return [Route.model_validate(obj) for obj in result]

    @get(
        "/count",
        summary="All routes with total count",
        description="Can be filtered by agency id",
        raises=[NotFoundException],
    )
    async def get_all_routes_and_count(
        self, repo: RouteRepository, agency_id: str | None
    ) -> RouteWithTotal:
        if agency_id:
            result, total = await repo.list_and_count(agency_id=agency_id)
            if not result or len(result) == 0:
                raise NotFoundException(detail=f"Routes not found with agency id {agency_id}")
        else:
            result, total = await repo.list_and_count()
        return RouteWithTotal(
            total=total, calendars=[Route.model_validate(obj) for obj in result]
        )

    @get("/{id:str}", summary="Route by ID", raises=[NotFoundException])
    async def get_route_by_id(self, repo: RouteRepository, id: str) -> Route:
        try:
            result = await repo.get(id)
        except NotFoundError:
            raise NotFoundException(detail=f"Route not found with id {id}")
        return Route.model_validate(result)
