from aiogram import Bot, Dispatcher
from settings import API_TOKEN
from loguru import logger


async def on_startup_event():
    logger.info('Bot started')


async def on_shutdown_event():
    logger.info('Bot stopped')


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher()
dp.startup.register(on_startup_event)
dp.shutdown.register(on_shutdown_event)
