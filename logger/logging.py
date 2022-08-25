import logging
from typing import Optional

from logger.settings import InterceptHandler, LoguruHandler
from loguru import logger


def setup_logging(extra_handlers: Optional[list[LoguruHandler]] = None) -> None:
    logging.getLogger().handlers = [InterceptHandler()]

    # Configure loguru
    if extra_handlers:
        logger.configure(handlers=extra_handlers)
