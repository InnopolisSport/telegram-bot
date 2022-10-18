from typing import Optional

from loguru import logger

from logger.settings import LoguruHandler


def setup_logging(extra_handlers: Optional[list[LoguruHandler]] = None) -> None:
    # logging.getLogger().handlers = [InterceptHandler()]

    # Configure loguru
    if extra_handlers:
        logger.configure(handlers=extra_handlers)
