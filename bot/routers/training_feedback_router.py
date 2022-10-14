from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from loguru import logger
from bot.filters import text
from bot.routers import POLL_NAMES
from bot.api import fetch_poll_by_name, upload_poll_result
from bot.utils import prepare_poll_questions, get_cur_state_name, get_question_text_id, get_question_answers, \
    get_user_string, prepare_poll_result

training_feedback_poll_router = Router()
TRAINING_FEEDBACK_POLL_NAME = POLL_NAMES['training_feedback_poll']
TRAINING_FEEDBACK_POLL = dict()


class TrainingFeedbackStates(StatesGroup):
    five_point_scale = State()
    breaks = State()
    # failed_exercises = State()
    # fail_reason = State()  # Optional
    # doddle_exercises = State()
    # doddle_reason = State()  # Optional

    finish = State()


@training_feedback_poll_router.message(commands=["training_feedback"])
@training_feedback_poll_router.message(text == "training feedback")
@training_feedback_poll_router.message(text == "перейти к вопросам фидбека")
async def command_training_feedback(message: Message, state: FSMContext) -> None:
    # Starting the training feedback poll
    global TRAINING_FEEDBACK_POLL
    TRAINING_FEEDBACK_POLL = await fetch_poll_by_name(message, TRAINING_FEEDBACK_POLL_NAME)
    TRAINING_FEEDBACK_POLL = prepare_poll_questions(TRAINING_FEEDBACK_POLL['questions'])
    # To ensure that we are starting from the beginning
    await state.clear()
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(TRAINING_FEEDBACK_POLL[cur_state])
    answers = get_question_answers(TRAINING_FEEDBACK_POLL[cur_state])
    await state.update_data(q=q_id)
    # Set state
    await state.set_state(TrainingFeedbackStates.five_point_scale)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
    # Send messages
    await message.answer('Скажи, насколько тяжелой прошедшая тренировка показалась тебе в процессе по пятибальной шкале?')
    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text=answer) for answer in answers
                ]
            ],
            resize_keyboard=True,
        ))
    logger.info(f'{get_user_string(message)} sent question {q_id} [five_point_scale]')


@training_feedback_poll_router.message(TrainingFeedbackStates.five_point_scale)
async def process_five_point_scale(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], int(message.text)
    await state.update_data({q: a})
    # Get next question
    cur_state = await get_cur_state_name(state)
    question, q_id = get_question_text_id(TRAINING_FEEDBACK_POLL[cur_state])
    answers = get_question_answers(TRAINING_FEEDBACK_POLL[cur_state])
    await state.update_data(q=q_id)
    # Set state
    await state.set_state(TrainingFeedbackStates.breaks)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
    # Send message
    await message.answer(
        question,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=answer)] for answer in answers],
            resize_keyboard=True,
        ),
    )
    logger.info(f'{get_user_string(message)} sent question {q_id} [breaks]')


@training_feedback_poll_router.message(TrainingFeedbackStates.breaks)
async def process_breaks(message: Message, state: FSMContext) -> None:
    # Save answer
    q, a = (await state.get_data())['q'], message.text
    await state.update_data({q: a})
    # Get next question
    # cur_state = await get_cur_state_name(state)
    # question, q_id = get_question_text_id(TRAINING_FEEDBACK_POLL[cur_state])
    # answers = get_question_answers(TRAINING_FEEDBACK_POLL[cur_state])
    # await state.update_data(q=q_id)
    # Set state
    # await state.set_state(TrainingFeedbackStates.failed_exercises)  # TODO: uncomment when ready
    await state.set_state(TrainingFeedbackStates.finish)
    logger.info(f'{get_user_string(message)} set state to {await get_cur_state_name(state)}')
    # Finish the poll
    logger.info(f'{get_user_string(message)} save and finish the poll')
    await save_and_finish(message, state)
    # Send message
    # TODO: Get list of exercises with number as in suggested training
    # await message.answer(
    #     question,
    #     reply_markup=ReplyKeyboardMarkup(
    #         keyboard=[
    #             [
    #                 KeyboardButton(text="нет, справился со всеми"),  # TODO: leave this not from db
    #                 KeyboardButton(text="1"),  # TODO: how to realize this?
    #                 KeyboardButton(text="2"),  # TODO: Change to inline multichoice
    #             ],
    #         ],
    #         resize_keyboard=True,
    #     ),
    # )


# @training_feedback_poll_router.message(TrainingFeedbackStates.failed_exercises,
#                                        text == "нет, справился со всеми")
# async def process_failed_exercises(message: Message, state: FSMContext) -> None:
#     await state.update_data(failed_exercises=message.text)  # TODO: Parse for backend correctly
#     await state.set_state(TrainingFeedbackStates.doddle_exercises)
#     await message.answer(
#         "Doddle exercises",  # TODO: from db
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text="нет, все были в меру тяжелыми"),
#                     KeyboardButton(text="1"),
#                     KeyboardButton(text="2"),  # TODO: Change to inline multichoice
#                 ],
#             ],
#             resize_keyboard=True,
#         ),
#     )


# @training_feedback_poll_router.message(TrainingFeedbackStates.failed_exercises,
#                                        ~(text == "нет, справился со всеми"))
# async def process_failed_exercises(message: Message, state: FSMContext) -> None:
#     await state.update_data(failed_exercises=message.text)  # TODO: Parse for backend correctly
#     await state.set_state(TrainingFeedbackStates.fail_reason)
#     await message.answer(
#         "fail reason",  # TODO: from db
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text="причина раз"),
#                     KeyboardButton(text="причина 2"),
#                     KeyboardButton(text="3"),
#                 ],
#             ],
#             resize_keyboard=True,
#         ),
#     )


# @training_feedback_poll_router.message(TrainingFeedbackStates.fail_reason)
# async def process_fail_reason(message: Message, state: FSMContext) -> None:
#     await state.update_data(fail_reason=message.text)  # TODO: Parse for backend correctly
#     await state.set_state(TrainingFeedbackStates.doddle_exercises)
#     await message.answer(
#         "Doddle exercises",  # TODO: from db
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text="нет, все были в меру тяжелыми"),
#                     KeyboardButton(text="1"),
#                     KeyboardButton(text="2"),  # TODO: Change to inline multichoice
#                 ],
#             ],
#             resize_keyboard=True,
#         ),
#     )


# @training_feedback_poll_router.message(TrainingFeedbackStates.doddle_exercises,
#                                        ~(text == "нет, все были в меру тяжелыми"))
# async def process_doddle_exercises(message: Message, state: FSMContext) -> None:
#     await state.update_data(doddle_exercises=message.text)  # TODO: Parse for backend correctly
#     await state.set_state(TrainingFeedbackStates.doddle_reason)
#     await message.answer(
#         "doddle reason",  # TODO: from db
#         reply_markup=ReplyKeyboardMarkup(
#             keyboard=[
#                 [
#                     KeyboardButton(text="причина раз"),
#                     KeyboardButton(text="причина 2"),
#                     KeyboardButton(text="3"),
#                 ],
#             ],
#             resize_keyboard=True,
#         ),
#     )


async def save_and_finish(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    result = prepare_poll_result(data, TRAINING_FEEDBACK_POLL_NAME)
    if await upload_poll_result(message, result):
        # Send message
        await message.answer('Ты молодец! Я обязательно учту это.')
        await message.answer(
            "Спасибо за обратную связь! Это поможет мне сделать твои тренировки лучше. Возвращайся, когда снова понадобится моя помощь!",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="главное меню"),
                    ],
                ],
                resize_keyboard=True,
            ),
        )
        logger.info(f'{get_user_string(message)} successfully sent training feedback poll result ({result})')
    else:
        # Send message
        await message.answer(
            'Что-то пошло не так. Попробуй еще раз.',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [
                        KeyboardButton(text="перейти к вопросам фидбека"),
                    ],
                    [
                        KeyboardButton(text="главное меню"),
                    ],
                ],
                resize_keyboard=True,
            ),
        )
        logger.warning(f'{get_user_string(message)} failed to sent training feedback poll result')
    logger.info(f'{get_user_string(message)} finished training feedback poll')


# @training_feedback_poll_router.message(TrainingFeedbackStates.doddle_exercises,
#                                        text == "нет, все были в меру тяжелыми")
# async def process_doddle_exercises(message: Message, state: FSMContext) -> None:
#     await state.update_data(doddle_exercises=message.text)  # TODO: Parse for backend correctly
#     await state.set_state(TrainingFeedbackStates.finish)
#     await save_and_finish(message, state)


# @training_feedback_poll_router.message(TrainingFeedbackStates.doddle_reason)
# async def process_doddle_reason(message: Message, state: FSMContext) -> None:
#     await state.update_data(doddle_reason=message.text)  # TODO: Parse for backend correctly
#     await state.set_state(TrainingFeedbackStates.finish)
#     await save_and_finish(message, state)
