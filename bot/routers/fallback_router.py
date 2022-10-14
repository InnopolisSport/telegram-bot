from aiogram import Router
from aiogram.types import Message

from loguru import logger
from bot.utils import get_user_string, ErrorMessages

fallback_router = Router()


@fallback_router.message()
async def fallback(message: Message):
    await message.answer(ErrorMessages.UNKNOWN_COMMAND.value)
    logger.info(f'{get_user_string(message)} fallback: {message.text}')
