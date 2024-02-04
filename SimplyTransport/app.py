import uvicorn
from litestar import Litestar
from litestar.di import Provide

from SimplyTransport.lib import exception_handlers

from .controllers import create_api_router, create_views_router
from .lib import settings
from SimplyTransport.lib.db import services as db_services
from .lib.db.database import sqlalchemy_plugin
from .lib.openapi.openapiconfig import custom_open_api_config
from .lib.template_engine import custom_template_config
from .lib.static_files import custom_static_files_config
from .lib.cache import cache_config
from .cli import CLIPlugin
from .lib.parameters.limitoffset import provide_limit_offset_pagination


def create_app() -> Litestar:
    return Litestar(
        debug=settings.app.DEBUG,
        route_handlers=[create_views_router(), create_api_router()],
        on_startup=[db_services.create_database],
        plugins=[sqlalchemy_plugin, CLIPlugin()],
        openapi_config=custom_open_api_config(),
        template_config=custom_template_config(),
        static_files_config=custom_static_files_config(),
        dependencies={
            "limit_offset": Provide(provide_limit_offset_pagination),
        },
        response_cache_config=cache_config,
        exception_handlers={404: exception_handlers.handle_404},
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )
