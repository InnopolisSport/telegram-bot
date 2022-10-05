from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from loguru import logger
from bot.filters import any_digits, text
from bot.routers import POLL_NAMES
from bot.api import fetch_poll_by_name, upload_poll_result
from bot.utils import prepare_poll_questions, get_cur_state_name, get_question_text_id, get_question_answers, \
    prepare_poll_result

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
    global INTRO_POLL
    INTRO_POLL = await fetch_poll_by_name(message, INTRO_POLL_NAME)
    INTRO_POLL = prepare_poll_questions(INTRO_POLL['questions'])

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


@intro_poll_router.message(IntroPollStates.age, text == "ок")
async def process_age(message: Message, state: FSMContext) -> None:
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.sex)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[1]),
                ],
                [
                    KeyboardButton(text=answers[0]),
                    KeyboardButton(text=answers[2]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sex)
async def process_sex(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.height)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[0]),
                    KeyboardButton(text=answers[1]),
                ],
                [
                    KeyboardButton(text=answers[2]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.height)
async def process_height(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.weight)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.weight, any_digits)
async def process_weight(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], int(message.text)
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.medical_group)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.weight)
async def process_weight(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Пожалуйста, введи число (в сантиметрах)",
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.medical_group, any_digits)
async def process_medical_group(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], int(message.text)
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.sport_experience)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[0]),
                    KeyboardButton(text=answers[1]),
                    KeyboardButton(text=answers[2]),
                ],
                [
                    KeyboardButton(text=answers[3]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.medical_group)
async def process_weight(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Пожалуйста, введи число (в килограммах)",
        reply_markup=ReplyKeyboardRemove(),
    )


@intro_poll_router.message(IntroPollStates.sport_experience)
async def process_sport_experience(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.sport_training_frequency)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[3]),
                    KeyboardButton(text=answers[0]),
                ],
                [
                    KeyboardButton(text=answers[2]),
                ],
                [
                    KeyboardButton(text=answers[1]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sport_training_frequency)
async def process_sport_training_frequency(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.sport_training_time)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[2]),
                    KeyboardButton(text=answers[1]),
                    KeyboardButton(text=answers[0]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sport_training_time)
async def process_sport_training_time(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.sport_desire_level)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[2]),
                ],
                [
                    KeyboardButton(text=answers[1]),
                ],
                [
                    KeyboardButton(text=answers[0]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.sport_desire_level)
async def process_sport_desire_level(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.pulse_rest)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[0]),
                ],
                [
                    KeyboardButton(text=answers[1]),
                ],
                [
                    KeyboardButton(text=answers[2]),
                ],
                [
                    KeyboardButton(text=answers[3]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.pulse_rest)
async def process_pulse_rest(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)

    await state.set_state(IntroPollStates.finish)

    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[0]),
                ],
                [
                    KeyboardButton(text=answers[1]),
                ],
                [
                    KeyboardButton(text=answers[2]),
                ],
                [
                    KeyboardButton(text=answers[3]),
                    KeyboardButton(text=answers[4]),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@intro_poll_router.message(IntroPollStates.finish)
async def process_finish(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get result
    data = await state.get_data()
    result = prepare_poll_result(data, INTRO_POLL_NAME)

    logger.info(f"Intro poll result: {result}")

    if await upload_poll_result(message, result):
        # Go to suggest training
        from bot.routers.suggest_training_poll_router import command_suggest_training
        await command_suggest_training(message, state)
    else:
        pass
        # await message.answer("Что-то пошло не так. Попробуйте еще раз.") # TODO: maybe return to the beginning of the poll
