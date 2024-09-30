from datetime import datetime, timedelta

from SimplyTransport.domain.realtime.realtime_schedule.model import RealTimeScheduleModel
from SimplyTransport.domain.services.realtime_service import RealTimeService, provide_realtime_service
from SimplyTransport.lib.logging.logging import provide_logger
from SimplyTransport.timescale.ts_stop_times.model import TS_StopTimeModel
from ...domain.services.schedule_service import ScheduleService, provide_schedule_service
from ..ts_stop_times.repo import TSStopTimeRepository
from ...domain.enums import DayOfWeek

from sqlalchemy.ext.asyncio import AsyncSession

logger = provide_logger(__name__)


class DelaysService:
    def __init__(
        self,
        ts_stop_time_repository: TSStopTimeRepository,
        schedule_service: ScheduleService,
        realtime_service: RealTimeService,
    ):
        self.ts_stop_time_repository = ts_stop_time_repository
        self.schedule_service = schedule_service
        self.realtime_service = realtime_service

    async def record_all_delays(self) -> int:
        """
        Records all delays for the current day within a specific time range.
        Returns:
            int: The number of delays recorded.
        """

        def chunk_list(lst, chunk_size):
            for i in range(0, len(lst), chunk_size):
                logger.info(f"Returning chunk number {i // chunk_size} out of {len(lst) // chunk_size}.")
                yield lst[i : i + chunk_size]

        current_day = DayOfWeek(datetime.now().weekday())
        start_time = datetime.now() - timedelta(minutes=30)
        end_time = datetime.now() + timedelta(minutes=30)
        logger.info(f"Fetching schedules for Day:{current_day} between {start_time} and {end_time}.")
        schedules = await self.schedule_service.get_all_schedule_for_day_between_times(
            day=current_day, start_time=start_time.time(), end_time=end_time.time()
        )
        logger.info(f"Found {len(schedules)} schedules.")

        schedules = await self.schedule_service.remove_exceptions_and_inactive_calendars(schedules)
        logger.info(f"Removed exceptions and inactive calendars. {len(schedules)} schedules remaining.")
        schedules = await self.schedule_service.add_in_added_exceptions(schedules)  # TODO

        realtime_schedules: list[RealTimeScheduleModel] = []
        for schedule_batch in chunk_list(schedules, 400):
            batch_realtime_schedules = (
                await self.realtime_service.get_realtime_schedules_for_static_schedules(schedule_batch)
            )
            logger.info(f"Got {len(batch_realtime_schedules)} realtime schedules.")
            realtime_schedules.extend(batch_realtime_schedules)

        logger.info(f"Got {len(realtime_schedules)} realtime schedules to be filtered.")
        realtime_schedules = self.realtime_service.filter_to_only_due_schedules(realtime_schedules)
        realtime_schedules = self.realtime_service.filter_to_only_schedules_with_updates(realtime_schedules)
        logger.info(f"Filtered to finally {len(realtime_schedules)} realtime schedules.")

        objects_to_commit = []
        for schedule in realtime_schedules:
            ts_stop_time = TS_StopTimeModel(
                stop_id=schedule.static_schedule.stop.id,
                route_code=schedule.static_schedule.route.short_name,
                scheduled_time=schedule.static_schedule.stop_time.arrival_time,
                delay_in_seconds=schedule.delay_in_seconds,
            )
            objects_to_commit.append(ts_stop_time)

        await self.ts_stop_time_repository.add_many(objects_to_commit, auto_commit=True)

        logger.info(f"Recorded {len(realtime_schedules)} delays.")
        return len(realtime_schedules)


async def provide_delays_service(
    timescale_db_session: AsyncSession, db_session: AsyncSession
) -> DelaysService:
    """
    Provides a delays service instance.

    Args:
        timescale_db_session (AsyncSession): The timescale database session.
        db_session (AsyncSession): The database session.

    Returns:
        DelaysService: The delays service instance.
    """
    return DelaysService(
        ts_stop_time_repository=TSStopTimeRepository(session=timescale_db_session),
        schedule_service=await provide_schedule_service(db_session=db_session),
        realtime_service=await provide_realtime_service(db_session=db_session),
    )
