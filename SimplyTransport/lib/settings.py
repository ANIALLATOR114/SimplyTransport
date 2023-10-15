from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvSettings(BaseSettings):
    """Base settings class for environment variables."""

    DEBUG: bool = False
    ENVIRONMENT: Literal["DEV", "PROD", "TEST", "CI_TEST"] = "DEV"
    LOG_LEVEL: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    NAME: str = "SimplyTransport"
    SECRET_KEY: str = "secret"
    LITESTAR_APP: str = "SimplyTransport.app:create_app"

    # Database
    DB_URL: str = "postgresql+asyncpg://stuser:stpassword@localhost:5432/st_database"

    # OpenAPI
    OPENAPI_TITLE: str = "SimplyTransport"
    OPENAPI_VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
