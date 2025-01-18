from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .model import AgencyModel


class AgencyRepository(SQLAlchemyAsyncRepository[AgencyModel]):
    """Agency repository."""

    model_type = AgencyModel


async def provide_agency_repo(db_session: AsyncSession) -> AgencyRepository:
    """This provides the Agency repository."""

    return AgencyRepository(session=db_session)
