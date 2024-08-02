from typing import List
from SimplyTransport.domain.database_statistics.model import (
    DatabaseStatisticModel,
    DatabaseStatisticWithPercentage,
)
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

    def convert_stats_to_stats_with_percentage_totals(
        self,
        stats: List[DatabaseStatisticModel],
        decimals_places_to_round: int = 2,
        add_totals_row: bool = True,
        total_row_key: str = "Total Rows",
        total_override: int | None = None,
    ) -> List[DatabaseStatisticWithPercentage]:
        """
        Converts a list of DatabaseStatisticModel objects to a list of DatabaseStatisticWithPercentage objects,
        with the addition of a totals row if specified.

        Args:
            stats (List[DatabaseStatisticModel]): The list of DatabaseStatisticModel objects to convert.
            decimals_places_to_round (int, optional): The number of decimal places to round the percentages to.
                Defaults to 2.
            add_totals_row (bool, optional): Whether to add a totals row to the resulting list. Defaults to True.
            total_row_key (str, optional): The key for the totals row. Defaults to "Total Rows".
            total_override (int | None, optional): An optional override for the total number of rows. If provided,
                this value will be used instead of calculating the sum of the values in the stats list. Defaults to None.

        Returns:
            List[DatabaseStatisticWithPercentage]: The list of DatabaseStatisticWithPercentage objects, including
            the totals row if specified.
        """
        if total_override is None:
            total_rows = sum(stat.value for stat in stats)
        else:
            total_rows = total_override
        stats_with_percentages: List[DatabaseStatisticWithPercentage] = []

        if add_totals_row:
            stat_for_totals = DatabaseStatisticWithPercentage(
                key=total_row_key,
                value=total_rows,
                percentage=100,
            )
            stats_with_percentages.append((stat_for_totals))

        for stat in stats:
            percentage = round((stat.value / total_rows) * 100, decimals_places_to_round)
            percentage_stat = DatabaseStatisticWithPercentage(
                key=stat.key,
                value=stat.value,
                percentage=percentage,
            )
            stats_with_percentages.append((percentage_stat))
        return stats_with_percentages

    def sort_stats_by_percentage(
        self, stats: List[DatabaseStatisticWithPercentage], descending: bool = True
    ) -> List[DatabaseStatisticWithPercentage]:
        """
        Sorts a list of DatabaseStatisticWithPercentage objects based on their percentage value.

        Args:
            stats (List[DatabaseStatisticWithPercentage]): The list of statistics to be sorted.
            descending (bool, optional): Specifies whether the sorting should be in descending order. 
                Defaults to True.

        Returns:
            List[DatabaseStatisticWithPercentage]: The sorted list of statistics.
        """
        return sorted(stats, key=lambda x: x.percentage, reverse=descending)


async def provide_statistics_service(db_session: AsyncSession) -> StatisticsService:
    """
    Provides a StatisticsService instance.

    Args:
        db_session (AsyncSession): The database session.

    Returns:
        StatisticsService: A StatisticsService instance.
    """
    return StatisticsService(database_statistic_repository=DatabaseStatisticRepository(session=db_session))
