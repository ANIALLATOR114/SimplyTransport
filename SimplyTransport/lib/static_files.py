from litestar.static_files.config import StaticFilesConfig
from SimplyTransport.lib.constants import STATIC_DIR, APP_DIR


def CustomStaticFilesConfigs() -> list[StaticFilesConfig]:
    static_file_configs = [
        StaticFilesConfig(directories=[f"./{APP_DIR}/{STATIC_DIR}"], path="/", name=STATIC_DIR),
    ]

    return static_file_configs
