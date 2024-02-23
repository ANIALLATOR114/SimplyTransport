import uvicorn
from litestar import Litestar
from litestar.di import Provide
from litestar.stores.registry import StoreRegistry

from SimplyTransport.lib import exception_handlers

from .controllers import create_api_router, create_views_router
from .lib import settings
from SimplyTransport.lib.db import services as db_services
from .lib.db.database import sqlalchemy_plugin
from .lib.openapi.openapiconfig import custom_open_api_config
from .lib.template_engine import custom_template_config
from .lib.static_files import create_static_router
from .lib.cache import redis_service_cache_config_factory, redis_store_factory
from .cli import CLIPlugin
from .lib.parameters.limitoffset import provide_limit_offset_pagination
from .lib.compression import compression_config


def create_app() -> Litestar:
    return Litestar(
        debug=settings.app.DEBUG,
        route_handlers=[create_views_router(), create_api_router(), create_static_router()],
        on_startup=[db_services.create_database],
        plugins=[sqlalchemy_plugin, CLIPlugin()],
        stores=StoreRegistry(default_factory=redis_store_factory),
        openapi_config=custom_open_api_config(),
        template_config=custom_template_config(),
        compression_config=compression_config,
        dependencies={
            "limit_offset": Provide(provide_limit_offset_pagination),
        },
        response_cache_config=redis_service_cache_config_factory(),
        exception_handlers={404: exception_handlers.handle_404},
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        app,
    )
