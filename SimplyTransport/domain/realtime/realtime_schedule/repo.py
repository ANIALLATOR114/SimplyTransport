from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Tuple
from sqlalchemy import Result

from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel


class RealtimeScheduleRepository:
    """RealtimeScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_realtime_schedules_for_trips(self, trips: list[str]) -> Result[Tuple[RTStopTimeModel, RTTripModel]]:
        """
        Returns all realtime schedules for the given trips

        Returns the most recent update for each trip
        """
        subquery_stop_time = (
            select(
                RTStopTimeModel.trip_id,
                func.max(RTStopTimeModel.created_at).label("max_created_at"),
            )
            .group_by(RTStopTimeModel.trip_id)
            .alias("subquery_stop_time")
        )

        subquery_trip = (
            select(
                RTTripModel.trip_id,
                func.max(RTTripModel.created_at).label("max_created_at"),
            )
            .group_by(RTTripModel.trip_id)
            .alias("subquery_trip")
        )

        statement = (
            select(
                RTStopTimeModel,
                RTTripModel,
            )
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .join(subquery_stop_time, 
                (subquery_stop_time.c.trip_id == RTStopTimeModel.trip_id) & 
                (subquery_stop_time.c.max_created_at == RTStopTimeModel.created_at))
            .join(subquery_trip, 
                (subquery_trip.c.trip_id == RTTripModel.trip_id) & 
                (subquery_trip.c.max_created_at == RTTripModel.created_at))
            .where(RTTripModel.trip_id.in_(trips))
        )

        return await self.session.execute(statement)


async def provide_schedule_update_repo(db_session: AsyncSession) -> RealtimeScheduleRepository:
    """This provides the RealtimeSchedule repository."""

    return RealtimeScheduleRepository(session=db_session)
