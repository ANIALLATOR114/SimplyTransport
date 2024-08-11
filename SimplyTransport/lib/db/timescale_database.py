import SimplyTransport.lib.settings as settings

from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

async_timescale_engine = create_async_engine(
    settings.app.TIMESCALE_URL,
    echo=settings.app.DB_ECHO,
    pool_pre_ping=True,
)
SQLAlchemyInstrumentor().instrument(
    engine=async_timescale_engine.sync_engine,
    enable_commenter=True,
)

timescale_session_config = AsyncSessionConfig(expire_on_commit=False)
timescale_sqlalchemy_config = SQLAlchemyAsyncConfig(
    engine_instance=async_timescale_engine, session_config=timescale_session_config
)
timescale_sqlalchemy_plugin = SQLAlchemyInitPlugin(config=timescale_sqlalchemy_config)

async_timescale_session_factory = async_sessionmaker(async_timescale_engine, expire_on_commit=False)
