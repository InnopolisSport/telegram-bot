from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from loguru import logger

from bot.api import fetch_poll_by_name, upload_poll_result, get_auth_status
from bot.filters import any_digits, text
from bot.routers import POLL_NAMES
from bot.utils import prepare_poll_questions, get_cur_state_name, get_question_text_id, get_question_answers, \
    prepare_poll_result, get_user_string, ErrorMessages, not_authorized_keyboard

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


async def start_intro_poll(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} started the intro poll, text: {message.text}')
    # Check for authorization
    if await get_auth_status(message) is None:
        # Send message
        await not_authorized_keyboard(message)
        logger.warning(f'{get_user_string(message)} requested an intro poll [/survey], but not authorized')
        return
    # Get intro poll from db
    global INTRO_POLL
    INTRO_POLL = await fetch_poll_by_name(message, INTRO_POLL_NAME)
    # Check for success fetch
    if INTRO_POLL is None:
        # Send message
        await message.answer(ErrorMessages.REQUEST_FAILED.value)
        logger.warning(f'{get_user_string(message)} failed to fetch intro poll')
        return
    # Prepare intro poll questions
    INTRO_POLL = prepare_poll_questions(INTRO_POLL['questions'])
    # To ensure that we are starting from the beginning
    await state.clear()
    # Send message
    await message.answer(
        '''Чтобы я мог составить оптимальный план занятия, мне нужно узнать тебя лучше. Пожалуйста, пройди небольшую анкету, чтобы я составил твой профиль. Проходи честно (я никому не расскажу твои ответы, но смогу лучше понять твои цели от спорта😉).\nВопросов будет много, но не беспокойся, каждый раз отвечать на все не придётся. Я запомню данные о тебе, а затем ты сможешь обновлять их по мере необходимости.''',
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
    # Set state
    await state.set_state(IntroPollStates.age)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.age, text == "ок")
async def process_age(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [age]')
    # Set state
    await state.set_state(IntroPollStates.sex)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.sex)
async def process_sex(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [sex]')
    # Set state
    await state.set_state(IntroPollStates.height)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.height)
async def process_height(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
    await message.answer(
        question,
        reply_markup=ReplyKeyboardRemove(),
    )
    logger.info(f'{get_user_string(message)} got question {q_id} [height]')
    # Set state
    await state.set_state(IntroPollStates.weight)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.weight, any_digits)
async def process_weight(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], int(message.text)
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
    await message.answer(
        question,
        reply_markup=ReplyKeyboardRemove(),
    )
    logger.info(f'{get_user_string(message)} got question {q_id} [weight]')
    # Set state
    await state.set_state(IntroPollStates.medical_group)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.weight)
async def process_height(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Send message
    await message.answer(
        ErrorMessages.REPEAT_INPUT.value,
        reply_markup=ReplyKeyboardRemove(),
    )
    logger.info(f'{get_user_string(message)} repeat question [height]')


@intro_poll_router.message(IntroPollStates.medical_group, any_digits)
async def process_medical_group(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], int(message.text)
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [medical_group]')
    # Set state
    await state.set_state(IntroPollStates.sport_experience)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.medical_group)
async def process_weight(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Send message
    await message.answer(
        ErrorMessages.REPEAT_INPUT.value,
        reply_markup=ReplyKeyboardRemove(),
    )
    logger.info(f'{get_user_string(message)} repeat question [weight]')


@intro_poll_router.message(IntroPollStates.sport_experience)
async def process_sport_experience(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [sport_experience]')
    # Set state
    await state.set_state(IntroPollStates.sport_training_frequency)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.sport_training_frequency, ~(text == 'не было никогда'))
async def process_sport_training_frequency(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [sport_training_frequency]')
    # Set state
    await state.set_state(IntroPollStates.sport_training_time)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.sport_training_time)
async def process_sport_training_time(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [sport_training_time]')
    # Set state
    await state.set_state(IntroPollStates.sport_desire_level)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.sport_desire_level)
async def process_sport_desire_level(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [sport_desire_level]')
    # Set state
    await state.set_state(IntroPollStates.pulse_rest)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.pulse_rest)
@intro_poll_router.message(IntroPollStates.sport_training_frequency, text == 'не было никогда')
async def process_pulse_rest(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Check for state (if user skipped previous questions)
    if await state.get_state() == IntroPollStates.sport_training_frequency:
        await state.set_state(IntroPollStates.pulse_rest)
        logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)} [questions skipped]')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(INTRO_POLL[cur_state])
    answers = get_question_answers(INTRO_POLL[cur_state])
    await state.update_data(q=q_id)
    # Send message
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
    logger.info(f'{get_user_string(message)} got question {q_id} [pulse_rest]')
    # Set state
    await state.set_state(IntroPollStates.finish)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')


@intro_poll_router.message(IntroPollStates.finish)
async def process_finish(message: Message, state: FSMContext) -> None:
    logger.info(f'{get_user_string(message)} sent text: {message.text}')
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get result
    data = await state.get_data()
    result = prepare_poll_result(data, INTRO_POLL_NAME)
    logger.info(f'{get_user_string(message)} obtained intro poll result {result}')
    # Send poll result
    if await upload_poll_result(message, result):
        # Go to suggest training poll
        from bot.routers.suggest_training_poll_router import command_suggest_training
        await command_suggest_training(message, state)
        logger.info(f'{get_user_string(message)} successfully finished intro poll')
    else:
        await message.answer(
            ErrorMessages.REQUEST_FAILED.value,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="главное меню"),
                    ],
                ],
                resize_keyboard=True,
            ),
        )
        logger.warning(f'{get_user_string(message)} failed to finish intro poll')
