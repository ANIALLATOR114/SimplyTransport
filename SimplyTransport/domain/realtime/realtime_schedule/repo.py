import datetime
import time
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Tuple
from sqlalchemy import Result

from ..stop_time.model import RTStopTimeModel
from ..trip.model import RTTripModel
from ....lib.logging.logging import provide_logger

logger = provide_logger(__name__)


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
        stop_time_max_statement = (
            select(RTStopTimeModel.trip_id, func.max(RTStopTimeModel.created_at))
            .where(RTStopTimeModel.trip_id.in_(trips))
            .group_by(RTStopTimeModel.trip_id)
        )
        trip_max_statement = (
            select(RTTripModel.trip_id, func.max(RTTripModel.created_at))
            .where(RTTripModel.trip_id.in_(trips))
            .group_by(RTTripModel.trip_id)
        )
        stops_and_trips_statement1 = (
            select(
                RTStopTimeModel,
                RTTripModel,
            )
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .where(RTTripModel.trip_id.in_(trips))
        )

        stops_and_trips_statement2 = (
            select(
                RTStopTimeModel,
                RTTripModel,
            )
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .where(RTTripModel.trip_id.in_(trips))
            .where(
                RTTripModel.created_at
                >= datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=2)
            )
            .where(
                RTStopTimeModel.created_at
                >= datetime.datetime.now(datetime.UTC) - datetime.timedelta(hours=2)
            )
        )

        stops_and_trips_statement = random.choice(
            [stops_and_trips_statement1, stops_and_trips_statement2]
        )
        logger.info(f"Using stops_and_trips_statement: {stops_and_trips_statement}")


        result_max_stop_times_start_time = time.perf_counter()
        result_max_stop_times: Result[Tuple[str, datetime.datetime]] = await self.session.execute(
            stop_time_max_statement
        )
        result_max_stop_times_end_time = time.perf_counter()
        logger.info(
            f"Time taken to execute stop_time_max_statement: {result_max_stop_times_end_time - result_max_stop_times_start_time:.3f} seconds"
        )

        result_max_trips_start_time = time.perf_counter()
        result_max_trips: Result[Tuple[str, datetime.datetime]] = await self.session.execute(
            trip_max_statement
        )
        result_max_trips_end_time = time.perf_counter()
        logger.info(
            f"Time taken to execute trip_max_statement: {result_max_trips_end_time - result_max_trips_start_time:.3f} seconds"
        )

        stop_times_and_trips_start_time = time.perf_counter()
        stop_times_and_trips: Result[Tuple[RTStopTimeModel, RTTripModel]] = await self.session.execute(
            stops_and_trips_statement
        )
        stop_times_and_trips_end_time = time.perf_counter()
        logger.info(
            f"Time taken to execute stops_and_trips_statement: {stop_times_and_trips_end_time - stop_times_and_trips_start_time:.3f} seconds"
        )

        most_recent_updates_start_time = time.perf_counter()
        max_stop_times = {stop_time[0]: stop_time[1] for stop_time in result_max_stop_times}
        max_trips = {trip[0]: trip[1] for trip in result_max_trips}

        most_recent_updates = []
        for stop_time, trip in stop_times_and_trips:
            if (
                stop_time.created_at == max_stop_times[stop_time.trip_id]
                and trip.created_at == max_trips[trip.trip_id]
            ):
                most_recent_updates.append((stop_time, trip))

        most_recent_updates_end_time = time.perf_counter()
        logger.info(
            f"Time taken to generate get_realtime_schedules_for_trips: {most_recent_updates_end_time - most_recent_updates_start_time:.3f} seconds"
        )

        # % of time taken out of 100 by each step
        total_time = (
            result_max_stop_times_end_time
            - result_max_stop_times_start_time
            + result_max_trips_end_time
            - result_max_trips_start_time
            + stop_times_and_trips_end_time
            - stop_times_and_trips_start_time
            + most_recent_updates_end_time
            - most_recent_updates_start_time
        )
        logger.info(
            f"Time taken by each step in get_realtime_schedules_for_trips: "
            f"\nstop_time_max_statement: {(result_max_stop_times_end_time - result_max_stop_times_start_time) / total_time * 100:.2f}%, "
            f"\ntrip_max_statement: {(result_max_trips_end_time - result_max_trips_start_time) / total_time * 100:.2f}%, "
            f"\nstops_and_trips_statement: {(stop_times_and_trips_end_time - stop_times_and_trips_start_time) / total_time * 100:.2f}%, "
            f"\nmost_recent_updates: {(most_recent_updates_end_time - most_recent_updates_start_time) / total_time * 100:.2f}%"
        )
        return most_recent_updates


async def provide_schedule_update_repo(db_session: AsyncSession) -> RealtimeScheduleRepository:
    """This provides the RealtimeSchedule repository."""

    return RealtimeScheduleRepository(session=db_session)
