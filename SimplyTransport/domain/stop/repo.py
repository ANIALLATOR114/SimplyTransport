from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import StopModel
from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy import NotFoundError


class StopRepository(SQLAlchemyAsyncRepository[StopModel]):
    """Stop repository."""

    model_type = StopModel

    async def get_by_code(self, code: str) -> StopModel:
        """Get a stop by code."""

        return await self.get_one(code=code)

    async def list_by_name_or_code(
        self, search: str, limit_offset: LimitOffset
    ) -> list[StopModel]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            StopModel.name.istartswith(search) | StopModel.code.istartswith(search), limit_offset, OrderBy(StopModel.code, 'asc')
        )

        if total == 0:
            raise NotFoundError()

        return results, total


async def provide_stop_repo(db_session: AsyncSession) -> StopRepository:
    """This provides the Stop repository."""

    return StopRepository(session=db_session)
