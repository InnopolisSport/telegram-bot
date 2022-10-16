from aiogram import F
from aiogram.types.message import ContentType
ANY_DIGITS_REGEX = r"^(\d+)$"

text = F.text.casefold()
any_digits = F.text.regexp(ANY_DIGITS_REGEX)
connected_website = F.content_type == ContentType.CONNECTED_WEBSITE
