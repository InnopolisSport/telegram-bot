from bot.main import start_bot
from logger.handlers import HANDLERS
from logger.logging import setup_logging

if __name__ == '__main__':
    setup_logging(HANDLERS)
    start_bot()
