import asyncio

from advanced_alchemy.exceptions import NotFoundError
from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from SimplyTransport.domain.route.model import RouteModel
from SimplyTransport.lib.cache import RedisService

from ..stop_times.model import StopTimeModel
from ..trip.model import TripModel


class RouteRepository(SQLAlchemyAsyncRepository[RouteModel]):  # type: ignore
    """Route repository."""

    model_type = RouteModel
    cache: RedisService

    def __init__(self, session: AsyncSession, *, cache: RedisService):
        self.cache = cache
        super().__init__(session=session)

    async def list_by_short_name_or_long_name(
        self, search: str, limit_offset: LimitOffset
    ) -> tuple[list[RouteModel], int]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            RouteModel.short_name.istartswith(search) | RouteModel.long_name.istartswith(search),
            limit_offset,
            OrderBy(RouteModel.short_name, "asc"),  # type: ignore
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_routes_by_stop_id(self, stop_id: str) -> list[RouteModel]:
        """Get routes by stop_id."""

        return await self.list(
            RouteModel.trips.any(TripModel.stop_times.any(StopTimeModel.stop_id == stop_id))
        )

    async def get_routes_by_stop_ids(self, stop_ids: list[str]) -> dict[str, list[RouteModel]]:
        """Get routes by stop_ids"""

        tasks = [self.get_routes_by_stop_id(stop_id) for stop_id in stop_ids]
        routes = await asyncio.gather(*tasks)
        return dict(zip(stop_ids, routes, strict=True))

    async def get_routes_by_stop_id_with_agency(self, stop_id: str) -> list[RouteModel]:
        """Get routes by stop_id with agency."""

        return await self.list(
            RouteModel.trips.any(TripModel.stop_times.any(StopTimeModel.stop_id == stop_id)),
            statement=select(RouteModel).options(joinedload(RouteModel.agency)),
        )

    async def get_by_id_with_agency(self, id: str) -> RouteModel:
        """Get a route by id with agency."""

        return await self.get(id, statement=select(RouteModel).options(joinedload(RouteModel.agency)))

    async def get_with_agencies(self) -> list[RouteModel]:
        """Get all routes with agencies"""

        return await self.list(statement=select(RouteModel).options(joinedload(RouteModel.agency)))

    async def get_with_agencies_by_agency_id(self, agency_id: str) -> list[RouteModel]:
        """Get all routes with agencies by agency_id"""

        return await self.list(
            RouteModel.agency_id == agency_id,
            statement=select(RouteModel).options(joinedload(RouteModel.agency)),
        )


async def provide_route_repo(db_session: AsyncSession, redis_service: RedisService) -> RouteRepository:
    """This provides the Route repository."""

    return RouteRepository(session=db_session, cache=redis_service)
