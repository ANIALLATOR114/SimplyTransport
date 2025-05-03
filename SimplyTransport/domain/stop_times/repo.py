from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .model import StopTimeModel


class StopTimeRepository(SQLAlchemyAsyncRepository[StopTimeModel]):  # type: ignore[type-var]
    """StopTime repository."""

    model_type = StopTimeModel


async def provide_stop_time_repo(db_session: AsyncSession) -> StopTimeRepository:
    """This provides the StopTime repository."""

    return StopTimeRepository(session=db_session)
