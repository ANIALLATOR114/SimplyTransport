from typing import List, Tuple

from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from ..stop_features.model import StopFeatureModel
from .model import StopModel
from ..trip.model import TripModel
from ..route.model import RouteModel
from ..stop_times.model import StopTimeModel
from sqlalchemy import select
from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy import NotFoundError
from sqlalchemy.orm import joinedload


class StopRepository(SQLAlchemyAsyncRepository[StopModel]):
    """Stop repository."""

    model_type = StopModel

    async def get_by_code(self, code: str) -> StopModel:
        """Get a stop by code."""

        return await self.get_one(code=code)

    async def list_by_name_or_code(
        self, search: str, limit_offset: LimitOffset
    ) -> Tuple[List[StopModel], int]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            StopModel.name.istartswith(search) | StopModel.code.istartswith(search),
            limit_offset,
            OrderBy(StopModel.code, "asc"),
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_stops_by_route_id(self, route_id: str, direction: int) -> list[StopModel]:
        """Get stops by route_id."""

        return await self.list(
            statement=select(StopModel)
            .options(joinedload(StopModel.stop_feature))
            .join(StopTimeModel, StopTimeModel.stop_id == StopModel.id)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .where(TripModel.direction == direction)
            .where(TripModel.route_id == route_id)
            .distinct(StopModel.id)
        )

    async def get_stops_by_route_ids(self, route_ids: list[str], direction: int) -> list[StopModel]:
        """Get stops by route_ids."""

        return await self.list(
            statement=select(StopModel)
            .options(joinedload(StopModel.stop_feature))
            .join(StopTimeModel, StopTimeModel.stop_id == StopModel.id)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .where(TripModel.direction == direction)
            .where(TripModel.route_id.in_(route_ids))
            .distinct(StopModel.id)
        )

    async def get_direction_of_stop(self, stop_id: str) -> int:
        """Get the direction of a stop."""

        result = await self._execute(
            statement=select(TripModel.direction)
            .join(StopTimeModel, StopTimeModel.trip_id == TripModel.id)
            .where(StopTimeModel.stop_id == stop_id)
            .limit(1)
        )
        return result.scalar() or 0

    async def get_by_route_id_with_sequence(
        self, route_id: str, direction: int
    ) -> List[Tuple[StopModel, int]]:
        """Get stops by route_id with a stop_sequence."""

        result = await self.session.execute(
            statement=select(StopModel, StopTimeModel.stop_sequence)
            .join(StopTimeModel, StopTimeModel.stop_id == StopModel.id)
            .join(TripModel, TripModel.id == StopTimeModel.trip_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .where(TripModel.direction == direction)
            .where(RouteModel.id == route_id)
            .group_by(StopModel.id, StopTimeModel.stop_sequence)
            .order_by(StopTimeModel.stop_sequence)
        )

        return [(row.StopModel, row.stop_sequence) for row in result.all()]

    async def get_by_id_with_stop_feature(self, id: str) -> StopModel:
        """Get a stop by id with stop feature."""

        return await self.get(id, statement=select(StopModel).options(joinedload(StopModel.stop_feature)))
    
    async def get_all_with_stop_feature(self) -> list[StopModel]:
        """Get all stops with stop features."""

        return await self.list(
            statement=select(StopModel).options(joinedload(StopModel.stop_feature))
        )

    async def get_stops_with_realtime_displays(
        self) -> list[StopModel]:
        """Get stops by realtime displays."""

        return await self.list(
            statement=select(StopModel)
            .options(joinedload(StopModel.stop_feature))
            .join(StopFeatureModel, StopFeatureModel.stop_id == StopModel.id)
            .where(StopFeatureModel.rtpi_active == True)  # noqa: E712
        )
    
    async def get_stops_with_shelters(self) -> list[StopModel]:
        """Get stops by realtime displays."""

        return await self.list(
            statement=select(StopModel)
            .options(joinedload(StopModel.stop_feature))
            .join(StopFeatureModel, StopFeatureModel.stop_id == StopModel.id)
            .where(StopFeatureModel.shelter_active == True)  # noqa: E712
        )
    
    async def get_stops_that_are_unsurveyed(self) -> list[StopModel]:
        """Get stops by realtime displays."""

        return await self.list(
            statement=select(StopModel)
            .options(joinedload(StopModel.stop_feature))
            .join(StopFeatureModel, StopFeatureModel.stop_id == StopModel.id)
            .where(StopFeatureModel.surveyed == False)  # noqa: E712
        )


async def provide_stop_repo(db_session: AsyncSession) -> StopRepository:
    """This provides the Stop repository."""

    return StopRepository(session=db_session)
