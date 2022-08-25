import logging
from typing import Any, NewType

from loguru import logger

LoguruHandler = NewType('LoguruHandler', dict[str, Any])


def logging_level_within(record: LoguruHandler, levels: list[str]) -> bool:
    return record['level'].name in levels


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
