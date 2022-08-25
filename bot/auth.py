from datetime import datetime, timedelta
from datetime import timezone
from typing import Any, Optional

import jwt
from aiogram import types as aiogram_types
from aiohttp import ClientSession
from aiohttp.typedefs import LooseHeaders

from settings import API_TOKEN, JWT_EXPIRATION_TIME


def jwt_encode(payload: dict[str, Any]):
    reg = {
        "exp": datetime.now(tz=timezone.utc) + timedelta(seconds=JWT_EXPIRATION_TIME),
        "iss": "telegram:bot",
        "iat": datetime.now(tz=timezone.utc)
    }
    payload.update(reg)
    return jwt.encode(payload, API_TOKEN, algorithm="HS256")


def generate_token(user: aiogram_types.User):
    return jwt_encode({"tg_user": dict(user)})


class SportSession(ClientSession):
    keyword = 'Bearer'

    def __init__(self, token: str, headers: Optional[LooseHeaders] = None, *args, **kwargs) -> None:
        if headers is None:
            headers = {}
        headers.update({"Authorization": f"{self.keyword} {token}"})
        super().__init__(headers=headers, *args, **kwargs)


class SportTelegramSession(SportSession):
    def __init__(self, user: aiogram_types.User, *args, **kwargs) -> None:
        super().__init__(token=generate_token(user), *args, **kwargs)
