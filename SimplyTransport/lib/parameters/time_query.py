from datetime import datetime, time
from typing import Annotated

from litestar.params import PathParameter, QueryParameter

from ...domain.enums import DayOfWeek

StartTimeQuery = Annotated[
    time | None,
    QueryParameter(description="Start time, defaults to 10 minutes ago\n\nExample: 10:00:00"),
]
EndTimeQuery = Annotated[
    time | None,
    QueryParameter(description="End time, defaults to 60 minutes from now\n\nExample: 11:00:00"),
]
DayQuery = Annotated[DayOfWeek | None, QueryParameter(description="Day of week, defaults to today")]

ScheduledTimePath = Annotated[time, PathParameter(description="Format: HH:MM:SS")]

StartDateTimeQuery = Annotated[
    datetime | None,
    QueryParameter(description="Use data from this time onwards. Format: 2023-10-13T21:34:23Z"),
]
EndDateTimeQuery = Annotated[
    datetime | None,
    QueryParameter(description="Use data up to this time. Format: 2023-10-13T21:34:23Z"),
]
