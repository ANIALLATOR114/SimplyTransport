from datetime import time
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException
from litestar.params import Parameter

from ...timescale.ts_stop_times.model import TS_StopTimeDelay
from ...timescale.ts_stop_times.repo import provide_ts_stop_time_repo, TSStopTimeRepository
from ...lib.cache_keys import CacheKeys, key_builder_from_path

__all__ = ["DelaysController"]


class DelaysController(Controller):
    dependencies = {"repo": Provide(provide_ts_stop_time_repo)}

    @get(
        "/{stop_id:str}/{route_code:str}/{scheduled_time:str}",
        cache=600,
        cache_key_builder=key_builder_from_path(
            CacheKeys.DELAYS_SPECIFIC_KEY_TEMPLATE,
            "stop_id",
            "route_code",
            "scheduled_time",
        ),
        summary="Get delay on stop on route on time",
        raises=[NotFoundException],
    )
    async def get__delay_on_stop_on_route_on_time(
        self,
        stop_id: str,
        route_code: str,
        repo: TSStopTimeRepository,
        scheduled_time: str = Parameter(required=True, description="Format: HH:MM:SS"),
    ) -> TS_StopTimeDelay:

        scheduled_time_parsed = time.fromisoformat(scheduled_time)
        result = await repo.get_delay_on_stop_on_route_on_time(route_code, stop_id, scheduled_time_parsed)

        if not result:
            raise NotFoundException(detail=f"Delays not found for {stop_id}, {route_code}, {scheduled_time}")
        return result
