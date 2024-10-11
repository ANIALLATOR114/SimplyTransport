from datetime import time
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from .model import TS_StopTimeDelay, TS_StopTimeModel


class TSStopTimeRepository(SQLAlchemyAsyncRepository[TS_StopTimeModel]):
    """TSStopTime repository."""

    async def get_delay_on_stop_on_route_on_time(self, route_code:str, stop_id: str, scheduled_time: time) -> TS_StopTimeDelay | None:
        """
        Retrieves delay statistics for a specific stop on a specific route at a given scheduled time.
        Args:
            route_code (str): The code of the route.
            stop_id (str): The ID of the stop.
            scheduled_time (time): The scheduled time of the stop.
        Returns:
            TS_StopTimeDelay | None: An instance of TS_StopTimeDelay containing delay statistics if data is available,
                                      otherwise None.
        """

        statement = text("""
        SELECT 
            AVG(delay_in_seconds) as avg_delay,
            MAX(delay_in_seconds) as max_delay,
            MIN(delay_in_seconds) as min_delay,
            STDDEV(delay_in_seconds) as stddev_delay,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delay_in_seconds) as median_delay,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY delay_in_seconds) as p75_delay,
            PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY delay_in_seconds) as p90_delay,
            COUNT(*) as samples
        FROM ts_stop_times
        WHERE route_code = :route_code
          AND stop_id = :stop_id
          AND scheduled_time = :scheduled_time;
        """)

        params = {
            "route_code": route_code,
            "stop_id": stop_id,
            "scheduled_time": scheduled_time,
        }

        result = await self.session.execute(statement=statement, params=params)
        row = result.fetchone()

        if row and row.samples > 0:
            return TS_StopTimeDelay(
                avg=int(row.avg_delay),
                max=int(row.max_delay),
                min=int(row.min_delay),
                standard_deviation=round(float(row.stddev_delay),2)
                if row.stddev_delay is not None
                else 0.0,
                median=int(row.median_delay),
                p75=int(row.p75_delay),
                p90=int(row.p90_delay),
                samples=row.samples,
            )
        
        return None

    model_type = TS_StopTimeModel


async def provide_ts_stop_time_repo(timescale_db_session: AsyncSession) -> TSStopTimeRepository:
    """This provides the TSStopTime repository."""

    return TSStopTimeRepository(session=timescale_db_session)
