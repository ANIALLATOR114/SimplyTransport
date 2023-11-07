import SimplyTransport.lib.settings as settings

from litestar.contrib.sqlalchemy.plugins import (
    AsyncSessionConfig,
    SQLAlchemyAsyncConfig,
    SQLAlchemyInitPlugin,
)

# Sync version for importer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine(settings.app.DB_URL_SYNC)
session = Session(engine)


# Async version for main API
session_config = AsyncSessionConfig(expire_on_commit=False)
sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.app.DB_URL, session_config=session_config
)
sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)
