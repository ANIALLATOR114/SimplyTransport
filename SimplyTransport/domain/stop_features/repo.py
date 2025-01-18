from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession

from .model import StopFeatureModel


class StopFeatureRepository(SQLAlchemyAsyncRepository[StopFeatureModel]):
    """Stop Feature repository."""

    model_type = StopFeatureModel


async def provide_stop_feature_repo(db_session: AsyncSession) -> StopFeatureRepository:
    """This provides the Stop Feature repository."""

    return StopFeatureRepository(session=db_session)
