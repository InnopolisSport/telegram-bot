from aiogram import F

ANY_DIGITS_REGEX = r"^(\d+)$"

text = F.text.casefold()
any_digits = F.text.regexp(ANY_DIGITS_REGEX)
