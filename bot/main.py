import asyncio

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, \
    InlineKeyboardMarkup
from loguru import logger

from bot.api import get_auth_status
from bot.bot import bot
from bot.filters import text, connected_website
from bot.loader import dp
from bot.utils import get_user_string, main_menu_keyboard, not_authorized_keyboard


def start_bot():
    try:
        dp.run_polling(bot)
    except Exception as error:
        logger.critical(f'Bot failed to start: {error}')


@dp.message(Command(commands=['me']))
async def get_me(message: Message):
    print(await bot.get_my_commands())
    data = await get_auth_status(message)
    if data is not None:
        await message.answer(f"*{data['first_name']} {data['last_name']}*\n{data['email']}")
        logger.info(f'{get_user_string(message)} sent /me command ({data}) [authorized]')
    else:
        await not_authorized_keyboard(message)
        logger.warning(f'{get_user_string(message)} sent /me command [not authorized]')


@dp.message(connected_website)  # If the user is connected (authorized) from website at the first time
async def connected_website_handler(message: Message, state: FSMContext):
    await asyncio.sleep(1)
    await command_start(message, state)


# Main menu
@dp.message(Command(commands=['start']))
async def command_start(message: Message, state: FSMContext):
    await state.clear()
    data = await get_auth_status(message)
    if data is not None:
        await main_menu_keyboard(message,
                                 '''Привет!\nЯ могу составить для тебя персональную тренировку, рассказать о доступных занятиях и секциях и сориентировать в твоем расписании!\n\nКакой план на сегодня:''')
        logger.info(f'{get_user_string(message)} sent /start command [main menu, authorized]')
    else:
        await not_authorized_keyboard(message)
        logger.warning(f'{get_user_string(message)} sent /start command [main menu, not authorized]')


# Alternative main menu
@dp.message(text == 'назад')
@dp.message(text == 'главное меню')
async def alternative_main_menu(message: Message, state: FSMContext) -> None:
    await main_menu_keyboard(message, 'Привет! Какой план на сегодня:')
    logger.info(f'{get_user_string(message)} returned to the main menu [назад, главное меню]')


@dp.message(Command(commands=['schedule']))
@dp.message(text == 'показать расписание')
async def command_schedule(message: Message) -> None:
    # TODO: Add request to the server later
    # Check for authorization
    if await get_auth_status(message) is None:
        # Send message
        await not_authorized_keyboard(message)
        logger.warning(f'{get_user_string(message)} requested suggest schedule [/schedule], but not authorized')
        return
    await message.answer(
        """Я работаю над тем, чтобы показывать расписание здесь, но нужно ещё немного времени🥺\nПока ты можешь посмотреть его на главной странице сайта.""",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="перейти на сайт", url="https://innosport.batalov.me/profile"),
                ]
            ]
        )
    )
    logger.info(f'{get_user_string(message)} requested a schedule [/schedule; показать расписание]')

# @dp.message(Command(commands=['survey']))
# @dp.message(text == 'изменить данные анкеты')
# async def command_survey(message: Message, state: FSMContext) -> None:
#     # Starting the intro poll
#     from bot.routers.intro_poll_router import start_intro_poll
#     await start_intro_poll(message, state)
#     logger.info(f'{get_user_string(message)} requested a change of the survey [/survey; изменить данные анкеты]')

# @dp.message(Command(commands=['help']))
# async def command_help(message: Message):
#     status_code, _ = await get_auth_status(message)
#     if status_code == 403:
#         await message.answer('''
#             You are not authorized. Please authorize at [the website](http://innosport.batalov.me/).
#         ''')
#     elif status_code == 200:
#         await message.answer('''
#         Use /suggest_training command to get a training!
#     ''')
#     logger.info(
#         f'{message.from_user.full_name} (@{message.from_user.username}) sent /help command (auth status: {status_code})')


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
