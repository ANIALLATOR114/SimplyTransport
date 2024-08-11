from litestar.openapi import OpenAPIConfig, OpenAPIController
from .. import settings
from .tags import Tags

DESCRIPTION = """SimplyTransport - An API for retrieving transport information.

This API provides access to transport data for agencies, routes, stops, trips, stop times, calendars, calendar dates, shapes, realtime information, schedules, maps, and statistics.

These endpoints are extensions of the GTFS standard with some additional endpoints for additional features such as maps and statistics.
"""


class MyOpenAPIController(OpenAPIController):
    path = "/docs"


def custom_open_api_config() -> OpenAPIConfig:
    return OpenAPIConfig(
        title=settings.app.NAME,
        version=settings.app.VERSION,
        openapi_controller=MyOpenAPIController,
        create_examples=True,
        description=DESCRIPTION,
        tags=Tags().list_all_tags(),
    )
