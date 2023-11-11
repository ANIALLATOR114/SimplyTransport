from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import StopModel
from ..trip.model import TripModel
from ..route.model import RouteModel
from ..stop_times.model import StopTimeModel
from sqlalchemy import select
from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy import NotFoundError


class StopRepository(SQLAlchemyAsyncRepository[StopModel]):
    """Stop repository."""

    model_type = StopModel

    async def get_by_code(self, code: str) -> StopModel:
        """Get a stop by code."""

        return await self.get_one(code=code)

    async def list_by_name_or_code(
        self, search: str, limit_offset: LimitOffset
    ) -> list[StopModel]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            StopModel.name.istartswith(search) | StopModel.code.istartswith(search),
            limit_offset,
            OrderBy(StopModel.code, "asc"),
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_by_route_id(self, route_id: str, direction: int) -> list[StopModel]:
        """Get a stop by route_id."""

        return await self.list(
            statement=select(StopModel)
            .join(StopTimeModel, StopTimeModel.stop_id == StopModel.id)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .where(TripModel.direction == direction, RouteModel.id == route_id)
            .group_by(StopModel.id)
        )

    async def get_by_route_id_with_sequence(
        self, route_id: str, direction: int
    ) -> list[StopModel, int]:
        """Get a stop by route_id with a stop_sequence."""

        return await self._execute(
            statement=select(StopModel, StopTimeModel.stop_sequence)
            .join(StopTimeModel, StopTimeModel.stop_id == StopModel.id)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .where(TripModel.direction == direction, RouteModel.id == route_id)
            .group_by(StopModel.id, StopTimeModel.stop_sequence)
            .order_by(StopTimeModel.stop_sequence)
        )


async def provide_stop_repo(db_session: AsyncSession) -> StopRepository:
    """This provides the Stop repository."""

    return StopRepository(session=db_session)
