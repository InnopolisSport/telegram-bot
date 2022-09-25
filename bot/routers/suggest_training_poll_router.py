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

INITIAL_WORKING_LOAD = 100_000

suggest_training_poll_router = Router()
SUGGEST_TRAINING_POLL_NAME = POLL_NAMES['suggest_training_poll']
SUGGEST_TRAINING_POLL = dict()


class SuggestTrainingPollStates(StatesGroup):
    goal = State()
    sport = State()
    training = State()  # includes training_time saving

    finish = State()


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
    training += '''\nНадеюсь, ты продуктивно проведешь время! Помни, что ты всегда можешь остановиться, если станет слишком тяжело. Не забывай пить достаточно воды во время и после тренировки и сохранять позитивный настрой! Ты делаешь это для себя🙂'''
    return training


@suggest_training_poll_router.message(commands=["suggest_training"])
@suggest_training_poll_router.message(text == "составить тренировку")
@suggest_training_poll_router.message(SuggestTrainingPollStates.finish, text == "составить следующую тренировку")
async def command_suggest_training(message: Message, state: FSMContext) -> None:
    if False and not await passed_intro_poll(message):
    # if True or not await passed_intro_poll(message):
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
    params = await state.get_data()
    json = await suggest_training(message, params)
    await message.answer('''Прекрасно! Следующим сообщением я отправил тебе план упражнений на сегодня. Если ты не совсем понимаешь, что это значит, я могу рассказать тебе немного теории про фитнес и разъяснить, что к чему.''')
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
    await state.clear()
    logger.info(
        f'{message.from_user.full_name} (@{message.from_user.username}:{message.from_user.id}) sent /suggest_training command {json})')


@suggest_training_poll_router.message(text == "объясни, что это значит")
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    await message.answer(
        '''Любая тренировка состоит из трех частей: разминка, основная часть и заключительное (или заминка, чтобы было проще запомнить).\nВо время разминки крайне важно “включить” все системы организма, разогреть их и подготовить к усердной работе на полную мощность. По времени она должна составлять примерно 20% от всей тренировки.\nОсновная часть тренировки также делится на две группы упражнений: PRE-SET, или подготовительная часть, нужна для того, чтобы вспомнить навыки и закрепить результаты, полученные на предыдущей тренировке; во время MAIN SET, или главной части, нужно выложиться на полную мощность и настроить себя на улучшение результатов. Основная часть должна составлять примерно 60% от всей тренировки.\nЗаключительная часть тренировки необходима для того, чтобы постепенно снизить нагрузку и вывести организм в состояние, близкое к тому, в котором он был перед началом занятий. Это крайне важно, поскольку резкие перепады нагрузок крайне опасны для организма. Заключительная часть также должна занимать около 20% тренировки.''',
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
    await state.set_state(SuggestTrainingPollStates.finish)
    await message.answer(
        "Удачи! Возвращайся, когда снова понадобится моя помощь!",
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


@suggest_training_poll_router.message(SuggestTrainingPollStates.finish, text == "тренировка прошла успешно!")
async def process_finish(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Я очень рад! Чтобы я мог составить для тебя следующую тренировку, мне нужно узнать о твоем занятии подробнее. Можешь ответить на пару вопросов, чтобы мой план упражнений лучше тебе подходил?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="перейти к вопросам фидбека"),
                ],
                [
                    KeyboardButton(text="составить следующую тренировку"),
                ],
                [
                    KeyboardButton(text="изменить данные анкеты"),
                    KeyboardButton(text="главное меню"),
                ],
            ],
            resize_keyboard=True,
        ),
    )