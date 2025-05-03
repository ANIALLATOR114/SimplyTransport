from collections.abc import Sequence

from advanced_alchemy import NotFoundError
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import TripModel


class TripRepository(SQLAlchemyAsyncRepository[TripModel]):  # type: ignore[type-var]
    """Trip repository."""

    async def get_first_trips_by_route_ids(
        self, route_ids: list[str], direction: int = 1
    ) -> Sequence[TripModel]:
        """Get first trips by route_ids."""

        result = await self.session.execute(
            select(TripModel)
            .where(TripModel.route_id.in_(route_ids))
            .where(TripModel.direction == direction)
            .distinct(TripModel.route_id)
        )

        return result.scalars().all()

    async def get_first_trip_by_route_id(self, route_id: str, direction: int) -> TripModel:
        """Get first trip by route_id."""

        result = await self.session.execute(
            select(TripModel)
            .where(TripModel.route_id == route_id)
            .where(TripModel.direction == direction)
            .distinct(TripModel.route_id)
            .limit(1)
        )
        trip = result.scalars().first()
        if trip is None:
            raise NotFoundError(f"Trip not found for route {route_id} and direction {direction}")
        else:
            return trip

    model_type = TripModel


async def provide_trip_repo(db_session: AsyncSession) -> TripRepository:
    """This provides the Trip repository."""

    return TripRepository(session=db_session)
