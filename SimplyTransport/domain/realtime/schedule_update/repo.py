from sqlalchemy.ext.asyncio import AsyncSession



class ScheduleUpdateRepository:
    """ScheduleUpdateRepository repository."""

    def __init__(self, session: AsyncSession):
        self.session = session


async def provide_schedule_update_repo(db_session: AsyncSession) -> ScheduleUpdateRepository:
    """This provides the ScheduleUpdate repository."""

    return ScheduleUpdateRepository(session=db_session)
