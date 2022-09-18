from aiogram import Bot, Dispatcher

from bot.intro_poll_router import intro_poll_router
from bot.suggest_training_poll_router import suggest_training_poll_router
from settings import API_TOKEN
from loguru import logger


async def on_startup_event():
    logger.info('Bot started')


async def on_shutdown_event():
    logger.info('Bot stopped')


# Initialize bot and dispatcher
# bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher()
# Register special events
dp.startup.register(on_startup_event)
dp.shutdown.register(on_shutdown_event)
# Include routers
dp.include_router(intro_poll_router)
dp.include_router(suggest_training_poll_router)
