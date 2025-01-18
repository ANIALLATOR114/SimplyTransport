from enum import StrEnum


class EventType(StrEnum):
    # Type of event, should be less than 255 chars long

    # GTFS
    GTFS_DATABASE_UPDATED = "gtfs.database.updated"

    # Realtime
    REALTIME_DATABASE_UPDATED = "realtime.database.updated"

    # Realtime Vehicles
    REALTIME_VEHICLES_DATABASE_UPDATED = "realtime_vehicles.database.updated"

    # Stop Features
    STOP_FEATURES_DATABASE_UPDATED = "stop_features.database.updated"

    # Database Statistics
    DATABASE_STATISTICS_UPDATED = "database_statistics.updated"

    # Cleanup
    CLEANUP_EVENTS_DELETED = "cleanup.events.deleted"
    CLEANUP_DELAYS_DELETED = "cleanup.delays.deleted"

    # Time Series
    RECORD_TS_STOP_TIMES = "timeseries.delays.recorded"
