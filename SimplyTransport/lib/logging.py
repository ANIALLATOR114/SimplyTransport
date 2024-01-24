from . import settings
import logging.handlers
import logging_loki
from queue import Queue


class LokiHandler:
    """A handler for logging to Loki"""

    def __init__(self):
        tags = {
            "app": settings.app.NAME,
            "env": settings.app.ENVIRONMENT,
            "version": settings.app.VERSION,
        }

        self.url = settings.app.LOKI_URL
        self.tags = tags
        self.version = "1"
        self.queue = Queue(-1)
        super().__init__()

    def create_queue_handler(self) -> logging.handlers.QueueHandler:
        handler = logging_loki.LokiQueueHandler(
            queue=self.queue,
            url=self.url,
            tags=self.tags,
            version=self.version,
        )
        return handler

    def create_handler(self) -> logging.Handler:
        handler = logging_loki.LokiHandler(
            url=self.url,
            tags=self.tags,
            version=self.version,
        )
        return handler


class FilterDefaultTags(logging.Filter):
    def filter(self, record):
        r = record.__dict__
        line_number = r["lineno"]
        calling_function = r["funcName"]
        filename = r["filename"]
        module = r["module"]
        full_path = f"{filename}:{line_number} {module}.{calling_function}()"

        record.tags = {
            "line_number": line_number,
            "function": calling_function,
            "filename": filename,
            "module": module,
            "full_path": full_path,
        }
        return True


def provide_logger(logger_name: str) -> logging.Logger:
    """Provides a configured named logger"""

    if not logger_name:
        raise ValueError("Logger_name is required")

    time_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt=time_format)

    logger = logging.getLogger(logger_name)
    logger.handlers = []
    logger.setLevel(settings.app.LOG_LEVEL)

    loki_handler = LokiHandler().create_queue_handler()
    caller_filter = FilterDefaultTags()
    loki_handler.addFilter(caller_filter)
    loki_handler.setFormatter(formatter)
    logger.addHandler(loki_handler)

    if settings.app.ENVIRONMENT != "DEV":
        logger.propagate = False

    return logger


logger = provide_logger(settings.app.NAME)
