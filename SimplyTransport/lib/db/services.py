import SimplyTransport.lib.db.database as _db
from litestar.contrib.sqlalchemy.base import UUIDBase

# Import all models here so that they are registered with SQLAlchemy
from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.calendar.model import CalendarModel
from SimplyTransport.domain.calendar_dates.model import CalendarDateModel
from SimplyTransport.domain.route.model import RouteModel


async def create_database() -> None:
    try:
        async with _db.sqlalchemy_config.get_engine().begin() as conn:
            await conn.run_sync(UUIDBase.metadata.create_all)
    except ConnectionRefusedError as e:
        print(e)
        print(
            f"\nDatabase connection refused. Please ensure the database is running and accessible.\nURL: {_db.sqlalchemy_config.get_engine().url}\n"
        )
        raise e
