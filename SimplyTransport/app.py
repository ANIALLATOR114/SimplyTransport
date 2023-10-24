from pathlib import Path
from typing import Any

import uvicorn
from litestar import Litestar
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

from SimplyTransport.controllers import create_api_router, create_views_router
from SimplyTransport.lib import settings
from SimplyTransport.lib.db import services as db_services
from SimplyTransport.lib.db.database import sqlalchemy_plugin
from SimplyTransport.lib.openapi.openapiconfig import CustomOpenApiConfig
from SimplyTransport.cli import CLIPlugin

__all__ = ["create_app"]


def create_app(**kwargs: Any) -> Litestar:
    env_settings = settings.BaseEnvSettings(**kwargs)

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
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )
