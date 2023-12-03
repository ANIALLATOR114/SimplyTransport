from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from SimplyTransport.domain.realtime.stop_time.model import RTStopTimeModel
from SimplyTransport.domain.realtime.trip.model import RTTripModel


class RealtimeScheduleRepository:
    """RealtimeScheduleRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_realtime_schedules_for_trips(self, trips: list[str]):
        statement = (
            select(RTStopTimeModel, RTTripModel)
            .join(RTTripModel, RTTripModel.trip_id == RTStopTimeModel.trip_id)
            .where(RTTripModel.trip_id.in_(trips))
        )
        return await self.session.execute(statement)


async def provide_schedule_update_repo(db_session: AsyncSession) -> RealtimeScheduleRepository:
    """This provides the RealtimeSchedule repository."""

    return RealtimeScheduleRepository(session=db_session)
