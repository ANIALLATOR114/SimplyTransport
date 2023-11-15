from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import RTStopTimeModel


class RTStopTimeRepository(SQLAlchemyAsyncRepository[RTStopTimeModel]):
    """RTStopTime repository."""

    model_type = RTStopTimeModel


async def provide_rt_stop_time_repo(db_session: AsyncSession) -> RTStopTimeRepository:
    """This provides the RTStopTime repository."""

    return RTStopTimeRepository(session=db_session)
