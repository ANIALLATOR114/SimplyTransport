import SimplyTransport.lib.settings as settings
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Patch sqlalchemy module factories before importing create_engine / create_async_engine into this
# module. A local `from sqlalchemy import create_engine` binds whatever callable the module held
# at import time; if that happens before instrument(), we keep the unwrapped function and never
# attach EngineTracer (no query spans — only the global Engine.connect wrap shows "connect").
SQLAlchemyInstrumentor().instrument(enable_commenter=True)

from litestar.contrib.sqlalchemy.plugins import (  # noqa: E402
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from sqlalchemy import create_engine  # noqa: E402
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

# Sync version for importer
engine = create_engine(settings.app.DB_URL_SYNC, echo=settings.app.DB_ECHO, pool_pre_ping=True)
session = Session(engine)


# Async version for main API
async_engine = create_async_engine(
    settings.app.DB_URL,
    echo=settings.app.DB_ECHO,
    pool_pre_ping=True,
)

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(engine_instance=async_engine, session_config=session_config)
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)

async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
