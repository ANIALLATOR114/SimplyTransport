from pathlib import Path

import uvicorn
from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig
from litestar.di import Provide

from SimplyTransport.controllers import create_api_router, create_views_router
from SimplyTransport.lib import settings
from SimplyTransport.lib.db import services as db_services
from SimplyTransport.lib.db.database import sqlalchemy_plugin
from SimplyTransport.lib.openapi.openapiconfig import CustomOpenApiConfig
from SimplyTransport.cli import CLIPlugin
from SimplyTransport.lib.parameters.limitoffset import provide_limit_offset_pagination
from SimplyTransport.lib.parameters.orderby_shapes import provide_order_by_shapes

__all__ = ["create_app"]


def create_app() -> Litestar:
    env_settings = settings.BaseEnvSettings()

    return Litestar(
        debug=env_settings.DEBUG,
        route_handlers=[create_views_router(), create_api_router()],
        on_startup=[db_services.create_database],
        plugins=[sqlalchemy_plugin, CLIPlugin()],
        openapi_config=CustomOpenApiConfig(),
        template_config=TemplateConfig(
            directory=Path("templates"),
            engine=JinjaTemplateEngine,
        ),
        dependencies={
            "limit_offset": Provide(provide_limit_offset_pagination),
            "order_by_shape": Provide(provide_order_by_shapes),
        },
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )
