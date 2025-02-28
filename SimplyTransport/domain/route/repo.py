import asyncio

from advanced_alchemy import NotFoundError
from advanced_alchemy.filters import LimitOffset, OrderBy
from litestar.contrib.sqlalchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from SimplyTransport.lib.cache import RedisService
from SimplyTransport.lib.cache_keys import CacheKeys

from ..stop_times.model import StopTimeModel
from ..trip.model import TripModel
from .model import RouteModel


class RouteRepository(SQLAlchemyAsyncRepository[RouteModel]):
    """Route repository."""

    model_type = RouteModel
    cache: RedisService

    def __init__(self, session: AsyncSession, *, cache: RedisService):
        self.cache = cache
        super().__init__(session=session)

    async def list_by_short_name_or_long_name(
        self, search: str, limit_offset: LimitOffset
    ) -> tuple[list[RouteModel], int]:
        """List stops that start with name/code."""

        results, total = await self.list_and_count(
            RouteModel.short_name.istartswith(search) | RouteModel.long_name.istartswith(search),
            limit_offset,
            OrderBy(RouteModel.short_name, "asc"),
        )

        if total == 0:
            raise NotFoundError()

        return results, total

    async def get_routes_by_stop_id(self, stop_id: str) -> list[RouteModel]:
        """Get routes by stop_id."""

        return await self.list(
            RouteModel.trips.any(TripModel.stop_times.any(StopTimeModel.stop_id == stop_id))
        )

    async def get_routes_by_stop_id_through_cache(self, stop_id: str) -> list[RouteModel]:
        """Through cache for get_routes_by_stop_id."""

        cache_key = CacheKeys.Routes.ROUTES_BY_STOP_ID_KEY_TEMPLATE.format(stop_id=stop_id)
        cached_routes = await self.cache.get(cache_key)
        if cached_routes:
            route_dicts = self.cache.deserialize(cached_routes)
            return [RouteModel(**route_dict) for route_dict in route_dicts]

        routes = await self.get_routes_by_stop_id(stop_id)
        routes_json = self.cache.serialize(
            [{k: v for k, v in route.__dict__.items() if not k.startswith("_")} for route in routes]
        )
        await self.cache.set(cache_key, routes_json, expiration=86400)
        return routes

    async def get_routes_by_stop_ids(self, stop_ids: list[str]) -> dict[str, list[RouteModel]]:
        """Get routes by stop_ids."""

        tasks = [self.get_routes_by_stop_id_through_cache(stop_id) for stop_id in stop_ids]
        routes = await asyncio.gather(*tasks)
        return dict(zip(stop_ids, routes, strict=False))

    async def get_routes_by_stop_id_with_agency(self, stop_id: str) -> list[RouteModel]:
        """Get routes by stop_id with agency."""

        return await self.list(
            RouteModel.trips.any(TripModel.stop_times.any(StopTimeModel.stop_id == stop_id)),
            statement=select(RouteModel).options(joinedload(RouteModel.agency)),
        )

    async def get_by_id_with_agency(self, id: str) -> RouteModel:
        """Get a route by id with agency."""

        return await self.get(id, statement=select(RouteModel).options(joinedload(RouteModel.agency)))

    async def get_with_agencies(self) -> list[RouteModel]:
        """Get all routes with agencies"""

        return await self.list(statement=select(RouteModel).options(joinedload(RouteModel.agency)))

    async def get_with_agencies_by_agency_id(self, agency_id: str) -> list[RouteModel]:
        """Get all routes with agencies by agency_id"""

        return await self.list(
            RouteModel.agency_id == agency_id,
            statement=select(RouteModel).options(joinedload(RouteModel.agency)),
        )


async def provide_route_repo(db_session: AsyncSession, redis_service: RedisService) -> RouteRepository:
    """This provides the Route repository."""

    return RouteRepository(session=db_session, cache=redis_service)
