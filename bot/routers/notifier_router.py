import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton
from loguru import logger

from bot.api import get_all_users
from bot.bot import bot
from bot.utils import get_user_string

notifier_router = Router()


class NotifierRouterStates(StatesGroup):
    message = State()


async def send_message(user_id: int, message: Message, disable_notification: bool = False) -> bool:
    # Try to send message safely
    try:
        await bot.copy_message(user_id, from_chat_id=message.chat.id, message_id=message.message_id,
                               disable_notification=disable_notification)
    except Exception as error:
        logger.error(f"Error while sending message to [ID:{user_id}]: {error}")
        logger.exception(error)
        return False
    logger.info(f"Target [ID:{user_id}]: success")
    return True


async def broadcaster(message: Message) -> int:
    count = 0
    try:
        users = await get_all_users(message)
        if users is not None:
            for user in users:
                tg_id = user['telegram_id']
                if await send_message(tg_id, message):
                    count += 1
                await asyncio.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)
        else:
            logger.warning(f"{get_user_string(message)} failed to get users list [broadcaster]")
    finally:
        logger.info(f"{get_user_string(message)}: sent {count} messages successfully")
    return count


@notifier_router.message(Command(commands=['notify_all']))
async def command_notify_all(message: Message, state: FSMContext) -> None:

    # Send message
    await message.answer('Введите сообщение, которое хотите отправить всем пользователям:', reply_markup=ReplyKeyboardRemove())
    # Set state
    await state.set_state(NotifierRouterStates.message)
    logger.info(f'{get_user_string(message)} requested a notification to all users [/notify_all]')


@notifier_router.message(NotifierRouterStates.message)
async def call_broadcaster(message: Message, state: FSMContext) -> None:
    # Get number of success sent messages
    count = await broadcaster(message)
    logger.info(f'{get_user_string(message)} sent a notification to all users [{count} messages]: {message.text} {message}')
    # Reset state
    await state.clear()
    # Send message
    if count:
        await message.answer(
            f'Успешно отправлено {count} сообщ. всем пользователям',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="главное меню")]],
                resize_keyboard=True,
            ),
        )
    else:
        await message.answer(
            'Не удалось отправить сообщение ни одному пользователю',
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="главное меню")]],
                resize_keyboard=True,
            ),
        )


