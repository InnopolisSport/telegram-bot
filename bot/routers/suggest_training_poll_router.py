from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loguru import logger
from bot.filters import text
from bot.routers import POLL_NAMES
from bot.api import passed_intro_poll, fetch_poll_by_name, suggest_training, upload_poll_result
from bot.utils import get_user_string, prepare_poll_questions, get_cur_state_name, get_question_text_id, \
    get_question_answers, prepare_poll_result, ErrorMessages, INITIAL_INFLUENCE_RATIOS, get_influence_ratios, \
    accumulate_influence_ratios

INITIAL_WORKING_LOAD = 100_000  # TODO move to db

suggest_training_poll_router = Router()
SUGGEST_TRAINING_POLL_NAME = POLL_NAMES['suggest_training_poll']
SUGGEST_TRAINING_POLL = dict()
INFLUENCE = INITIAL_INFLUENCE_RATIOS


class SuggestTrainingPollStates(StatesGroup):
    goal = State()
    sport = State()
    time = State()
    training = State()

    finish = State()


def parse_suggested_training(suggested_training: dict, info: dict) -> str:  # TODO: add training time, sport, goal
    print(info)
    exercises = suggested_training['exercises']
    full_exercise_types = {
        'WU': '1️⃣️ WARM-UP',    # 1
        'PS': '2️⃣ PRE-SET',    # 2
        'MS': '3️⃣ MAIN SET',   # 3
        'CD': '4️⃣ COOL-DOWN',  # 4
    }
    training_skeleton = {
        'WU': [],
        'PS': [],
        'MS': [],
        'CD': [],
    }
    training = 'План тренировки на сегодня:\n\n'
    training += f"*{info['sport']}*, _{int(info['time'] / 60)} минут_\n*Цель*: {info['goal']}\n\n"
    for exercise in exercises:
        training_skeleton[exercise['type']].append(exercise)

    type_number = 1
    for (exercise_type, exercises) in training_skeleton.items():
        if exercises:
            number = 1
            training += f'*{full_exercise_types[exercise_type]}*\n\n'
            for ex in exercises:
                exercise = ex['exercise']
                training += f'''{type_number}.{number} _{exercise['name']}_  *{"" if ex['set'] == 0 else "" if ex['set'] == 1 else f"{ex['set']}x"}{ex['repeat']}*  `PZ{ex['power_zone']}`\n'''
                number += 1
            training += '\n'
        type_number += 1

    return training


def prepare_params_suggest(results: dict) -> dict:
    return {
        'time': results['time'],
        'working_load': results['working_load'],
        'influence_t': results['influence']['t'],
        'influence_wl': results['influence']['wl'],
    }


@suggest_training_poll_router.message(Command(commands=["suggest_training"]))
@suggest_training_poll_router.message(text == "составить тренировку")
@suggest_training_poll_router.message(SuggestTrainingPollStates.finish, text == "составить следующую тренировку")
async def command_suggest_training(message: Message, state: FSMContext) -> None:
    # Check for intro poll passing
    passed = await passed_intro_poll(message)
    if passed is None:
        await message.answer(ErrorMessages.REQUEST_FAILED.value)
        logger.warning(f'{get_user_string(message)} failed to start suggest training poll')
        return
    if not passed:
        # Starting the intro poll
        from bot.routers.intro_poll_router import start_intro_poll
        await start_intro_poll(message, state)
    else:
        # Starting the suggest training poll
        global SUGGEST_TRAINING_POLL
        SUGGEST_TRAINING_POLL = await fetch_poll_by_name(message, SUGGEST_TRAINING_POLL_NAME)
        SUGGEST_TRAINING_POLL = prepare_poll_questions(SUGGEST_TRAINING_POLL['questions'])
        # To ensure that we are starting from the beginning
        await state.clear()
        # Set state
        await state.set_state(SuggestTrainingPollStates.goal)
        logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
        # Get next question
        cur_state = await get_cur_state_name(state)
        question, q_id = get_question_text_id(SUGGEST_TRAINING_POLL[cur_state])
        answers = get_question_answers(SUGGEST_TRAINING_POLL[cur_state])
        await state.update_data(q=cur_state)
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
                    ]
                ],
                resize_keyboard=True,
            ),
        )
        logger.info(f'{get_user_string(message)} sent /suggest_training command [составить тренировку, составить следующую тренировку] and got question {q_id} [goal]')


@suggest_training_poll_router.message(SuggestTrainingPollStates.goal)
async def process_goal(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    current_influence = get_influence_ratios(SUGGEST_TRAINING_POLL[await get_cur_state_name(state)], message.text)
    global INFLUENCE
    INFLUENCE = accumulate_influence_ratios(INFLUENCE, current_influence)
    # Set state
    await state.set_state(SuggestTrainingPollStates.sport)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(SUGGEST_TRAINING_POLL[cur_state])
    answers = get_question_answers(SUGGEST_TRAINING_POLL[cur_state])
    await state.update_data(q=cur_state)
    # Send message
    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=answer)] for answer in answers],
            resize_keyboard=True,
        ),
    )
    logger.info(f'{get_user_string(message)} got question {q_id} [sport]')


@suggest_training_poll_router.message(SuggestTrainingPollStates.sport)
async def process_sport(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    current_influence = get_influence_ratios(SUGGEST_TRAINING_POLL[await get_cur_state_name(state)], message.text)
    global INFLUENCE
    INFLUENCE = accumulate_influence_ratios(INFLUENCE, current_influence)
    # Set state
    await state.set_state(SuggestTrainingPollStates.time)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(SUGGEST_TRAINING_POLL[cur_state])
    answers = get_question_answers(SUGGEST_TRAINING_POLL[cur_state])
    await state.update_data(q=cur_state)
    # Send message
    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answers[1]),
                    KeyboardButton(text=answers[3]),
                ],
                [
                    KeyboardButton(text=answers[0]),
                    KeyboardButton(text=answers[2]),
                    KeyboardButton(text=answers[4]),
                ],
            ],
            resize_keyboard=True,
        ),
    )
    logger.info(f'{get_user_string(message)} got question {q_id} [time]')


@suggest_training_poll_router.message(SuggestTrainingPollStates.time)
async def process_training(message: Message, state: FSMContext) -> None:
    # Save answer
    current_influence = get_influence_ratios(SUGGEST_TRAINING_POLL[await get_cur_state_name(state)], message.text)
    global INFLUENCE
    INFLUENCE = accumulate_influence_ratios(INFLUENCE, current_influence)
    # Save params for suggest training
    await state.update_data(working_load=INITIAL_WORKING_LOAD)  # TODO: obtain from db
    await state.update_data(time=int(message.text) * 60)  # time in seconds
    await state.update_data(influence=INFLUENCE)  # {t, wl}
    # Set state
    await state.set_state(SuggestTrainingPollStates.training)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
    # Get results
    results = await state.get_data()
    result = prepare_poll_result(results, SUGGEST_TRAINING_POLL_NAME)
    params = prepare_params_suggest(results)
    # Get suggested training
    suggested_training = await suggest_training(message, params)
    if suggested_training:
        # Send message
        await message.answer('''Прекрасно! Следующим сообщением я отправил тебе план упражнений на сегодня. Если ты не совсем понимаешь, что это значит, я могу рассказать тебе немного теории про фитнес и разъяснить, что к чему.''')
        # Parse suggested training
        training = parse_suggested_training(suggested_training, results)
        # Send message with training
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
        # Send message
        await message.answer('''Надеюсь, ты продуктивно проведешь время! Помни, что ты всегда можешь остановиться, если станет слишком тяжело. Не забывай пить достаточно воды во время и после тренировки и сохранять позитивный настрой! Ты делаешь это для себя🙂''')
        logger.info(f'{get_user_string(message)} successfully got suggested training')
    else:
        await message.answer(
            ErrorMessages.SUGGEST_TRAINING.value,
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="составить тренировку"),
                    ],
                    [
                        KeyboardButton(text="главное меню"),
                    ],
                ],
                resize_keyboard=True,
            ),
        )
        logger.warning(f'{get_user_string(message)} failed to get suggested training')
    # Send poll result
    if await upload_poll_result(message, result):
        logger.info(f'{get_user_string(message)} successfully sent suggest training poll result ({result})')
    else:
        logger.warning(f'{get_user_string(message)} failed to sent suggest training poll result')


@suggest_training_poll_router.message(SuggestTrainingPollStates.training, text == "объясни, что это значит")
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    # Send message
    await message.answer(
        '''Любая тренировка состоит из трех частей: разминка (Warm-up), основная часть и заключительное (или заминка (Cool-down), чтобы было проще запомнить).\n\nВо время разминки крайне важно «включить» все системы организма, разогреть их и подготовить к усердной работе на полную мощность. По времени она должна составлять примерно 20% от всей тренировки.\n\nОсновная часть тренировки также делится на две группы упражнений: подготовительная часть (Pre-set), нужна для того, чтобы вспомнить навыки и закрепить результаты, полученные на предыдущей тренировке; во время главной части (Main set), нужно выложиться на полную мощность и настроить себя на улучшение результатов. Основная часть должна составлять примерно 60% от всей тренировки.\n\nЗаключительная часть тренировки необходима для того, чтобы постепенно снизить нагрузку и вывести организм в состояние, близкое к тому, в котором он был перед началом занятий. Это крайне важно, поскольку резкие перепады нагрузок крайне опасны для организма. Заключительная часть также должна занимать около 20% тренировки.''',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="ок, понял"),
                ],
            ],
            resize_keyboard=True,
        ),
    )
    logger.info(f'{get_user_string(message)} got explanation about training structure on state {await get_cur_state_name(state)} [training; объясни, что это значит]')


@suggest_training_poll_router.message(SuggestTrainingPollStates.training, text == "ок, все понятно")
@suggest_training_poll_router.message(SuggestTrainingPollStates.training, text == "ок, понял")
async def process_training_understood(message: Message, state: FSMContext) -> None:
    # Send messages
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
    await message.answer("""Не забудь оставить фидбек после тренировки. Во-первых, это поможет мне скорректировать следующие занятия под твой ритм. Во-вторых только после обратной связи тренировка зачтется в твоём академическом прогрессе😉\n\nОсторожно! Нажав «главное меню» сейчас, ты упустишь возможность отчитаться по прошедшему занятию. Вернуться назад уже не получится.""")
    logger.info(f'{get_user_string(message)} understood training structure [ок, все понятно; ок, понял]')
    # Set state
    await state.set_state(SuggestTrainingPollStates.finish)
    logger.info(f'{get_user_string(message)} set state {await get_cur_state_name(state)}')


@suggest_training_poll_router.message(SuggestTrainingPollStates.finish, text == "тренировка прошла успешно!")
async def process_finish(message: Message, state: FSMContext) -> None:
    # Send message
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
                    KeyboardButton(text="главное меню"),
                ],
            ],
            resize_keyboard=True,
        ),
    )
    logger.info(f'{get_user_string(message)} successfully finished training [тренировка прошла успешно!]')
