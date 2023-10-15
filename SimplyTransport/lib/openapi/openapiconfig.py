from litestar.openapi import OpenAPIConfig
from SimplyTransport.lib import settings
from litestar.openapi.spec import Components, SecurityScheme, Tag


def CustomOpenApiConfig() -> OpenAPIConfig:
    env_settings = settings.BaseEnvSettings()
    return OpenAPIConfig(
        title=env_settings.OPENAPI_TITLE,
        version=env_settings.OPENAPI_VERSION,
        description="SimplyTransport API - A simple API for retrieving transport information.",
        tags=[
            Tag(name="public", description="These endpoints are public without authentication"),
            Tag(name="auth", description="These endpoints require authentication"),
            Tag(name="Agency", description="Agencies are the operators of transport services"),
            Tag(name="Route", description="Routes are the lines that transport services follow"),
            Tag(name="Stop", description="Stops are the places where transport services stop"),
            Tag(name="Trip", description="Trips are the instances of a route"),
            Tag(
                name="StopTime", description="StopTimes are the times that a trip stops at a stop"
            ),
            Tag(name="Calendar", description="Calendars are the schedules of a route"),
            Tag(
                name="CalendarDate", description="CalendarDates are the exceptions to a calendar"
            ),
            Tag(name="Shapes", description="Shapes are the points that a route follows"),
        ],
        security=[{"BearerToken": []}],
        components=Components(
            security_schemes={
                "BearerToken": SecurityScheme(
                    type="http",
                    scheme="bearer",
                )
            },
        ),
    )
