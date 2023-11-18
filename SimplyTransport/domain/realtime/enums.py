from enum import Enum


class ScheduleRealtionship(str, Enum):
    SCHEDULED = "SCHEDULED"
    SKIPPED = "SKIPPED"
    NO_DATA = "NO_DATA"
    UNSCHEDULED = "UNSCHEDULED"
    ADDED = "ADDED"
    CANCELED = "CANCELED"
