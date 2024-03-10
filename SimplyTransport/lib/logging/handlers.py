import os
from queue import Queue
from SimplyTransport.lib import settings

import logging.config
import logging.handlers
import logging_loki


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
        self.handler = self.create_queue_handler()
        self.level = logging.NOTSET
        self.addFilter(FilterDefaultTags())
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

    def setFormatter(self, formatter: logging.Formatter) -> None:
        self.handler.setFormatter(formatter)

    def setLevel(self, level: int) -> None:
        self.level = level
        self.handler.setLevel(level)

    def handle(self, record: logging.LogRecord) -> None:
        self.handler.handle(record)

    def addFilter(self, filter: logging.Filter) -> None:
        self.handler.addFilter(filter)


def get_loki_handler_path():
    """
    Returns the fully qualified path of the LokiHandler class.

    Returns:
        str: The fully qualified path of the LokiHandler class.
    """
    return f"{__name__}.{LokiHandler.__name__}"
