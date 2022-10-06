from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loguru import logger
from bot.filters import text
from bot.loader import dp, bot
from bot.routers.intro_poll_router import IntroPollStates
from bot.routers.suggest_training_poll_router import SuggestTrainingPollStates
from bot.routers.training_feedback_router import TrainingFeedbackStates
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
                 KeyboardButton(text="записаться на занятия"),  # TODO: logic
             ],
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
        await message.answer('''Привет!\nЧтобы мы продолжили работу, нужно авторизоваться в системе _innosport+_. Пожалуйста, зайди в профиль по ссылке: [innosport.batalov.me](http://innosport.batalov.me/).''')
        logger.warning(f'{get_user_string(message)} sent /me command [not authorized]')


# Main menu
@dp.message(Command(commands=['start']))
async def command_start(message: Message, state: FSMContext):
    await state.clear()
    data = await get_auth_status(message)
    if message:
        if data:
            await main_menu_keyboard(message, '''Привет!\nЯ бот _innosport+_, и моя задача — усовершенствовать твой подход к спорту. Я могу составить для тебя персональную тренировку, рассказать о доступных занятиях и секциях и сориентировать в твоем расписании! Какой план на сегодня:''')
            logger.info(f'{get_user_string(message)} sent /start command [main menu]')
    else:
        await main_menu_keyboard(message, '')
        logger.info(f'{get_user_string(message)} sent /start command [???]')  # TODO what is this case?


# Alternative main menu
@dp.message(IntroPollStates.age, text == 'назад')
@dp.message(IntroPollStates.finish, text == 'главное меню')
@dp.message(TrainingFeedbackStates.finish, text == 'главное меню')
@dp.message(SuggestTrainingPollStates.finish, text == 'главное меню')
async def alternative_main_menu(message: Message, state: FSMContext) -> None:
    await main_menu_keyboard(message, 'Привет! Какой план на сегодня:')
    logger.info(f'{get_user_string(message)} returned to the main menu [назад, главное меню]')


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
