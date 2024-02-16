from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import ShapeModel


class ShapeRepository(SQLAlchemyAsyncRepository[ShapeModel]):
    """Stop repository."""

    async def get_shapes_by_shape_id(self, shape_id: str) -> list[ShapeModel]:
        """Get shapes by shape_id."""

        return await self.list(ShapeModel.shape_id == shape_id)

    async def get_shapes_by_shape_ids(self, shape_ids: list[str]) -> list[ShapeModel]:
        """Get shapes by shape_ids."""

        result = await self.session.execute(select(ShapeModel).filter(ShapeModel.shape_id.in_(shape_ids)))
        return result.scalars().all()

    model_type = ShapeModel


async def provide_shape_repo(db_session: AsyncSession) -> ShapeRepository:
    """This provides the Shape repository."""

    return ShapeRepository(session=db_session)
