from typing import Any, Dict
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loguru import logger
from bot import auth
from bot.filters import text
from bot.routers import POLL_NAMES
from bot.utils import passed_intro_poll, fetch_poll_by_name

INITIAL_WORKING_LOAD = 100_000

suggest_training_poll_router = Router()
SUGGEST_TRAINING_POLL_NAME = POLL_NAMES['suggest_training_poll']
SUGGEST_TRAINING_POLL = dict()


class SuggestTrainingPollStates(StatesGroup):
    goal = State()
    sport = State()
    training = State()  # includes training_time saving


def parse_suggested_training(suggested_training: Dict[str, Any]) -> str:
    exercises = suggested_training['exercises']
    full_exercise_types = {
        'WU': '1️⃣️ WARM-UP',
        'PS': '2️⃣ PRE-SET',
        'MS': '3️⃣ MAIN SET',
        'CD': '4️⃣ COOL-DOWN',
    }
    training_skeleton = {
        'WU': [],
        'PS': [],
        'MS': [],
        'CD': [],
    }
    training = 'План тренировки на сегодня:\n\n'
    for exercise in exercises:
        training_skeleton[exercise['type']].append(exercise)

    type_number = 1
    for (exercise_type, exercises) in training_skeleton.items():
        if exercises:
            number = 1
            training += f'*{full_exercise_types[exercise_type]}*\n\n'
            for ex in exercises:
                exercise = ex['exercise']
                training += f'''{type_number}.{number} _{exercise['name']}_  *{"" if ex['set'] == 0 else f"{ex['set']}x" }{ex['repeat']}*  `PZ{ex['power_zone']}`\n'''
                number += 1
            training += '\n'
        type_number += 1
    return training


@suggest_training_poll_router.message(commands=["suggest_training"])
@suggest_training_poll_router.message(text == "suggest training")
async def command_suggest_training(message: Message, state: FSMContext) -> None:
    if not await passed_intro_poll(message):
        from bot.routers.intro_poll_router import start_intro_poll
        await start_intro_poll(message, state)  # Starting the intro poll
    else:
        # SUGGEST_TRAINING_POLL = await fetch_poll_by_name(message, SUGGEST_TRAINING_POLL_NAME)
        await state.clear()  # to ensure that we are starting from the beginning
        await state.set_state(SuggestTrainingPollStates.goal)
        await message.answer(
            "GOAL",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="поддержание фитнеса"),
                    ],
                    [
                        KeyboardButton(text="умеренный набор мышечной массы"),
                    ],
                    [
                        KeyboardButton(text="стремительный набор мышечной массы"),
                    ]
                ],
                resize_keyboard=True,
            ),
        )


@suggest_training_poll_router.message(SuggestTrainingPollStates.goal)
async def process_goal(message: Message, state: FSMContext) -> None:
    await state.update_data(goal=message.text)  # TODO: Parse for backend into enum
    await state.set_state(SuggestTrainingPollStates.sport)
    await message.answer(
        "SPORT",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="плавание"),  # For now, only swimming (later need loop for sports)
                ],
            ],
            resize_keyboard=True,
        ),
    )


@suggest_training_poll_router.message(SuggestTrainingPollStates.sport)
async def process_sport(message: Message, state: FSMContext) -> None:
    await state.update_data(sport=message.text)  # TODO: Parse for backend into enum
    await state.set_state(SuggestTrainingPollStates.training)
    await message.answer(
        "TRAINING TIME",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="45"),
                    KeyboardButton(text="90"),
                ],
                [
                    KeyboardButton(text="30"),
                    KeyboardButton(text="60"),
                    KeyboardButton(text="120"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@suggest_training_poll_router.message(SuggestTrainingPollStates.training)
async def process_training(message: Message, state: FSMContext) -> None:
    await state.update_data(time=int(message.text) * 60)  # TODO: Parse for backend correctly
    await state.update_data(working_load=INITIAL_WORKING_LOAD)
    data = await state.get_data()
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'http://innosport.batalov.me/api/training_suggestor/suggest', params=data) as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        training = parse_suggested_training(json)
        await message.answer(
            training,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="ок, все понятно"),
                    ],
                    [
                        KeyboardButton(text="объясни, что это значит"),
                    ],
                ],
                resize_keyboard=True,
            ),
        )
    else:
        pass  # TODO: Handle error
    await state.clear()
    logger.info(
        f'{message.from_user.full_name} (@{message.from_user.username}:{message.from_user.id}) sent /suggest_training command (auth status: {status_code}, json: {json})')


@suggest_training_poll_router.message(text == "объясни, что это значит")
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    await message.answer(
        "FITNESS INFO",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="ок, понял"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@suggest_training_poll_router.message(text == "ок, все понятно")
@suggest_training_poll_router.message(text == "ок, понял")
async def process_training_understood(message: Message, state: FSMContext) -> None:
    await message.answer(
        "TRAINING UNDERSTOOD",  # TODO: Change with actual info from BD
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="тренировка прошла успешно!"),
                ],
                [
                    KeyboardButton(text="главное меню"),
                ],
            ],
            resize_keyboard=True,
        ),
    )
