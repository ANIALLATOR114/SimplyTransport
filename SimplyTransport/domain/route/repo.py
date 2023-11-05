from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy.ext.asyncio import AsyncSession
from .model import RouteModel
from advanced_alchemy.filters import LimitOffset, OrderBy
from advanced_alchemy import NotFoundError


class RouteRepository(SQLAlchemyAsyncRepository[RouteModel]):
    """Route repository."""

    async def list_by_short_name_or_long_name(
        self, search: str, limit_offset: LimitOffset
    ) -> list[RouteModel]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            RouteModel.short_name.istartswith(search) | RouteModel.long_name.istartswith(search), limit_offset, OrderBy(RouteModel.short_name, 'asc')
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    model_type = RouteModel


async def provide_route_repo(db_session: AsyncSession) -> RouteRepository:
    """This provides the Route repository."""

    return RouteRepository(session=db_session)
