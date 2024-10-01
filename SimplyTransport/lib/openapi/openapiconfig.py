from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import (
    StoplightRenderPlugin,
    YamlRenderPlugin,
    JsonRenderPlugin,
    RapidocRenderPlugin,
    RedocRenderPlugin,
    ScalarRenderPlugin,
    SwaggerRenderPlugin,
)
from .. import settings
from .tags import Tags

DESCRIPTION = """SimplyTransport - An API for retrieving transport information.

This API provides access to transport data for agencies, routes, stops, trips, stop times, calendars, calendar dates, shapes, realtime information, schedules, maps, and statistics.

These endpoints are extensions of the GTFS standard with some additional endpoints for additional features such as maps and statistics.
"""

favicon = "<link rel='icon' type='image/png' href='/favicon.ico'>"
render_plugins = [
    StoplightRenderPlugin(favicon=favicon),
    YamlRenderPlugin(favicon=favicon),
    JsonRenderPlugin(favicon=favicon),
    RapidocRenderPlugin(favicon=favicon),
    RedocRenderPlugin(favicon=favicon),
    ScalarRenderPlugin(favicon=favicon),
    SwaggerRenderPlugin(favicon=favicon),
]


def custom_open_api_config() -> OpenAPIConfig:
    return OpenAPIConfig(
        title=settings.app.NAME,
        version=settings.app.VERSION,
        path="/docs",
        render_plugins=render_plugins,
        create_examples=False,
        description=DESCRIPTION,
        tags=Tags().list_all_tags(),
    )
