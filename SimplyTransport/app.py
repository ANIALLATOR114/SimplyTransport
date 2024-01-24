import uvicorn
from litestar import Litestar
from litestar.di import Provide

from .controllers import create_api_router, create_views_router
from .lib import settings
from SimplyTransport.lib.db import services as db_services
from .lib.db.database import sqlalchemy_plugin
from .lib.openapi.openapiconfig import CustomOpenApiConfig
from .lib.template_engine import CustomTemplateConfig
from .lib.static_files import CustomStaticFilesConfigs
from .lib.cache import cache_config
from .cli import CLIPlugin
from .lib.parameters.limitoffset import provide_limit_offset_pagination


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
        response_cache_config=cache_config,
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )
