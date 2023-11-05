from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseEnvSettings(BaseSettings):
    """Base settings class for environment variables."""

    DEBUG: bool = False
    ENVIRONMENT: Literal["DEV", "PROD", "TEST", "CI_TEST"] = "DEV"
    if ENVIRONMENT != "PROD":
        NAME: str = f"SimplyTransport {ENVIRONMENT}"
    else:
        NAME: str = "SimplyTransport"
    LOG_LEVEL: Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"] = "INFO"
    VERSION: str = "0.1.0"
    SECRET_KEY: str = "secret"
    LITESTAR_APP: str = "SimplyTransport.app:create_app"

    # Database
    DB_URL: str = "postgresql+asyncpg://user:password@localhost:5432/st_database"
    DB_URL_SYNC: str = "postgresql+psycopg2://user:password@localhost:5432/st_database"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
