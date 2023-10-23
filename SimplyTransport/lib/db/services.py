import SimplyTransport.lib.db.database as _db
from litestar.contrib.sqlalchemy.base import UUIDBase

# Import all models here so that they are registered with SQLAlchemy
from SimplyTransport.domain.example import ExampleModel
from SimplyTransport.domain.agency.model import AgencyModel
from SimplyTransport.domain.calendar.model import CalendarModel


async def create_database() -> None:
    async with _db.sqlalchemy_config.get_engine().begin() as conn:
        await conn.run_sync(UUIDBase.metadata.create_all)
