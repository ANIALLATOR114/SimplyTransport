from litestar import Controller, get
from litestar.response import Template
from litestar.di import Provide

from ..lib.logging.logging import provide_logger
from ..domain.database_statistics.repo import DatabaseStatisticRepository, provide_database_statistic_repo
from ..domain.services.statistics_service import StatisticsService, provide_statistics_service
from ..domain.database_statistics.statistic_type import StatisticType


__all__ = [
    "StatsController",
]

logger = provide_logger(__name__)


class StatsController(Controller):
    dependencies = {
        "stats_repo": Provide(provide_database_statistic_repo),
        "stats_service": Provide(provide_statistics_service),
    }

    @get("/static/most-recent", cache=60, name="stats.static_stats")
    async def static_stats(
        self, stats_repo: DatabaseStatisticRepository, stats_service: StatisticsService
    ) -> Template:

        stats = await stats_repo.get_statistics_most_recent_by_type(StatisticType.GTFS_RECORD_COUNTS)
        stats_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(stats)

        return Template(
            template_name="stats/static_data.html",
            context={"stats_with_percentages": stats_with_percentages},
        )

    @get("/operators/most-recent", cache=60, name="stats.operator_stats")
    async def operator_stats(
        self, stats_repo: DatabaseStatisticRepository, stats_service: StatisticsService
    ) -> Template:

        routes = await stats_repo.get_statistics_most_recent_by_type(StatisticType.OPERATOR_ROUTE_COUNTS)
        routes_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(
            routes, total_row_key="Total Routes"
        )

        trips = await stats_repo.get_statistics_most_recent_by_type(StatisticType.OPERATOR_TRIP_COUNTS)
        trips_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(
            trips, total_row_key="Total Trips"
        )

        return Template(
            template_name="stats/operator_data.html",
            context={
                "routes_with_percentages": routes_with_percentages,
                "trips_with_percentages": trips_with_percentages,
            },
        )

    @get("/stop-features/most-recent", cache=60, name="stats.stop_features")
    async def stop_features(
        self, stats_repo: DatabaseStatisticRepository, stats_service: StatisticsService
    ) -> Template:
        stats = await stats_repo.get_statistics_most_recent_by_type(StatisticType.STOP_FEATURE_COUNTS)
        stats_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(
            stats, total_row_key="Total Stops"
        )

        return Template(
            template_name="stats/stop_features_data.html",
            context={"stats_with_percentages": stats_with_percentages},
        )
