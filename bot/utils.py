import re
from typing import Tuple

from aiogram.types import Message

from loguru import logger
from bot import auth
from bot.routers import POLL_NAMES

API_URL = 'http://innosport.batalov.me/api'


def escape_to_markdownv2(text: str):
    #  To be escaped: '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    return re.sub(r'([_*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


def escape_to_markdown(text: str):
    #  To be escaped: ''_', '*', '`', '[', ']'
    return re.sub(r'([_*\[\]`])', r'\\\1', text)


async def get_auth_status(message: Message):
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/profile/me') as response:
            json = await response.json()
            status_code = response.status
    logger.info(f'User {message.from_user.id} status code: {status_code}')  # TODO: revise
    return status_code, json


async def suggest_training(message: Message, params: dict) -> dict:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/suggest', params=params) as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        return dict(json)
    else:
        # К сожалению, тренировку сгенерировать не удалось. Подойди к тренеру и попроси его помочь.
        pass  # TODO: Handle error here or handle it in the caller?


async def fetch_poll_by_name(message: Message, poll_name: str) -> dict:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/poll/{poll_name}') as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        return dict(json)


async def upload_poll_result_by_name(message: Message, result: dict) -> Tuple[int, dict]:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/poll_result', data=result) as response:
            json = await response.json()
            status_code = response.status
    return status_code, json


async def passed_intro_poll(message: Message) -> bool:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/poll_result/{POLL_NAMES["intro_poll"]}') as response:
            status_code = response.status
    return status_code == 200
