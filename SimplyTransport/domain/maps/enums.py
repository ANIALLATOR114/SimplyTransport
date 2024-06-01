from enum import Enum


class StaticStopMapTypes(str, Enum):
    ALL_STOPS = "All Stops"
    REALTIME_DISPLAYS = "Realtime Displays"
    SHELTERED_STOPS = "Sheltered Stops"
    UNSURVEYED = "Unsurveyed"
