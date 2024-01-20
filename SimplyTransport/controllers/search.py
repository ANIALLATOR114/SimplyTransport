import math

from litestar import Controller, get
from litestar.response import Template
from litestar.di import Provide
from SimplyTransport.domain.stop.repo import StopRepository, provide_stop_repo
from SimplyTransport.domain.route.repo import RouteRepository, provide_route_repo
from advanced_alchemy.filters import LimitOffset
from litestar.params import Parameter
from advanced_alchemy import NotFoundError

from SimplyTransport.lib.parameters.pagination_page_numbers import generate_pagination_pages

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
            stops, total = await stop_repo.list_by_name_or_code(search=search, limit_offset=limit_offset)
        except NotFoundError:
            stops = []
            total = 0

        current_page = limit_offset.offset // limit_offset.limit + 1
        total_pages = math.ceil(total / limit_offset.limit)
        pages = generate_pagination_pages(current_page, total_pages)

        return Template(
            "gtfs_search/stop_result.html",
            context={
                "stops": stops,
                "total": total,
                "search": search,
                "limit": limit_offset.limit,
                "current_page": current_page,
                "total_pages": total_pages,
                "pages": pages,
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
            routes, total = await route_repo.list_by_short_name_or_long_name(
                search=search, limit_offset=limit_offset
            )
        except NotFoundError:
            routes = []
            total = 0

        current_page = limit_offset.offset // limit_offset.limit + 1
        total_pages = math.ceil(total / limit_offset.limit)
        pages = generate_pagination_pages(current_page, total_pages)

        return Template(
            "gtfs_search/route_result.html",
            context={
                "routes": routes,
                "total": total,
                "search": search,
                "limit": limit_offset.limit,
                "current_page": current_page,
                "total_pages": total_pages,
                "pages": pages,
            },
        )
