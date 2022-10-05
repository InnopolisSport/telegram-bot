from aiogram import Router
from aiogram.types import Message

from loguru import logger
from bot.utils import get_user_string

fallback_router = Router()


@fallback_router.message()
async def fallback(message: Message):
    await message.answer('Любой бот даёт сбой, я не понимаю тебя. Попробуй еще раз')
    logger.info(f'{get_user_string(message)} fallback: {message.text}')
