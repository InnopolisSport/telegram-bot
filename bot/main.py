import asyncio
import re

from aiogram import types
from aiogram.filters import Command
from loguru import logger
from bot.loader import dp, bot
from bot import auth


def start_bot():
    try:
        dp.run_polling(bot)
    except Exception as err:
        logger.critical(f'Bot failed to start: {err}')


async def get_auth_status(message: types.Message):
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get('http://localhost/api/profile/history_with_self/15') as response:  # TODO change the url
            json = await response.json()
            status_code = response.status
    return status_code, json


@dp.message(Command(commands=['me']))
async def get_me(message: types.Message):
    status_code, json = await get_auth_status(message)
    await message.reply(re.escape(json['detail']))
    logger.info(f'Replied message: {status_code} {json}')


@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    message_body = '''
        Hi there\!\nI'm innosport\+ bot\!\nI can suggest you a training for you\!
    '''
    await message.answer(message_body)
    logger.info(f'{message.from_user.full_name} (@{message.from_user.username}) sent /start command')


@dp.message(Command(commands=['help']))
async def send_welcome(message: types.Message):
    message_body = '''
        I'm innosport\+ bot\!\nUse /suggest\_training command to get a training\!
    '''
    await message.answer(message_body)
    logger.info(f'{message.from_user.full_name} (@{message.from_user.username}) sent /help command')


@dp.message()
async def echo(message: types.Message):
    """
    Handler will forward received message back to the sender
    By default, message handler will handle all message types (like text, photo, sticker and etc.)
    """
    try:
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.answer("Nice try!")
