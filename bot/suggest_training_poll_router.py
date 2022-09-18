import logging
from typing import Any, Dict

from aiogram import F, Router, html
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove

suggest_training_poll_router = Router()


class SuggestTrainingPollStates(StatesGroup):
    goal = State()
    sport = State()
    training = State()  # includes training_time saving


@suggest_training_poll_router.message(commands=["suggest_training"])
@suggest_training_poll_router.message(F.text.casefold() == "suggest training")
async def command_suggest_training(message: Message, state: FSMContext) -> None:
    print(F.text)
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
        "TRAINING_TIME",
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
    # Parsing training_time
    await state.update_data(training_time=int(message.text) * 60)  # TODO: Parse for backend correctly
    # TODO: Add call to backend suggest_training()
    # TODO: Parse backend response into beautiful training
    data = await state.get_data()
    print(data)
    await state.clear()
    await message.answer(
        "TRAINING PARSED: " + str(data),
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


@suggest_training_poll_router.message(F.text.casefold() == "объясни, что это значит")
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


@suggest_training_poll_router.message(F.text.casefold() == "ок, все понятно")
@suggest_training_poll_router.message(F.text.casefold() == "ок, понял")
async def process_training_understood(message: Message, state: FSMContext) -> None:
    # await state.set_state(Menu.main)  # TODO: Add main menu state
    await message.answer(
        "TRAINING UNDERSTOOD",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="главное меню"),
                ],
            ],
            resize_keyboard=True,
        ),
    )
