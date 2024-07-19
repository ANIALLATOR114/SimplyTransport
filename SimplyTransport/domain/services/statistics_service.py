from SimplyTransport.domain.database_statistics.statistic_type import StatisticType
from ..database_statistics.repo import DatabaseStatisticRepository

from sqlalchemy.ext.asyncio import AsyncSession


class StatisticsService:
    def __init__(
        self,
        database_statistic_repository: DatabaseStatisticRepository,
    ):
        self.database_statistic_repository = database_statistic_repository


    async def update_all_statistics(self) -> None:
        """Updates all statistics."""

        await self.update_gtfs_row_counts()
        await self.update_operator_row_counts()
        await self.update_stop_feature_counts()


    async def update_gtfs_row_counts(self) -> None:
        """Updates the GTFS row counts."""
        
        row_counts = await self.database_statistic_repository.get_gtfs_record_counts()
        await self.database_statistic_repository.add_row_counts(row_counts, StatisticType.GTFS_RECORD_COUNTS)

    async def update_operator_row_counts(self) -> None:
        """Updates the operator row counts."""
        
        route_counts = await self.database_statistic_repository.get_operator_route_counts()
        await self.database_statistic_repository.add_row_counts(
            route_counts, StatisticType.OPERATOR_ROUTE_COUNTS
        )

        trip_counts = await self.database_statistic_repository.get_operator_trip_counts()
        await self.database_statistic_repository.add_row_counts(
            trip_counts, StatisticType.OPERATOR_TRIP_COUNTS
        )

    async def update_stop_feature_counts(self) -> None:
        """Updates the stop feature counts."""
        
        stop_feature_counts = await self.database_statistic_repository.get_stop_feature_counts()
        await self.database_statistic_repository.add_row_counts(
            stop_feature_counts, StatisticType.STOP_FEATURE_COUNTS
        )


async def provide_statistics_service(db_session: AsyncSession) -> StatisticsService:
    """
    Provides a StatisticsService instance.

    Args:
        db_session (AsyncSession): The database session.

    Returns:
        StatisticsService: A StatisticsService instance.
    """
    return StatisticsService(
        database_statistic_repository=DatabaseStatisticRepository(session=db_session)
    )