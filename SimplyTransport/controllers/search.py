from litestar import Controller, get
from litestar.response import Template
from litestar.di import Provide
from SimplyTransport.domain.stop.repo import StopRepository, provide_stop_repo
from SimplyTransport.domain.route.repo import RouteRepository, provide_route_repo
from advanced_alchemy.filters import LimitOffset
from litestar.params import Parameter
from advanced_alchemy import NotFoundError


__all__ = [
    "SearchController",
]


class SearchController(Controller):
    dependencies = {
        "stop_repo": Provide(provide_stop_repo),
        "route_repo": Provide(provide_route_repo),
    }

    @get("/stops")
    async def stops(
        self,
        stop_repo: StopRepository,
        limit_offset: LimitOffset,
        search: str = Parameter(
            query="search", required=True, description="Search string to search by name or code"
        ),
    ) -> Template:
        try:
            results, total = await stop_repo.list_by_name_or_code(search=search, limit_offset=limit_offset)
            current_page = round(limit_offset.offset / limit_offset.limit) + 1
            if total < limit_offset.limit:
                total_pages = 1
            else:
                total_pages = round(total / limit_offset.limit)
        except NotFoundError:
            return Template(
                "gtfs_search/stop_result.html",
                context={
                    "stops": [],
                    "total": 0,
                    "search": search,
                    "limit": limit_offset.limit,
                    "page": 0,
                    "totalpages": 0,
                },
            )
        return Template(
            "gtfs_search/stop_result.html",
            context={
                "stops": results,
                "total": total,
                "search": search,
                "limit": limit_offset.limit,
                "page": current_page,
                "totalpages": total_pages,
            },
        )

    @get("/routes")
    async def routes(
        self,
        route_repo: RouteRepository,
        limit_offset: LimitOffset,
        search: str = Parameter(
            query="search", required=True, description="Search string to search by name or code"
        ),
    ) -> Template:
        try:
            results, total = await route_repo.list_by_short_name_or_long_name(
                search=search, limit_offset=limit_offset
            )
            current_page = round(limit_offset.offset / limit_offset.limit) + 1
            if total < limit_offset.limit:
                total_pages = 1
            else:
                total_pages = round(total / limit_offset.limit) + 1
        except NotFoundError:
            return Template(
                "gtfs_search/route_result.html",
                context={
                    "routes": [],
                    "total": 0,
                    "search": search,
                    "limit": limit_offset.limit,
                    "page": 0,
                    "totalpages": 0,
                },
            )
        return Template(
            "gtfs_search/route_result.html",
            context={
                "routes": results,
                "total": total,
                "search": search,
                "limit": limit_offset.limit,
                "page": current_page,
                "totalpages": total_pages,
            },
        )
