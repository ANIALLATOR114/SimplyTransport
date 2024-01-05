from enum import Enum


class ExceptionType(str, Enum):
    added = "added"
    removed = "removed"


class RouteType(int, Enum):
    TRAM = 0
    SUBWAY = 1
    RAIL = 2
    BUS = 3
    FERRY = 4
    CABLE_TRAM = 5
    AERIAL_LIFT = 6
    FUNICULAR = 7
    TROLLYBUS = 11
    MONORAIL = 12


class DayOfWeek(int, Enum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class LocationType(int, Enum):
    STOP = 0
    STATION = 1
    ENTRANCE_EXIT = 2
    GENERIC_NODE = 3
    BOARDING_AREA = 4


class PickupType(int, Enum):
    """Indicates pickup method"""

    REGULARLY_SCHEDULED = 0
    NO_PICKUP = 1
    MUST_PHONE_AGENCY = 2
    MUST_COORDINATE_WITH_DRIVER = 3


class DropoffType(int, Enum):
    """Indicates dropoff method"""

    REGULARLY_SCHEDULED = 0
    NO_DROP_OFF = 1
    MUST_PHONE_AGENCY = 2
    MUST_COORDINATE_WITH_DRIVER = 3


class Timepoint(int, Enum):
    """Indicates if arrival and departure times for a stop are strictly adhered to by the vehicle or if they are instead approximate and/or interpolated times
    A null value here means EXACT
    """

    APPROXIMATE = 0
    EXACT = 1


class StopType(str, Enum):
    """Type marked (MKD) indicates the stops is marked with a physical
    transport infrastructure item (pole, shelter or real time unit). Customs
    and Practice (CUS) indicates there is no such infrastructure
    """

    MARKED = "MKD"
    CUSTOMS = "CUS"
    UNKNOWN = "Unknown"


class Bearing(str, Enum):
    """Bearing indicates the direction that traffic travels"""

    NORTH = "N"
    NORTH_EAST = "NE"
    EAST = "E"
    SOUTH_EAST = "SE"
    SOUTH = "S"
    SOUTH_WEST = "SW"
    WEST = "W"
    NORTH_WEST = "NW"
    UNKNOWN = "U"
