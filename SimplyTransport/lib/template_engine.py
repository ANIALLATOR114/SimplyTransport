from pathlib import Path

from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.template.config import TemplateConfig

from .constants import APP_DIR, TEMPLATE_DIR


def custom_template_config() -> TemplateConfig:
    return TemplateConfig(
        directory=Path(f"./{APP_DIR}/{TEMPLATE_DIR}"),
        engine=JinjaTemplateEngine,
    )
