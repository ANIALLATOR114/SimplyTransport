from pathlib import Path
from litestar.template.config import TemplateConfig
from litestar.contrib.jinja import JinjaTemplateEngine
from .constants import TEMPLATE_DIR, APP_DIR


def custom_template_config() -> TemplateConfig:
    return TemplateConfig(
        directory=Path(f"./{APP_DIR}/{TEMPLATE_DIR}"),
        engine=JinjaTemplateEngine,
    )
