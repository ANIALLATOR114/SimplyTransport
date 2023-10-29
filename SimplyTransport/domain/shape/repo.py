from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import ShapeModel


class ShapeRepository(SQLAlchemyAsyncRepository[ShapeModel]):
    """Stop repository."""

    model_type = ShapeModel


async def provide_shape_repo(db_session: AsyncSession) -> ShapeRepository:
    """This provides the Shape repository."""

    return ShapeRepository(session=db_session)
