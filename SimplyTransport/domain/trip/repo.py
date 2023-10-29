from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import TripModel


class TripRepository(SQLAlchemyAsyncRepository[TripModel]):
    """Trip repository."""

    model_type = TripModel


async def provide_trip_repo(db_session: AsyncSession) -> TripRepository:
    """This provides the Trip repository."""

    return TripRepository(session=db_session)
