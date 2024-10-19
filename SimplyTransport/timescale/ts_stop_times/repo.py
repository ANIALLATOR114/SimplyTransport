from datetime import datetime, time, timedelta
from typing import List
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from .model import TS_StopTimeDelayAggregated, TS_StopTimeForGraph, TS_StopTimeModel

MAXIMUM_LIMIT = 730
MAXIMUM_TIMESTAMP = datetime.now() - timedelta(days=MAXIMUM_LIMIT)


class TSStopTimeRepository(SQLAlchemyAsyncRepository[TS_StopTimeModel]):
    """TSStopTime repository."""

    async def get_aggregated_delay_on_stop_on_route_on_time(
        self,
        route_code: str,
        stop_id: str | None = None,
        scheduled_time: time | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> TS_StopTimeDelayAggregated | None:
        """
        Retrieves delay statistics for a specific stop on a specific route at a given scheduled time.
        Args:
            route_code (str): The code of the route.
            stop_id (str): The ID of the stop.
            scheduled_time (time): The scheduled time of the stop.
            start_time (datetime): The start time of the data.
            end_time (datetime): The end time of the data.
        Returns:
            TS_StopTimeDelay | None: An instance of TS_StopTimeDelay containing delay statistics if data is available,
                                      otherwise None.
        """

        base_query = """
        SELECT 
            AVG(delay_in_seconds) as avg_delay,
            MAX(delay_in_seconds) as max_delay,
            MIN(delay_in_seconds) as min_delay,
            STDDEV(delay_in_seconds) as stddev_delay,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY delay_in_seconds) as p50_delay,
            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY delay_in_seconds) as p75_delay,
            PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY delay_in_seconds) as p90_delay,
            COUNT(*) as samples
        FROM ts_stop_times
        WHERE route_code = :route_code
          AND "Timestamp" > :max_timestamp
        """

        if start_time:
            base_query += ' AND "Timestamp" >= :start_time'
        if end_time:
            base_query += ' AND "Timestamp" <= :end_time'
        if stop_id:
            base_query += " AND stop_id = :stop_id"
        if scheduled_time:
            base_query += " AND scheduled_time = :scheduled_time"

        statement = text(base_query)

        params = {
            "route_code": route_code,
            "max_timestamp": MAXIMUM_TIMESTAMP,
        }

        if start_time:
            start_time = start_time.replace(tzinfo=None)
            params["start_time"] = start_time
        if end_time:
            end_time = end_time.replace(tzinfo=None)
            params["end_time"] = end_time
        if stop_id:
            params["stop_id"] = stop_id
        if scheduled_time:
            params["scheduled_time"] = scheduled_time

        result = await self.session.execute(statement=statement, params=params)
        row = result.fetchone()

        if row and row.samples > 0:
            return TS_StopTimeDelayAggregated(
                avg=int(row.avg_delay),
                max=int(row.max_delay),
                min=int(row.min_delay),
                standard_deviation=round(float(row.stddev_delay), 2) if row.stddev_delay is not None else 0.0,
                p50=int(row.p50_delay),
                p75=int(row.p75_delay),
                p90=int(row.p90_delay),
                samples=row.samples,
            )

        return None

    async def get_delay_on_stop_on_route_on_time(
        self,
        route_code: str,
        stop_id: str,
        scheduled_time: time,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> List[TS_StopTimeModel]:
        """
        Retrieve delay information for a specific stop on a route at a scheduled time.
        Args:
            route_code (str): The code of the route.
            stop_id (str): The ID of the stop.
            scheduled_time (time): The scheduled time of the stop.
            start_time (datetime | None, optional): The start time for filtering results. Defaults to None.
            end_time (datetime | None, optional): The end time for filtering results. Defaults to None.
        Returns:
            List[TS_StopTimeModel]: A list of TS_StopTimeModel instances that match the criteria.
        """

        conditions = []
        if start_time:
            conditions.append(TS_StopTimeModel.Timestamp >= start_time)
        if end_time:
            conditions.append(TS_StopTimeModel.Timestamp <= end_time)

        statement = (
            select(TS_StopTimeModel)
            .where(
                TS_StopTimeModel.route_code == route_code,
                TS_StopTimeModel.stop_id == stop_id,
                TS_StopTimeModel.scheduled_time == scheduled_time,
                TS_StopTimeModel.Timestamp > MAXIMUM_TIMESTAMP,
            )
            .order_by(TS_StopTimeModel.Timestamp.desc())
            .limit(MAXIMUM_LIMIT)
        )

        if conditions:
            statement = statement.where(*conditions)

        result = await self.session.execute(statement)
        rows = result.scalars().all()

        return list(rows)

    async def get_truncated_delay_on_stop_on_route_on_time(
        self,
        route_code: str,
        stop_id: str,
        scheduled_time: time,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> List[TS_StopTimeForGraph]:
        """
        Retrieves a list of truncated delays for a specific stop on a route at a scheduled time.
        Args:
            route_code (str): The code of the route.
            stop_id (str): The ID of the stop.
            scheduled_time (time): The scheduled time of the stop.
            start_time (datetime | None, optional): The start time for filtering the results. Defaults to None.
            end_time (datetime | None, optional): The end time for filtering the results. Defaults to None.
        Returns:
            List[TS_StopTimeForGraph]: A list of TS_StopTimeForGraph objects containing the timestamp and delay in seconds.
        """

        conditions = []
        if start_time:
            conditions.append(TS_StopTimeModel.Timestamp >= start_time)
        if end_time:
            conditions.append(TS_StopTimeModel.Timestamp <= end_time)

        statement = (
            select(TS_StopTimeModel.Timestamp, TS_StopTimeModel.delay_in_seconds)
            .where(
                TS_StopTimeModel.route_code == route_code,
                TS_StopTimeModel.stop_id == stop_id,
                TS_StopTimeModel.scheduled_time == scheduled_time,
                TS_StopTimeModel.Timestamp > MAXIMUM_TIMESTAMP,
            )
            .order_by(TS_StopTimeModel.Timestamp.desc())
            .limit(MAXIMUM_LIMIT)
        )

        if conditions:
            statement = statement.where(*conditions)

        result = await self.session.execute(statement)
        rows = result.all()

        return [TS_StopTimeForGraph(Timestamp=row[0], delay_in_seconds=row[1]) for row in rows]

    model_type = TS_StopTimeModel


async def provide_ts_stop_time_repo(timescale_db_session: AsyncSession) -> TSStopTimeRepository:
    """This provides the TSStopTime repository."""

    return TSStopTimeRepository(session=timescale_db_session)
