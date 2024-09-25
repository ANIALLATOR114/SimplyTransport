from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import TS_StopTimeModel


class TSStopTimeRepository(SQLAlchemyAsyncRepository[TS_StopTimeModel]):
    """TSStopTime repository."""

    model_type = TS_StopTimeModel


async def provide_ts_stop_time_repo(timescale_db_session: AsyncSession) -> TSStopTimeRepository:
    """This provides the TSStopTime repository."""

    return TSStopTimeRepository(session=timescale_db_session)
