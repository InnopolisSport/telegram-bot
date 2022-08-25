from aiogram import Bot, Dispatcher
from settings import API_TOKEN


# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode="MarkdownV2")
dp = Dispatcher()
