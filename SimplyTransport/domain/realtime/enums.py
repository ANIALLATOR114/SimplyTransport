from enum import StrEnum


class ScheduleRealtionship(StrEnum):
    SCHEDULED = "SCHEDULED"
    SKIPPED = "SKIPPED"
    NO_DATA = "NO_DATA"
    UNSCHEDULED = "UNSCHEDULED"
    ADDED = "ADDED"
    CANCELED = "CANCELED"


class OnTimeStatus(StrEnum):
    EARLY = "EARLY"
    ON_TIME = "ON_TIME"
    LATE = "LATE"
    UNKNOWN = "UNKNOWN"
