from litestar.openapi import OpenAPIConfig, OpenAPIController
from litestar.openapi.spec import Components, SecurityScheme, Tag
from SimplyTransport.lib import settings


class MyOpenAPIController(OpenAPIController):
    path = "/docs"


def CustomOpenApiConfig() -> OpenAPIConfig:
    return OpenAPIConfig(
        title=settings.app.NAME,
        version=settings.app.VERSION,
        openapi_controller=MyOpenAPIController,
        create_examples=True,
        description="SimplyTransport API - An API for retrieving transport information",
        tags=[
            Tag(name="Agency", description="Agencies are the operators of transport services"),
            Tag(
                name="Route",
                description="Routes are a group of trips that display to riders as a single service",
            ),
            Tag(
                name="Stop",
                description="Stops are the places where transport services pick up and dropoff riders",
            ),
            Tag(
                name="Trip",
                description="Trips are a sequence of two or more stops that occur at specific times",
            ),
            Tag(
                name="StopTime",
                description="StopTimes are when a vehicle arrives at and departs from stops for each trip.",
            ),
            Tag(name="Calendar", description="Calendars are the weekly schedules of a route"),
            Tag(
                name="CalendarDate", description="CalendarDates are the exceptions to a calendar"
            ),
            Tag(
                name="Shape",
                description="Shapes define the path that a vehicle travels along a route",
            ),
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
