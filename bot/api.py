from aiogram.types import Message

from loguru import logger
from bot import auth
from bot.routers import POLL_NAMES
from bot.utils import get_user_string

API_URL = 'http://innosport.batalov.me/api'


async def get_auth_status(message: Message) -> dict:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/profile/me') as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        logger.info(f'{get_user_string(message)} is authorized ({status_code} {json})')
        return dict(json)
    else:
        logger.error(f'{get_user_string(message)} is not authorized ({status_code} {json})')
        return {}


async def suggest_training(message: Message, params: dict) -> dict:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/suggest', params=params) as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        logger.info(f'{get_user_string(message)} received suggested training ({status_code} {json})')
        return dict(json)
    else:
        logger.info(f'{get_user_string(message)} failed to receive suggested training ({status_code} {json})')
        return {}


async def fetch_poll_by_name(message: Message, poll_name: str) -> dict:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/poll/{poll_name}') as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        logger.info(f'{get_user_string(message)} successfully fetched the poll {poll_name} ({status_code} {json})')
        return dict(json)
    else:
        logger.error(f'{get_user_string(message)} failed to fetch the poll {poll_name} ({status_code} {json})')
        return {}


async def upload_poll_result(message: Message, result: dict) -> bool:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/poll_result', data=result) as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        logger.info(f'{get_user_string(message)} successfully upload poll result {result} ({status_code} {json})')
        return True
    else:
        logger.error(f'{get_user_string(message)} failed to upload poll result {result} ({status_code} {json})')
        return False


async def passed_intro_poll(message: Message) -> bool | None:
    async with auth.SportTelegramSession(message.from_user) as session:
        async with session.get(f'{API_URL}/training_suggestor/poll_result/{POLL_NAMES["intro_poll"]}') as response:
            status_code = response.status
    if status_code == 200:
        logger.info(f'{get_user_string(message)} passed intro poll ({status_code})')
        return True
    elif status_code == 404:
        logger.info(f'{get_user_string(message)} did not pass intro poll ({status_code})')
        return False
    else:
        logger.error(
            f'{get_user_string(message)} failed to check {POLL_NAMES["intro_poll"]} poll result ({status_code})')
        return None
