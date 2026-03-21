from enum import StrEnum


class ScheduleRealtionship(StrEnum):
    SCHEDULED = "SCHEDULED"
    SKIPPED = "SKIPPED"
    NO_DATA = "NO_DATA"
    UNSCHEDULED = "UNSCHEDULED"
    ADDED = "ADDED"
    CANCELED = "CANCELED"
    REPLACEMENT = "REPLACEMENT"
    DUPLICATED = "DUPLICATED"
    NEW = "NEW"
    DELETED = "DELETED"


# Trip-level relationships that remove the trip from normal service
REMOVED_TRIP_RELATIONSHIPS: frozenset[str] = frozenset[str](
    {ScheduleRealtionship.CANCELED.value, ScheduleRealtionship.DELETED.value}
)


class OnTimeStatus(StrEnum):
    EARLY = "EARLY"
    ON_TIME = "ON_TIME"
    LATE = "LATE"
    UNKNOWN = "UNKNOWN"
