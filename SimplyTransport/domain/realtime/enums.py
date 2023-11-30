from enum import Enum


class ScheduleRealtionship(str, Enum):
    SCHEDULED = "SCHEDULED"
    SKIPPED = "SKIPPED"
    NO_DATA = "NO_DATA"
    UNSCHEDULED = "UNSCHEDULED"
    ADDED = "ADDED"
    CANCELED = "CANCELED"


class OnTimeStatus(str, Enum):
    EARLY = "EARLY"
    ON_TIME = "ON_TIME"
    LATE = "LATE"
    UNKNOWN = "UNKNOWN"
    NO_DATA = "NO_DATA"