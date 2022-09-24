import re
from typing import Tuple

from aiogram.types import Message

from bot import auth
from bot.routers import POLL_NAMES


def escape_to_markdownv2(text: str):
    #  To be escaped: '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    return re.sub(r'([_*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


def escape_to_markdown(text: str):
    #  To be escaped: ''_', '*', '`', '[', ']'
    return re.sub(r'([_*\[\]`])', r'\\\1', text)


async def fetch_poll_by_name(message: Message, poll_name: str) -> dict:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'http://innosport.batalov.me/api/poll/{poll_name}') as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        return dict(json)


async def upload_poll_result_by_name(message: Message, result: dict,  poll_name: str) -> Tuple[int, dict]:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'http://innosport.batalov.me/api/poll_result/{poll_name}', data=result) as response:
            json = await response.json()
            status_code = response.status
    return status_code, json


async def passed_intro_poll(message: Message) -> bool:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'http://innosport.batalov.me/api/poll_result/{POLL_NAMES["intro_poll"]}') as response:
            status_code = response.status
    return status_code == 200
