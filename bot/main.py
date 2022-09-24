from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from bot.filters import text
from bot.loader import dp, bot
from bot import auth
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup


def start_bot():
    try:
        dp.run_polling(bot)
    except Exception as err:
        logger.critical(f'Bot failed to start: {err}')


async def get_auth_status(message: Message):
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get('http://innosport.batalov.me/api/profile/me') as response:
            json = await response.json()
            status_code = response.status
    logger.info(f'User {message.from_user.id} status code: {status_code}')
    return status_code, json


@dp.message(Command(commands=['me']))
async def get_me(message: Message):
    status_code, json = await get_auth_status(message)
    if status_code == 200:
        await message.answer(json['first_name'] + ' ' + json['last_name'] + '\n' + json['email'])
        logger.info(f'Replied message: {json}')
    elif status_code == 403:
        await message.answer(json['detail'])
        logger.info(f'{status_code} Replied message: {json}')
    else:
        await message.answer('Something went wrong')
        logger.warning(f'Something went wrong, replied message: {json}')


# Main menu
@dp.message(Command(commands=['start']))
@dp.message(text == "главное меню")
async def command_start(message: Message, state: FSMContext):
    await state.clear()
    status_code, json = await get_auth_status(message)
    if message:
        # if status_code == 403:
        #     await message.answer('''
        #         Hi there!\nYou are not authorized\. Please authorize at [the website](http://innosport.batalov.me/).
        #     ''')
        # elif status_code == 200:
        await message.answer('''
                Hi there!\nI'm innosport+ bot!\nI can suggest you a training!
            ''',
                             reply_markup=ReplyKeyboardMarkup(
                                 keyboard=[
                                     [
                                         KeyboardButton(text="Suggest training"),
                                     ],
                                 ],
                                 resize_keyboard=True,
                             ))
    else:
        await message.answer('', reply_markup=ReplyKeyboardMarkup(
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
        f'{message.from_user.full_name} (@{message.from_user.username}:{message.from_user.id}) sent /start command (auth status: {status_code}, json: {json})')


@dp.message(Command(commands=['help']))
async def command_help(message: Message):
    status_code, _ = await get_auth_status(message)
    if status_code == 403:
        await message.answer('''
            You are not authorized. Please authorize at [the website](http://innosport.batalov.me/).
        ''')
    elif status_code == 200:
        await message.answer('''
        Use /suggest_training command to get a training!
    ''')
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
