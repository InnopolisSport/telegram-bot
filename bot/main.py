import re

from aiogram.filters import Command
from loguru import logger
from bot.loader import dp, bot
from bot import auth
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton


def start_bot():
    try:
        dp.run_polling(bot)
    except Exception as err:
        logger.critical(f'Bot failed to start: {err}')


async def get_auth_status(message: Message):
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get('https://474d-188-130-155-148.eu.ngrok.io/api/profile/me') as response:
            json = await response.json()
            status_code = response.status
    return status_code, json


def escape_to_markdownv2(text: str):
    #  To be escaped: '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    return re.sub(r'([_*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


@dp.message(Command(commands=['me']))
async def get_me(message: Message):
    status_code, json = await get_auth_status(message)
    if status_code == 403:
        await message.answer(escape_to_markdownv2(json['detail']))
        logger.info(f'Replied message: {json}')
    elif status_code == 200:
        await message.answer(escape_to_markdownv2(json['first_name'] + ' ' + json['last_name'] + '\n' + json['email']))
        logger.info(f'Replied message: {json}')


@dp.message(Command(commands=['start']))
async def send_welcome(message: Message):
    status_code, _ = await get_auth_status(message)
    # if status_code == 403:
    #     await message.answer('''
    #         Hi there\!\nYou are not authorized\. Please authorize at [sport\.innopolis\.university](https://sport.innopolis.university/)\.
    #     ''')
    # elif status_code == 200:
    await message.answer(escape_to_markdownv2('''
            Hi there!\nI'm innosport+ bot!\nI can suggest you a training for you!
        '''),
                         reply_markup=ReplyKeyboardMarkup(
                             keyboard=[
                                 [
                                     KeyboardButton(text="Suggest training"),
                                 ],
                                 [
                                     KeyboardButton(text="Show schedule"),
                                     KeyboardButton(text="Check in for training"),
                                 ]
                             ],
                             resize_keyboard=True,
                         ))
    logger.info(
        f'{message.from_user.full_name} (@{message.from_user.username}:{message.from_user.id}) sent /start command (auth status: {status_code})')


@dp.message(Command(commands=['help']))
async def send_welcome(message: Message):
    status_code, _ = await get_auth_status(message)
    if status_code == 403:
        await message.answer('''
            You are not authorized\. Please authorize at [sport\.innopolis\.university](https://sport.innopolis.university/)\.
        ''')
    elif status_code == 200:
        await message.answer(escape_to_markdownv2('''
        Use /suggest_training command to get a training!
    '''))
    logger.info(
        f'{message.from_user.full_name} (@{message.from_user.username}) sent /help command (auth status: {status_code})')

# @dp.message()
# async def echo(message: Message):
#     """
#     Handler will forward received message back to the sender
#     By default, message handler will handle all message types (like text, photo, sticker and etc.)
#     """
#     try:
#         await message.send_copy(chat_id=message.chat.id)
#     except TypeError:
#         await message.answer("Nice try!")
