import asyncio
import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Tuple

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
        twenty_mins_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=20)

        # Subquery to rank rows by created_at within each trip_id
        ranked_stop_times = (
            select(
                RTStopTimeModel.trip_id,
                func.rank()
                .over(
                    partition_by=RTStopTimeModel.trip_id,
                    order_by=desc(RTStopTimeModel.created_at),
                )
                .label("rank"),
            )
            .where(RTStopTimeModel.trip_id.in_(trips))
            .where(RTStopTimeModel.created_at >= twenty_mins_ago)
        ).subquery()

        ranked_trips = (
            select(
                RTTripModel.trip_id,
                func.rank()
                .over(
                    partition_by=RTTripModel.trip_id,
                    order_by=desc(RTTripModel.created_at),
                )
                .label("rank"),
            )
            .where(RTTripModel.trip_id.in_(trips))
            .where(RTTripModel.created_at >= twenty_mins_ago)
        ).subquery()

        # Main query to filter only the top-ranked rows
        stop_time_max_statement = select(ranked_stop_times).where(ranked_stop_times.c.rank == 1)

        trip_max_statement = select(ranked_trips).where(ranked_trips.c.rank == 1)

        stops_and_trips_statement = (
            select(
                RTStopTimeModel,
                RTTripModel,
            )
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .where(RTTripModel.trip_id.in_(trips))
            .where(RTTripModel.created_at >= twenty_mins_ago)
            .where(RTStopTimeModel.created_at >= twenty_mins_ago)
        )

        # Execute the queries concurrently
        result_max_stop_times, result_max_trips, stop_times_and_trips = await asyncio.gather(
            self.session.execute(stop_time_max_statement),
            self.session.execute(trip_max_statement),
            self.session.execute(stops_and_trips_statement),
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
