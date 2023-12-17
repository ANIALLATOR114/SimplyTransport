import SimplyTransport.lib.settings as settings

from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# Sync version for importer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(settings.app.DB_URL_SYNC, echo=settings.app.DB_ECHO)
session = Session(engine)


# Async version for main API
async_engine = create_async_engine(
    settings.app.DB_URL,
    echo=settings.app.DB_ECHO,
)

session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(engine_instance=async_engine, session_config=session_config)
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)

async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)
