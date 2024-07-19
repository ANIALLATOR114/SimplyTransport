import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Tuple
from sqlalchemy import Result

from ..stop_time.model import RTStopTimeModel
from ..trip.model import RTTripModel


class RealtimeScheduleRepository:
    """RealtimeScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_realtime_schedules_for_trips(
        self, trips: list[str]
    ) -> List[Tuple[RTStopTimeModel, RTTripModel]]:
        """
        Returns all realtime schedules for the given trips

        Returns the most recent update for each trip
        """
        two_hours_ago = datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=2)

        stop_time_max_statement = (
            select(RTStopTimeModel.trip_id, func.max(RTStopTimeModel.created_at))
            .where(RTStopTimeModel.trip_id.in_(trips))
            .where(RTStopTimeModel.created_at >= two_hours_ago)
            .group_by(RTStopTimeModel.trip_id)
        )
        trip_max_statement = (
            select(RTTripModel.trip_id, func.max(RTTripModel.created_at))
            .where(RTTripModel.trip_id.in_(trips))
            .where(RTTripModel.created_at >= two_hours_ago)
            .group_by(RTTripModel.trip_id)
        )
        stops_and_trips_statement = (
            select(
                RTStopTimeModel,
                RTTripModel,
            )
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .where(RTTripModel.trip_id.in_(trips))
            .where(RTTripModel.created_at >= two_hours_ago)
            .where(RTStopTimeModel.created_at >= two_hours_ago)
        )

        result_max_stop_times: Result[Tuple[str, datetime.datetime]] = await self.session.execute(
            stop_time_max_statement
        )
        result_max_trips: Result[Tuple[str, datetime.datetime]] = await self.session.execute(
            trip_max_statement
        )
        stop_times_and_trips: Result[Tuple[RTStopTimeModel, RTTripModel]] = await self.session.execute(
            stops_and_trips_statement
        )

        max_stop_times = {stop_time[0]: stop_time[1] for stop_time in result_max_stop_times}
        max_trips = {trip[0]: trip[1] for trip in result_max_trips}

        most_recent_updates = []
        for stop_time, trip in stop_times_and_trips:
            if (
                stop_time.created_at == max_stop_times[stop_time.trip_id]
                and trip.created_at == max_trips[trip.trip_id]
            ):
                most_recent_updates.append((stop_time, trip))

        return most_recent_updates


async def provide_schedule_update_repo(db_session: AsyncSession) -> RealtimeScheduleRepository:
    """This provides the RealtimeSchedule repository."""

    return RealtimeScheduleRepository(session=db_session)
