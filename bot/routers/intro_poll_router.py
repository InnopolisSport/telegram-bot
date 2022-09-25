from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from loguru import logger
from bot.filters import any_digits, text
from bot.routers import POLL_NAMES
from bot.utils import fetch_poll_by_name, upload_poll_result_by_name

intro_poll_router = Router()
INTRO_POLL_NAME = POLL_NAMES['intro_poll']
INTRO_POLL = dict()


class IntroPollStates(StatesGroup):
    age = State()
    sex = State()
    height = State()
    weight = State()
    medical_group = State()
    sport_experience = State()
    sport_training_frequency = State()
    sport_training_time = State()
    sport_desire_level = State()
    pulse_rest = State()

    finish = State()


@intro_poll_router.message(commands=["intro_poll"])
@intro_poll_router.message(text == 'изменить данные анкеты')
async def start_intro_poll(message: Message, state: FSMContext) -> None:
    # INTRO_POLL = await fetch_poll_by_name(message, INTRO_POLL_NAME)
    await state.clear()  # to ensure that we are starting from the beginning
    await state.set_state(IntroPollStates.age)
    await message.answer(  # TODO: Add alternative text for editing intro poll
        '''Чтобы я мог составить оптимальный план занятия, мне нужно узнать тебя лучше. Пожалуйста, пройти небольшую анкету, чтобы я составил твой профиль. Проходи честно (я никому не расскажу твои ответы, но смогу лучше понять твои цели от спорта😉).\nВопросов будет 13, но не беспокойся, каждый раз отвечать на все не придётся. Я запомню данные о тебе, а затем ты сможешь обновлять их по мере необходимости.''',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="ок"),
                ],
                [
                    KeyboardButton(text="назад"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.age, text == "ок")  # INTRO_POLL.get("first").get("answer")[0]
async def process_age(message: Message, state: FSMContext) -> None:
    await state.set_state(IntroPollStates.sex)
    await message.answer(
        "AGE",  # INTRO_POLL.get('age').get('text')
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="20-24"),
                ],
                [
                    KeyboardButton(text="<20"),
                    KeyboardButton(text=">24"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sex)
async def process_sex(message: Message, state: FSMContext) -> None:
    await state.update_data(age=message.text)  # TODO: Parse for backend into enum
    await state.set_state(IntroPollStates.height)
    await message.answer(
        "SEX",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Мужской"),
                    KeyboardButton(text="Женский"),
                ],
                [
                    KeyboardButton(text="Другой"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.height)
async def process_height(message: Message, state: FSMContext) -> None:
    await state.update_data(sex=message.text)  # TODO: Parse correctly
    await state.set_state(IntroPollStates.weight)
    await message.answer(
        "HEIGHT CM",
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.weight, any_digits)
async def process_weight(message: Message, state: FSMContext) -> None:
    await state.update_data(height=int(message.text))  # TODO: Parse correctly (what if not int?)
    await state.set_state(IntroPollStates.medical_group)
    await message.answer(
        "WEIGHT KG",
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.weight)
async def process_weight(message: Message, state: FSMContext) -> None:
    await message.answer(
        "TRY HEIGHT CM AGAIN",
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.medical_group, any_digits)
async def process_medical_group(message: Message, state: FSMContext) -> None:
    await state.update_data(weight=int(message.text))  # TODO: Parse correctly (what if not int?)
    await state.set_state(IntroPollStates.sport_experience)
    await message.answer(
        "MEDICAL GROUP",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="I"),  # TODO: Parse from sport site?
                    KeyboardButton(text="II"),
                    KeyboardButton(text="III"),
                ],
                [
                    KeyboardButton(text="Не знаю"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.medical_group)
async def process_weight(message: Message, state: FSMContext) -> None:
    await message.answer(
        "TRY WEIGHT KG AGAIN",
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.sport_experience)
async def process_sport_experience(message: Message, state: FSMContext) -> None:
    await state.update_data(medical_group=message.text)  # TODO: Parse correctly
    await state.set_state(IntroPollStates.sport_training_frequency)
    await message.answer(
        "SPORT EXPERIENCE",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Не было никогда"),
                    KeyboardButton(text="Есть регулярный"),
                ],
                [
                    KeyboardButton(text="Был больше 3 лет назад"),
                ],
                [
                    KeyboardButton(text="Был меньше 1 года назад"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sport_training_frequency)
async def process_sport_training_frequency(message: Message, state: FSMContext) -> None:
    await state.update_data(sport_experience=message.text)  # TODO: Parse correctly
    await state.set_state(IntroPollStates.sport_training_time)
    await message.answer(
        "SPORT TRAINING FREQUENCY",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="0-1 раз"),
                    KeyboardButton(text="2-3 раза"),
                    KeyboardButton(text=">4 раз"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sport_training_time)
async def process_sport_training_time(message: Message, state: FSMContext) -> None:
    await state.update_data(sport_training_frequency=message.text)  # TODO: Parse correctly
    await state.set_state(IntroPollStates.sport_desire_level)
    await message.answer(
        "SPORT TRAINING TIME",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="до 30 минут"),
                ],
                [
                    KeyboardButton(text="30-60 минут"),
                ],
                [
                    KeyboardButton(text="свыше 60 минут"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sport_desire_level)
async def process_sport_desire_level(message: Message, state: FSMContext) -> None:
    await state.update_data(sport_training_time=message.text)  # TODO: Parse correctly
    await state.set_state(IntroPollStates.pulse_rest)
    await message.answer(
        "SPORT DESIRE LEVEL",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="тренировался легко, без отдышки и потоотделения"),
                ],
                [
                    KeyboardButton(text="тренировался до появления первой отдышки и потоотделения"),
                ],
                [
                    KeyboardButton(text="тренировался на полную, потел и едва дышал"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.pulse_rest)
async def process_pulse_rest(message: Message, state: FSMContext) -> None:
    await state.update_data(sport_desire_level=message.text)  # TODO: Parse correctly
    await state.set_state(IntroPollStates.finish)
    await message.answer(
        "PULSE REST",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="менее 60 уд/мин"),
                ],
                [
                    KeyboardButton(text="60-90 уд/мин"),
                ],
                [
                    KeyboardButton(text="более 90 уд/мин"),
                ],
                [
                    KeyboardButton(text="какой-то неправильный"),
                    KeyboardButton(text="не знаю"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


def prepare_result(data: dict) -> dict:
    return {}  # TODO: Prepare result


@intro_poll_router.message(IntroPollStates.finish)
async def process_finish(message: Message, state: FSMContext) -> None:
    await state.update_data(pulse_rest=message.text)
    data = await state.get_data()
    result = prepare_result(data)
    status_code, json = await upload_poll_result_by_name(message, result, INTRO_POLL_NAME)

    # if status_code == 200:
    # Go to suggest training
    from bot.routers.suggest_training_poll_router import command_suggest_training
    await command_suggest_training(message, state)
    logger.info(f"Upload intro poll result: {status_code} {json}")
