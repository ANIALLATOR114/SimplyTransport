from SimplyTransport.lib import settings
from SimplyTransport.lib.logging.handlers import get_loki_handler_path

import litestar
import structlog
import logging.config


def provide_logger(logger_name: str) -> structlog.stdlib.BoundLogger:
    """
    Provides a logger with the specified name.

    Args:
        logger_name (str): The name of the logger.

    Returns:
        logging.Logger: The logger object.

    Raises:
        ValueError: If logger_name is empty or None.
    """
    if not logger_name:
        raise ValueError("Logger_name is required")

    logger: structlog.stdlib.BoundLogger = structlog.getLogger(logger_name)

    return logger


def logging_setup():
    timestamper = structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S")
    pre_chain = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.ExtraAdder(),
        timestamper,
        structlog.processors.StackInfoRenderer(),
    ]
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(
                            colors=True,
                            exception_formatter=structlog.dev.RichTracebackFormatter(
                                extra_lines=5,
                                suppress=[litestar],
                                max_frames=5
                            )
                        ),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "loki_formatting": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(
                            colors=True,
                            exception_formatter=structlog.dev.RichTracebackFormatter(
                                suppress=[litestar],
                                max_frames=1
                            )
                        ),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": settings.app.LOG_LEVEL,
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                },
                "loki": {
                    "level": settings.app.LOG_LEVEL,
                    "class": get_loki_handler_path(),
                    "formatter": "loki_formatting",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["default", "loki"],
                    "level": settings.app.LOG_LEVEL,
                    "propagate": True,
                },
                "urllib3.connectionpool": {
                    "handlers": ["default"],
                    "level": "INFO",
                    "propagate": True,
                },
            },
        }
    )

    if structlog.is_configured():
       return
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            timestamper,
            structlog.processors.StackInfoRenderer(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logger = provide_logger(__name__)
    logger.info(
        "Application starting",
        app_name=settings.app.NAME,
        app_version=settings.app.VERSION,
        app_env=settings.app.ENVIRONMENT,
        log_level=settings.app.LOG_LEVEL,
    )


def logging_shutdown():
    logger = provide_logger(__name__)
    logger.info("Application shutting down", app_name=settings.app.NAME, app_version=settings.app.VERSION, app_env=settings.app.ENVIRONMENT, log_level=settings.app.LOG_LEVEL)
    logging.shutdown()