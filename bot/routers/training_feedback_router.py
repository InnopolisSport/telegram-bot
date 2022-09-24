from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

from loguru import logger
from bot import auth
from bot.filters import any_digits, text
from bot.routers import POLL_NAMES
from bot.utils import fetch_poll_by_name

training_feedback_poll_router = Router()
TRAINING_FEEDBACK_POLL_NAME = POLL_NAMES['training_feedback_poll']
TRAINING_FEEDBACK_POLL = dict()


class TrainingFeedbackStates(StatesGroup):
    five_point_scale = State()
    breaks = State()
    failed_exercises = State()
    fail_reason = State()  # Optional
    doddle_exercises = State()
    doddle_reason = State()  # Optional

    finish = State()


@training_feedback_poll_router.message(commands=["training_feedback"])
@training_feedback_poll_router.message(text == "training feedback")
@training_feedback_poll_router.message(text == "тренировка прошла успешно!")
async def command_training_feedback(message: Message, state: FSMContext) -> None:
    TRAINING_FEEDBACK_POLL = await fetch_poll_by_name(message, TRAINING_FEEDBACK_POLL_NAME)
    await state.clear()  # to ensure that we are starting from the beginning
    await state.set_state(TrainingFeedbackStates.five_point_scale)
    await message.answer('Оцените тренировку по шкале от 1 до 5')
    await message.answer(
        '5point scale with info',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text='1'),
                    KeyboardButton(text='2'),
                    KeyboardButton(text='3'),
                    KeyboardButton(text='4'),
                    KeyboardButton(text='5'),
                ]
            ],
            resize_keyboard=True,
        ))


@training_feedback_poll_router.message(TrainingFeedbackStates.five_point_scale, any_digits)  # TODO: add filter for 1-5 combined strings
async def process_five_point_scale(message: Message, state: FSMContext) -> None:
    await state.update_data(five_point_scale=int(message.text))  # TODO: Parse correctly
    await state.set_state(TrainingFeedbackStates.breaks)
    await message.answer(
        "Breaks",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="ни одного"),
                ],
                [
                    KeyboardButton(text="ни одного"),
                ],
                [
                    KeyboardButton(text="ни одного"),
                ],
                [
                    KeyboardButton(text="ни одного"),
                ],
                [
                    KeyboardButton(text="ни одного"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.five_point_scale)
async def process_five_point_scale(message: Message, state: FSMContext) -> None:
    await message.answer("Breaks again")


@training_feedback_poll_router.message(TrainingFeedbackStates.breaks)
async def process_breaks(message: Message, state: FSMContext) -> None:
    await state.update_data(breaks=message.text)  # TODO: Parse for backend into enum
    await state.set_state(TrainingFeedbackStates.failed_exercises)
    # TODO: Get list of exercises with number as in suggested training
    await message.answer(
        "Failed exercises",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="нет, справился со всеми"),
                    KeyboardButton(text="1"),
                    KeyboardButton(text="2"),  # TODO: Change to inline multichoice
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.failed_exercises,
                                       text == "нет, справился со всеми")
async def process_failed_exercises(message: Message, state: FSMContext) -> None:
    await state.update_data(failed_exercises=message.text)  # TODO: Parse for backend correctly
    await state.set_state(TrainingFeedbackStates.doddle_exercises)
    await message.answer(
        "Doddle exercises",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="нет, все были в меру тяжелыми"),
                    KeyboardButton(text="1"),
                    KeyboardButton(text="2"),  # TODO: Change to inline multichoice
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.failed_exercises,
                                       text != "нет, справился со всеми")
async def process_failed_exercises(message: Message, state: FSMContext) -> None:
    await state.update_data(failed_exercises=message.text)  # TODO: Parse for backend correctly
    await state.set_state(TrainingFeedbackStates.fail_reason)
    await message.answer(
        "fail reason",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="причина раз"),
                    KeyboardButton(text="причина 2"),
                    KeyboardButton(text="3"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.fail_reason)
async def process_fail_reason(message: Message, state: FSMContext) -> None:
    await state.update_data(fail_reason=message.text)  # TODO: Parse for backend correctly
    await state.set_state(TrainingFeedbackStates.doddle_exercises)
    await message.answer(
        "Doddle exercises",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="нет, все были в меру тяжелыми"),
                    KeyboardButton(text="1"),
                    KeyboardButton(text="2"),  # TODO: Change to inline multichoice
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.doddle_exercises,
                                       text == "нет, все были в меру тяжелыми")
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    await state.update_data(doddle_exercises=message.text)  # TODO: Parse for backend correctly
    await state.set_state(TrainingFeedbackStates.finish)
    await message.answer(
        "Finish",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="главное меню"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.doddle_exercises,
                                       text != "нет, все были в меру тяжелыми")
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    await state.update_data(doddle_exercises=message.text)  # TODO: Parse for backend correctly
    await state.set_state(TrainingFeedbackStates.doddle_reason)
    await message.answer(
        "doddle reason",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="причина раз"),
                    KeyboardButton(text="причина 2"),
                    KeyboardButton(text="3"),
                ],
            ],
            resize_keyboard=True,
        ),
    )


@training_feedback_poll_router.message(TrainingFeedbackStates.doddle_reason)
async def process_fitness_info(message: Message, state: FSMContext) -> None:
    await state.update_data(doddle_reason=message.text)  # TODO: Parse for backend correctly
    await state.set_state(TrainingFeedbackStates.finish)
    await message.answer(
        "Finish",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="главное меню"),
                ],
            ],
            resize_keyboard=True,
        ),
    )
