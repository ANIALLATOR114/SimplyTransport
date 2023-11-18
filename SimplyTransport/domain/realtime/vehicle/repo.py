from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import RTVehicleModel


class RTVehicleRepository(SQLAlchemyAsyncRepository[RTVehicleModel]):
    """RTVehicle repository."""

    model_type = RTVehicleModel


async def provide_rt_vehicle_repo(db_session: AsyncSession) -> RTVehicleRepository:
    """This provides the RTVehicle repository."""

    return RTVehicleRepository(session=db_session)
