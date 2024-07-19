from enum import Enum


class StatisticType(str, Enum):
    # Type of statistic, should be less than 255 chars long

    # GTFS
    GTFS_RECORD_COUNTS = "gtfs.record.counts"

    # Operators
    OPERATOR_ROUTE_COUNTS = "operator.route.counts"
    OPERATOR_TRIP_COUNTS = "operator.trip.counts"

    # Stop Features
    STOP_FEATURE_COUNTS = "stop_features.feature.counts"
