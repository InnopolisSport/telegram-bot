from aiogram import Router
from aiogram.types import Message

fallback_router = Router()


@fallback_router.message()
async def fallback(message: Message):
    await message.answer('Любой бот даёт сбой, я не понимаю тебя. Попробуй еще раз')
