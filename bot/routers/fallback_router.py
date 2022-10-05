from typing import Any, Dict
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loguru import logger
from bot import auth
from bot.filters import text
from bot.routers import POLL_NAMES
from bot.utils import passed_intro_poll, fetch_poll_by_name, API_URL, suggest_training


fallback_router = Router()


class FallbackStates(StatesGroup):
    pass


@fallback_router.message()
async def fallback(message: Message):
    await message.answer('Любой бот даёт сбой, я не понимаю тебя. Попробуй еще раз')
