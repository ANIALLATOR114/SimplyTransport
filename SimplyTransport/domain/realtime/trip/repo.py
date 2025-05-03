from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .model import RTTripModel


class RTTripRepository(SQLAlchemyAsyncRepository[RTTripModel]):  # type: ignore
    """RTTripRepository repository."""

    model_type = RTTripModel


async def provide_rt_trip_repo(db_session: AsyncSession) -> RTTripRepository:
    """This provides the RTTrip repository."""

    return RTTripRepository(session=db_session)
