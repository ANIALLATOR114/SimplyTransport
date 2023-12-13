from enum import Enum


class EventType(str, Enum):
    # Type of event, should be less than 255 chars long

    # GTFS
    GTFS_DATABASE_UPDATED = "gtfs.database.updated"

    # Realtime
    REALTIME_DATABASE_UPDATED = "realtime.database.updated"

