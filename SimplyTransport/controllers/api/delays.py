from datetime import time, datetime
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException, ValidationException
from litestar.params import Parameter

from ...timescale.ts_stop_times.model import TS_StopTime, TS_StopTimeDelayAggregated, TS_StopTimeForGraph
from ...timescale.ts_stop_times.repo import provide_ts_stop_time_repo, TSStopTimeRepository, MAXIMUM_TIMESTAMP
from ...lib.cache_keys import CacheKeys, key_builder_from_path

__all__ = ["DelaysController"]


class DelaysController(Controller):
    dependencies = {"repo": Provide(provide_ts_stop_time_repo)}

    @get(
        "/{stop_id:str}/{route_code:str}/{scheduled_time:str}/aggregated",
        cache=600,
        cache_key_builder=key_builder_from_path(
            CacheKeys.DELAYS_AGGREGATED_SPECIFIC_KEY_TEMPLATE,
            "stop_id",
            "route_code",
            "scheduled_time",
        ),
        summary="Get aggregated delay data for a route on a stop on a time",
        description=f"All queries will be limited to {MAXIMUM_TIMESTAMP.strftime('%Y-%m-%d')} onwards",
        raises=[NotFoundException, ValidationException],
    )
    async def get_aggregated_delay_on_stop_on_route_on_time(
        self,
        stop_id: str,
        route_code: str,
        repo: TSStopTimeRepository,
        scheduled_time: time = Parameter(required=True, description="Format: HH:MM:SS"),
        start_time: datetime | None = Parameter(
            required=False,
            description="Use data from this time onwards. Format: 2023-10-13T21:34:23Z",
        ),
        end_time: datetime | None = Parameter(
            required=False, description="Use data up to this time. Format: 2023-10-13T21:34:23Z"
        ),
    ) -> TS_StopTimeDelayAggregated:

        if start_time and end_time and start_time > end_time:
            raise ValidationException(
                detail=f"Start time cannot be greater than end time {start_time} > {end_time}"
            )

        result = await repo.get_aggregated_delay_on_stop_on_route_on_time(
            route_code, stop_id, scheduled_time, start_time, end_time
        )

        if not result:
            raise NotFoundException(detail=f"Delays not found for {stop_id}, {route_code}, {scheduled_time}")
        return result

    @get(
        "/{stop_id:str}/{route_code:str}/{scheduled_time:str}",
        cache=600,
        cache_key_builder=key_builder_from_path(
            CacheKeys.DELAYS_SPECIFIC_KEY_TEMPLATE,
            "stop_id",
            "route_code",
            "scheduled_time",
        ),
        summary="Get delay data for a route on a stop on a time",
        description=f"All queries will be limited to {MAXIMUM_TIMESTAMP.strftime('%Y-%m-%d')} onwards or 730 records",
        raises=[ValidationException],
    )
    async def get_delay_on_stop_on_route_on_time(
        self,
        stop_id: str,
        route_code: str,
        repo: TSStopTimeRepository,
        scheduled_time: time = Parameter(required=True, description="Format: HH:MM:SS"),
        start_time: datetime | None = Parameter(
            required=False,
            description="Use data from this time onwards. Format: 2023-10-13T21:34:23Z",
        ),
        end_time: datetime | None = Parameter(
            required=False,
            description="Use data up to this time. Format: 2023-10-13T21:34:23Z",
        ),
    ) -> list[TS_StopTime]:
        if start_time and end_time and start_time > end_time:
            raise ValidationException(
                detail=f"Start time cannot be greater than end time {start_time} > {end_time}"
            )

        result = await repo.get_delay_on_stop_on_route_on_time(
            route_code, stop_id, scheduled_time, start_time, end_time
        )

        return [TS_StopTime.model_validate(obj) for obj in result]

    @get(
        "/{stop_id:str}/{route_code:str}/{scheduled_time:str}/truncated",
        cache=600,
        cache_key_builder=key_builder_from_path(
            CacheKeys.DELAYS_SPECIFIC_SLIM_KEY_TEMPLATE,
            "stop_id",
            "route_code",
            "scheduled_time",
        ),
        summary="Get truncated delay data for a route on a stop on a time",
        description=f"All queries will be limited to {MAXIMUM_TIMESTAMP.strftime('%Y-%m-%d')} onwards or 730 records",
        raises=[ValidationException],
    )
    async def get_truncated_delay_on_stop_on_route_on_time(
        self,
        stop_id: str,
        route_code: str,
        repo: TSStopTimeRepository,
        scheduled_time: time = Parameter(required=True, description="Format: HH:MM:SS"),
        start_time: datetime | None = Parameter(
            required=False,
            description="Use data from this time onwards. Format: 2023-10-13T21:34:23Z",
        ),
        end_time: datetime | None = Parameter(
            required=False,
            description="Use data up to this time. Format: 2023-10-13T21:34:23Z",
        ),
    ) -> list[TS_StopTimeForGraph]:
        if start_time and end_time and start_time > end_time:
            raise ValidationException(
                detail=f"Start time cannot be greater than end time {start_time} > {end_time}"
            )

        result = await repo.get_truncated_delay_on_stop_on_route_on_time(
            route_code, stop_id, scheduled_time, start_time, end_time
        )

        return [TS_StopTimeForGraph.model_validate(obj) for obj in result]

    @get(
        "/{route_code:str}/aggregated",
        cache=600,
        cache_key_builder=key_builder_from_path(
            CacheKeys.DELAYS_AGGREGATED_ROUTE_KEY_TEMPLATE,
            "route_code",
        ),
        summary="Get aggregated delay data for a route",
        description=f"All queries will be limited to {MAXIMUM_TIMESTAMP.strftime('%Y-%m-%d')} onwards",
        raises=[NotFoundException, ValidationException],
    )
    async def get_aggregated_delay_on_route(
        self,
        route_code: str,
        repo: TSStopTimeRepository,
        start_time: datetime | None = Parameter(
            required=False,
            description="Use data from this time onwards. Format: 2023-10-13T21:34:23Z",
        ),
        end_time: datetime | None = Parameter(
            required=False,
            description="Use data up to this time. Format: 2023-10-13T21:34:23Z",
        ),
    ) -> TS_StopTimeDelayAggregated:
        if start_time and end_time and start_time > end_time:
            raise ValidationException(
                detail=f"Start time cannot be greater than end time {start_time} > {end_time}"
            )

        result = await repo.get_aggregated_delay_on_stop_on_route_on_time(
            route_code, start_time=start_time, end_time=end_time
        )

        if not result:
            raise NotFoundException(detail=f"Delays not found for {route_code}")
        return result
