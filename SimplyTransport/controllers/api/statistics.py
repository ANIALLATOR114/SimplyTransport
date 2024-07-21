import datetime
from litestar import Controller, get
from litestar.di import Provide
from litestar.exceptions import NotFoundException

from SimplyTransport.domain.database_statistics.statistic_type import StatisticType

from ...domain.database_statistics.model import DatabaseStatistic
from ...domain.database_statistics.repo import DatabaseStatisticRepository, provide_database_statistic_repo

__all__ = ["StatisticsController"]


class StatisticsController(Controller):
    dependencies = {"repo": Provide(provide_database_statistic_repo)}

    @get(
        "/{key:str}",
        summary="Get the most recent statistics for a given type",
        raises=[NotFoundException],
    )
    async def get_gtfs_most_recent(
        self, repo: DatabaseStatisticRepository, key: StatisticType
    ) -> list[DatabaseStatistic]:
        result = await repo.get_statistics_most_recent_by_key(key)

        if not result:
            raise NotFoundException(detail=f"Statistics not found for {key.value}")
        
        return [DatabaseStatistic.model_validate(obj) for obj in result]
    
    @get(
        "/{key:str}/{date:date}",
        summary="Get the statistics for a given type on a given day",
        description="Date format = YYYY-MM-DD",
        raises=[NotFoundException],
    )
    async def get_gtfs_by_day(
        self, repo: DatabaseStatisticRepository, key: StatisticType, date: datetime.date
    ) -> list[DatabaseStatistic]:
        result = await repo.get_statistics_by_key_and_date(key, date)

        if not result:
            raise NotFoundException(detail=f"Statistics not found for {key.value} on {date}")
        
        return [DatabaseStatistic.model_validate(obj) for obj in result]
