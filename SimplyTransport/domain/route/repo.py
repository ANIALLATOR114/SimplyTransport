from typing import List, Tuple

from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from .model import RouteModel
from ..trip.model import TripModel
from ..stop_times.model import StopTimeModel
from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy import NotFoundError


class RouteRepository(SQLAlchemyAsyncRepository[RouteModel]):
    """Route repository."""

    async def list_by_short_name_or_long_name(
        self, search: str, limit_offset: LimitOffset
    ) -> Tuple[List[RouteModel], int]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            RouteModel.short_name.istartswith(search) | RouteModel.long_name.istartswith(search),
            limit_offset,
            OrderBy(RouteModel.short_name, "asc"),
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_routes_by_stop_id(self, stop_id: str) -> List[RouteModel]:
        """Get routes by stop_id."""

        return await self.list(
            RouteModel.trips.any(TripModel.stop_times.any(StopTimeModel.stop_id == stop_id))
        )

    async def get_routes_by_stop_id_with_agency(self, stop_id: str) -> List[RouteModel]:
        """Get routes by stop_id with agency."""

        return await self.list(
            RouteModel.trips.any(TripModel.stop_times.any(StopTimeModel.stop_id == stop_id)),
            statement=select(RouteModel).options(joinedload(RouteModel.agency)),
        )

    async def get_by_id_with_agency(self, id: str) -> RouteModel:
        """Get a route by id with agency."""

        return await self.get(id, statement=select(RouteModel).options(joinedload(RouteModel.agency)))

    model_type = RouteModel


async def provide_route_repo(db_session: AsyncSession) -> RouteRepository:
    """This provides the Route repository."""

    return RouteRepository(session=db_session)
