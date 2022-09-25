from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loguru import logger
from bot.filters import text
from bot.loader import dp, bot
from bot.routers.intro_poll_router import IntroPollStates
from bot.routers.suggest_training_poll_router import SuggestTrainingPollStates
from bot.routers.training_feedback_router import TrainingFeedbackStates
from bot.utils import get_auth_status


def start_bot():
    try:
        dp.run_polling(bot)
    except Exception as err:
        logger.critical(f'Bot failed to start: {err}')


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
async def command_start(message: Message, state: FSMContext):
    await state.clear()
    status_code, json = await get_auth_status(message)
    if message:
        if status_code == 403:
            await message.answer('''
                 Привет!\nЧтобы мы продолжили работу, нужно авторизоваться в системе _innosport+_. Пожалуйста, зайди в профиль по ссылке: [innosport.batalov.me](http://innosport.batalov.me/).
            ''')
        elif status_code == 200:
            await message.answer('''
                    Привет!\nЯ бот _innosport+_, и моя задача — усовершенствовать твой подход к спорту. Я могу составить для тебя персональную тренировку, рассказать о доступных занятиях и секциях и сориентировать в твоем расписании! Какой план на сегодня:
                ''',
                                 reply_markup=ReplyKeyboardMarkup(
                                     keyboard=[
                                         [
                                             KeyboardButton(text="показать расписание"),
                                             KeyboardButton(text="записаться на занятия"),
                                         ],
                                         [
                                             KeyboardButton(text="составить тренировку"),
                                         ],
                                     ],
                                     resize_keyboard=True,
                                 ))
    else:
        await message.answer(
            '', reply_markup=ReplyKeyboardMarkup(
                                     keyboard=[
                                         [
                                             KeyboardButton(text="показать расписание"),
                                             KeyboardButton(text="записаться на занятия"),
                                         ],
                                         [
                                             KeyboardButton(text="составить тренировку"),
                                         ],
                                     ],
                                     resize_keyboard=True,
                                 ))
    logger.info(
        f'{message.from_user.full_name} (@{message.from_user.username}:{message.from_user.id}) sent /start command (auth status: {status_code}, json: {json})')


# Alternative main menu
@dp.message(IntroPollStates.age, text == 'назад')
@dp.message(TrainingFeedbackStates.finish, text == 'главное меню')
@dp.message(SuggestTrainingPollStates.finish, text == 'главное меню')
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Привет! Какой план на сегодня:',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="показать расписание"),
                    KeyboardButton(text="записаться на занятия"),
                ],
                [
                    KeyboardButton(text="составить тренировку"),
                ],
            ],
            resize_keyboard=True,
        ))


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
