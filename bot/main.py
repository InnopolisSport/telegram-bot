import asyncio
from aiogram import types
from aiogram.filters import Command
from loguru import logger
from bot.loader import dp, bot
from bot import auth


async def on_startup_event():
    logger.info('Bot started')


async def on_shutdown_event():
    logger.info('Bot stopped')


def start_bot():
    try:
        dp.startup.register(on_startup_event)
        dp.shutdown.register(on_shutdown_event)
        dp.run_polling(bot)
    except Exception as err:
        logger.critical(f'Bot failed to start: {err}')


@dp.message(Command(commands=['start', 'help']))
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    message_body = "Hi\!\nI'm EchoBot\!\nPowered by aiogram\."
    await message.reply(message_body)
    logger.info(f'Replied message:\n {message_body}')


@dp.message(Command(commands=['me']))
async def get_me(message: types.Message):
    async with auth.SportTelegramSession(message.from_user) as session:
        await asyncio.sleep(10)
        async with session.get('http://localhost/api/profile/history_with_self/15') as response:
            text = await response.text()
    print(text)
    await message.reply(text)
    logger.info(f'Replied message:\n {text}')


@dp.message()
async def echo(message: types.Message):
    """
    Handler will forward received message back to the sender
    By default, message handler will handle all message types (like text, photo, sticker and etc.)
    """
    try:
        # Send copy of the received message
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        # But not all the types is supported to be copied so need to handle it
        await message.answer("Nice try!")
