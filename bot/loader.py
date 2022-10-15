from aiogram import Dispatcher

from bot.routers.fallback_router import fallback_router
from bot.routers.intro_poll_router import intro_poll_router
from bot.routers.notifier_router import notifier_router
from bot.routers.suggest_training_poll_router import suggest_training_poll_router
from bot.routers.training_feedback_router import training_feedback_poll_router
from loguru import logger


async def on_startup_event():
    logger.info('Bot started')


async def on_shutdown_event():
    logger.info('Bot stopped')


# Initialize dispatcher
dp = Dispatcher()
# Register special events
dp.startup.register(on_startup_event)
dp.shutdown.register(on_shutdown_event)
# Include routers
dp.include_router(intro_poll_router)
dp.include_router(suggest_training_poll_router)
dp.include_router(training_feedback_poll_router)
dp.include_router(notifier_router)
dp.include_router(fallback_router)  # must be included last
