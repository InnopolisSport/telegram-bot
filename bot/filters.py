from aiogram import F

ANY_DIGITS_REGEX = r"^(\d+)$"

any_digits = F.text.regexp(ANY_DIGITS_REGEX)
