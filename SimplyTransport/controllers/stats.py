from litestar import Controller, get
from litestar.di import Provide
from litestar.response import Template

from ..domain.database_statistics.repo import DatabaseStatisticRepository, provide_database_statistic_repo
from ..domain.database_statistics.statistic_type import StatisticType
from ..domain.services.statistics_service import StatisticsService, provide_statistics_service
from ..domain.stop.repo import StopRepository, provide_stop_repo
from ..lib.logging.logging import provide_logger

__all__ = [
    "StatsController",
]

logger = provide_logger(__name__)


class StatsController(Controller):
    dependencies = {
        "stats_repo": Provide(provide_database_statistic_repo),
        "stats_service": Provide(provide_statistics_service),
        "stop_repo": Provide(provide_stop_repo),
    }

    @get("/static/most-recent", cache=60, name="stats.static_stats")
    async def static_stats(
        self, stats_repo: DatabaseStatisticRepository, stats_service: StatisticsService
    ) -> Template:
        stats = await stats_repo.get_statistics_most_recent_by_type(StatisticType.GTFS_RECORD_COUNTS)
        stats_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(stats)
        stats_with_percentages = stats_service.sort_stats_by_value(stats_with_percentages)

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
        routes_with_percentages = stats_service.sort_stats_by_value(routes_with_percentages)

        trips = await stats_repo.get_statistics_most_recent_by_type(StatisticType.OPERATOR_TRIP_COUNTS)
        trips_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(
            trips, total_row_key="Total Trips"
        )
        trips_with_percentages = stats_service.sort_stats_by_value(trips_with_percentages)

        return Template(
            template_name="stats/operator_data.html",
            context={
                "routes_with_percentages": routes_with_percentages,
                "trips_with_percentages": trips_with_percentages,
            },
        )

    @get("/stop-features/most-recent", cache=60, name="stats.stop_features")
    async def stop_features(
        self,
        stats_repo: DatabaseStatisticRepository,
        stats_service: StatisticsService,
        stop_repo: StopRepository,
    ) -> Template:
        stats = await stats_repo.get_statistics_most_recent_by_type(StatisticType.STOP_FEATURE_COUNTS)
        total_stop_count = await stop_repo.count()

        stats_with_percentages = stats_service.convert_stats_to_stats_with_percentage_totals(
            stats, total_row_key="Total Stops", total_override=total_stop_count
        )
        stats_with_percentages = stats_service.sort_stats_by_value(stats_with_percentages)

        return Template(
            template_name="stats/stop_features_data.html",
            context={"stats_with_percentages": stats_with_percentages},
        )
