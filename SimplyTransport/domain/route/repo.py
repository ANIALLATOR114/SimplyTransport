from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import RouteModel


class RouteRepository(SQLAlchemyAsyncRepository[RouteModel]):
    """Calendar repository."""

    model_type = RouteModel


async def provide_route_repo(db_session: AsyncSession) -> RouteRepository:
    """This provides the Route repository."""

    return RouteRepository(session=db_session)
