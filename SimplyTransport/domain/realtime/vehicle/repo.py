from collections.abc import Sequence

from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ...agency.model import AgencyModel
from ...route.model import RouteModel
from ...trip.model import TripModel
from .model import RTVehicleModel


class RTVehicleRepository(SQLAlchemyAsyncRepository[RTVehicleModel]):
    """RTVehicle repository."""

    async def get_vehicles_on_routes(self, route_ids: list, direction: int) -> Sequence[RTVehicleModel]:
        """Get most recent vehicle updates for vehicles on routes.

        Args:
            route_ids (list): List of route IDs.

        Returns:
            list: List of RTVehicleModel objects representing the most recent vehicle updates
            for vehicles on the specified routes.
        """

        subquery = (
            select(
                RTVehicleModel.vehicle_id,
                func.max(RTVehicleModel.time_of_update).label("max_time_of_update"),
            )
            .join(TripModel, TripModel.id == RTVehicleModel.trip_id)
            .where(TripModel.route_id.in_(route_ids))
            .where(TripModel.direction == direction)
            .group_by(RTVehicleModel.vehicle_id)
            .alias("subquery")
        )

        statement = (
            select(RTVehicleModel)
            .options(
                joinedload(RTVehicleModel.trip).joinedload(TripModel.route).joinedload(RouteModel.agency)
            )
            .join(TripModel, TripModel.id == RTVehicleModel.trip_id)
            .join(RouteModel, RouteModel.id == TripModel.route_id)
            .join(AgencyModel, RouteModel.agency_id == AgencyModel.id)
            .join(
                subquery,
                (subquery.c.vehicle_id == RTVehicleModel.vehicle_id)
                & (subquery.c.max_time_of_update == RTVehicleModel.time_of_update),
            )
            .where(TripModel.route_id.in_(route_ids))
            .where(TripModel.direction == direction)
            .order_by(RTVehicleModel.vehicle_id.desc())
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

    model_type = RTVehicleModel


async def provide_rt_vehicle_repo(db_session: AsyncSession) -> RTVehicleRepository:
    """This provides the RTVehicle repository."""

    return RTVehicleRepository(session=db_session)
