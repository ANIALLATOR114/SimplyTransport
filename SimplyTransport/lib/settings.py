from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import validator


class AppSettings(BaseSettings):
    """Settings class for environment variables."""

    model_config = SettingsConfigDict(env_file=(".env"))

    DEBUG: bool = False
    ENVIRONMENT: str = "DEV"
    NAME: str = "SimplyTransport"
    LOG_LEVEL: str = "DEBUG"

    VERSION: str = "0.2.1"  # Version bumping will cache bust static css/js files
    SECRET_KEY: str = "secret"
    LITESTAR_APP: str = "SimplyTransport.app:create_app"

    # Database
    DB_URL: str = "postgresql+asyncpg://user:password@localhost:5432/st_database"
    DB_URL_SYNC: str = "postgresql+psycopg2://user:password@localhost:5432/st_database"
    DB_ECHO: bool = False

    POSTGRES_DB: str = "example"
    POSTGRES_USER: str = "example"
    POSTGRES_PASSWORD: str = "example"

    # Redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379

    # Loki
    LOKI_URL: str = "http://localhost:3100/loki/api/v1/push"

    # GTFS TFI Realtime
    GTFS_TFI_REALTIME_URL: str = "example"
    GTFS_TFI_API_KEY_1: str = "example"
    GTFS_TFI_API_KEY_2: str = "example"
    GTFS_TFI_DATASET: str = "example"

    @validator("NAME", pre=True, always=True)
    def set_name(cls, v, values):
        # Appends the evnironment to the name if not in production
        return v if values.get("ENVIRONMENT") == "PROD" else f"SimplyTransport {values.get('ENVIRONMENT')}"

    @validator("LOG_LEVEL", pre=True, always=True)
    def set_log_level(cls, v, values):
        # Sets the log level to DEBUG if in DEV else INFO
        return "DEBUG" if values.get("ENVIRONMENT") == "DEV" else "INFO"


app = AppSettings()
