from aiogram.types import Message
from aiohttp import FormData
from loguru import logger

from bot import auth
from bot.routers import POLL_NAMES
from bot.utils import get_user_string

API_URL = 'http://innosport.batalov.me/api'


async def get_auth_status(message: Message) -> dict | None:
    async with auth.SportTelegramSession(message.from_user) as session:
        try:
            async with session.get(f'{API_URL}/profile/me', raise_for_status=True) as response:
                json = await response.json()
                status_code = response.status
        except Exception as error:
            logger.error(f'{get_user_string(message)} is not authorized (or failed to fetch) [{error}]')
            return None
        logger.info(f'{get_user_string(message)} is authorized ({status_code} {json})')
        return dict(json)


async def suggest_training(message: Message, params: dict) -> dict | None:
    async with auth.SportTelegramSession(message.from_user) as session:
        try:
            async with session.get(f'{API_URL}/training_suggestor/suggest', params=params, raise_for_status=True) as response:
                json = await response.json()
                status_code = response.status
        except Exception as error:
            logger.error(f'{get_user_string(message)} failed to suggest training ({error})')
            return None
        logger.info(f'{get_user_string(message)} received suggested training ({status_code} {json})')
        return dict(json)


async def fetch_poll_by_name(message: Message, poll_name: str) -> dict | None:
    async with auth.SportTelegramSession(message.from_user) as session:
        try:
            async with session.get(f'{API_URL}/training_suggestor/poll/{poll_name}', raise_for_status=True) as response:
                json = await response.json()
                status_code = response.status
        except Exception as error:
            logger.error(f'{get_user_string(message)} failed to fetch poll {poll_name} ({error})')
            return None
        logger.info(f'{get_user_string(message)} successfully fetched the poll {poll_name} ({status_code} {json})')
        return dict(json)


async def upload_poll_result(message: Message, data: dict) -> bool:
    async with auth.SportTelegramSession(message.from_user) as session:
        try:
            async with session.post(f'{API_URL}/training_suggestor/poll_result', json=data, raise_for_status=True) as response:
                json = await response.json()
                status_code = response.status
        except Exception as error:
            logger.error(f'{get_user_string(message)} failed to upload poll result {data} ({error})')
            return False
        logger.info(f'{get_user_string(message)} successfully upload poll result {data} ({status_code} {json})')
        return True


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


async def upload_training_result(message: Message, data: dict) -> bool:  # upload for getting sport hours
    async with auth.SportTelegramSession(message.from_user) as session:
        form_data = FormData(data)
        form_data._is_multipart = True
        async with session.post(f'{API_URL}/selfsport/upload', data=form_data) as response:
            json = await response.json()
            status_code = response.status
    if status_code == 200:
        logger.info(f'{get_user_string(message)} successfully upload training result {data} ({status_code} {json})')
        return True
    else:
        logger.error(f'{get_user_string(message)} failed to upload training result {data} ({status_code} {json})')
        return False


async def get_all_users(message: Message) -> list[dict] | None:
    async with auth.SportTelegramSession(message.from_user) as session:
        try:
            async with session.get(f'{API_URL}/training_suggestor/tg_users', raise_for_status=True) as response:
                json = await response.json()
                status_code = response.status
        except Exception as error:
            logger.error(f'{get_user_string(message)} failed to fetch all users ({error})')
            return None
        logger.info(f'{get_user_string(message)} successfully fetched all users ({status_code} {json})')
        return json
