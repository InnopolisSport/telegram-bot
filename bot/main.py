from aiogram.filters import Command, ChatMemberUpdatedFilter, MEMBER, IS_NOT_MEMBER, IS_MEMBER, JOIN_TRANSITION
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, InlineKeyboardButton, \
    InlineKeyboardMarkup, ReplyKeyboardRemove

from loguru import logger

from bot.bot import bot
from bot.filters import text, connected_website
from bot.loader import dp
from bot.api import get_auth_status
from bot.utils import get_user_string


def start_bot():
    try:
        dp.run_polling(bot)
    except Exception as error:
        logger.critical(f'Bot failed to start: {error}')


async def main_menu_keyboard(message: Message, msg_text: str) -> None:
    await message.answer(
        msg_text,
        reply_markup=ReplyKeyboardMarkup(
         keyboard=[
             [
                 KeyboardButton(text="составить тренировку"),
             ],
             [
                 KeyboardButton(text="показать расписание"),  # TODO: logic
                 # KeyboardButton(text="записаться на занятия"),  # TODO: logic
             ],
             [
                 KeyboardButton(text="изменить данные анкеты"),
             ]
         ],
         resize_keyboard=True,
        ))


@dp.message(Command(commands=['me']))
async def get_me(message: Message):
    data = await get_auth_status(message)
    if data:
        await message.answer(f"*{data['first_name']} {data['last_name']}*\n{data['email']}")
        logger.info(f'{get_user_string(message)} sent /me command ({data}) [authorized]')
    else:
        await message.answer(
            '''Привет!\nЧтобы мы продолжили работу, нужно авторизоваться в системе _innosport+_. Пожалуйста, зайди в профиль на сайте.''',
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="авторизоваться на сайте", url="https://innosport.batalov.me/"),
                    ]
                ]
            )
        )
        logger.warning(f'{get_user_string(message)} sent /me command [not authorized]')


# Main menu
@dp.message(Command(commands=['start']))
@dp.message(connected_website)  # If the user is connected (authorized) from website at the first time
async def command_start(message: Message, state: FSMContext):
    await state.clear()
    data = await get_auth_status(message)
    if message:
        if data:
            await main_menu_keyboard(message, '''Привет!\nЯ могу составить для тебя персональную тренировку, рассказать о доступных занятиях и секциях и сориентировать в твоем расписании!\n\nКакой план на сегодня:''')
            logger.info(f'{get_user_string(message)} sent /start command [main menu, authorized]')
        else:
            await message.answer(
                '''Привет!\nЧтобы мы продолжили работу, нужно авторизоваться в системе _innosport+_. Пожалуйста, зайди в профиль на сайте.''',
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(text="авторизоваться на сайте", url="https://innosport.batalov.me/"),
                        ]
                    ]
                )
            )
            logger.warning(f'{get_user_string(message)} sent /start command [main menu, not authorized]')
    else:
        await main_menu_keyboard(message, '')
        logger.info(f'{get_user_string(message)} sent /start command [???]')  # TODO what is this case?


# Alternative main menu
@dp.message(text == 'назад')
@dp.message(text == 'главное меню')
async def alternative_main_menu(message: Message, state: FSMContext) -> None:
    await main_menu_keyboard(message, 'Привет! Какой план на сегодня:')
    logger.info(f'{get_user_string(message)} returned to the main menu [назад, главное меню]')


@dp.message(Command(commands=['schedule']))
@dp.message(text == 'показать расписание')
async def command_schedule(message: Message) -> None:
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


@dp.message(Command(commands=['survey']))
@dp.message(text == 'изменить данные анкеты')
async def command_survey(message: Message, state: FSMContext) -> None:
    # Starting the intro poll
    from bot.routers.intro_poll_router import start_intro_poll
    await start_intro_poll(message, state)
    logger.info(f'{get_user_string(message)} requested a change of the survey [/survey; изменить данные анкеты]')

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
