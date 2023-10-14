import SimplyTransport.lib.settings as settings

from litestar.contrib.sqlalchemy.plugins import AsyncSessionConfig, SQLAlchemyAsyncConfig, SQLAlchemyInitPlugin


session_config = AsyncSessionConfig(expire_on_commit=False)

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.BaseEnvSettings().DB_URL, session_config=session_config
)

sqlalchemy_plugin = SQLAlchemyInitPlugin(config=sqlalchemy_config)