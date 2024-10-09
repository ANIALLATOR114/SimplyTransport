import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
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
        Returns all realtime schedules for the given trips.
        """
        thirty_mins_ago = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=30)

        stops_and_trips_statement = (
            select(
                RTStopTimeModel,
                RTTripModel,
            )
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .where(RTTripModel.trip_id.in_(trips))
            .where(RTTripModel.created_at >= thirty_mins_ago)
            .where(RTStopTimeModel.created_at >= thirty_mins_ago)
        )

        result = await self.session.execute(stops_and_trips_statement)
        stop_times_and_trips = result.all()

        most_recent_updates = [(stop_time, trip) for stop_time, trip in stop_times_and_trips]
        return most_recent_updates
    
    async def get_distinct_realtime_trips(self) -> List[str]:
        """
        Returns all distinct trips.
        """
        trips_statement = select(RTTripModel.trip_id).distinct()
        result = await self.session.execute(trips_statement)
        return [trip[0] for trip in result]


async def provide_schedule_update_repo(db_session: AsyncSession) -> RealtimeScheduleRepository:
    """This provides the RealtimeSchedule repository."""

    return RealtimeScheduleRepository(session=db_session)
