from litestar.static_files.config import StaticFilesConfig
from .constants import STATIC_DIR, APP_DIR


def custom_static_files_config() -> list[StaticFilesConfig]:
    static_file_configs = [
        StaticFilesConfig(directories=[f"./{APP_DIR}/{STATIC_DIR}"], path="/", name=STATIC_DIR),
    ]

    return static_file_configs
