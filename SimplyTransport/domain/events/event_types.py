from enum import Enum


class EventType(str, Enum):
    # Type of event, should be less than 255 chars long

    # GTFS
    GTFS_DATABASE_UPDATED = "gtfs.database.updated"

    # Realtime
    REALTIME_DATABASE_UPDATED = "realtime.database.updated"

    # Realtime Vehicles
    REALTIME_VEHICLES_DATABASE_UPDATED = "realtime_vehicles.database.updated"

    # Stop Features
    STOP_FEATURES_DATABASE_UPDATED = "stop_features.database.updated"
