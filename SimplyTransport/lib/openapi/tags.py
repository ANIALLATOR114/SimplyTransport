from litestar.openapi.spec import Tag


class Tags:
    AGENCY = Tag(
        name="Agency",
        description="Agencies are the operators of transport services",
    )
    ROUTE = Tag(
        name="Route",
        description="Routes are a group of trips that display to riders as a single service",
    )
    STOP = Tag(
        name="Stop",
        description="Stops are the places where transport services pick up and dropoff riders",
    )
    TRIP = Tag(
        name="Trip",
        description="Trips are a sequence of two or more stops that occur at specific times",
    )
    STOP_TIME = Tag(
        name="StopTime",
        description="StopTimes are when a vehicle arrives at and departs from stops for each trip.",
    )
    CALENDAR = Tag(
        name="Calendar",
        description="Calendars are the weekly schedules of a route",
    )
    CALENDAR_DATE = Tag(
        name="CalendarDate",
        description="CalendarDates are the exceptions to a calendar",
    )
    SHAPE = Tag(
        name="Shape",
        description="Shapes define the path that a vehicle travels along a route",
    )
    REALTIME = Tag(
        name="Realtime",
        description="Realtime information provides the current status of a STOP",
    )
    SCHEDULE = Tag(
        name="Schedule",
        description="Schedule provides the static schedule of a STOP",
    )
    MAP = Tag(
        name="Map",
        description="Maps will be returned as iframes",
    )
    STATISTICS = Tag(
        name="Statistics",
        description="Statistics provides summaries of the data",
    )
    EVENTS = Tag(
        name="Events",
        description="Events are records of tthings that have happened in the system",
    )

    @classmethod
    def list_all_tags(cls) -> list[Tag]:
        return [value for key, value in cls.__dict__.items() if isinstance(value, Tag)]
