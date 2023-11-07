import uvicorn
from litestar import Litestar
from litestar.di import Provide

from SimplyTransport.controllers import create_api_router, create_views_router
from SimplyTransport.lib import settings
from SimplyTransport.lib.db import services as db_services
from SimplyTransport.lib.db.database import sqlalchemy_plugin
from SimplyTransport.lib.openapi.openapiconfig import CustomOpenApiConfig
from SimplyTransport.lib.template_engine import CustomTemplateConfig
from SimplyTransport.lib.static_files import CustomStaticFilesConfigs
from SimplyTransport.lib.logging import provide_logger
from SimplyTransport.cli import CLIPlugin
from SimplyTransport.lib.parameters.limitoffset import provide_limit_offset_pagination

__all__ = ["create_app"]


def create_app() -> Litestar:

    return Litestar(
        debug=settings.app.DEBUG,
        route_handlers=[create_views_router(), create_api_router()],
        on_startup=[db_services.create_database],
        plugins=[sqlalchemy_plugin, CLIPlugin()],
        openapi_config=CustomOpenApiConfig(),
        template_config=CustomTemplateConfig(),
        static_files_config=CustomStaticFilesConfigs(),
        dependencies={
            "limit_offset": Provide(provide_limit_offset_pagination),
        },
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )
