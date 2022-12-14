import re
from enum import Enum

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, \
    ReplyKeyboardRemove


class ErrorMessages(Enum):
    REQUEST_FAILED = "У каждого бота бывают сбои, извини. Скоро всё исправят, и ты сможешь повторить запрос"
    SUGGEST_TRAINING = "К сожалению, Что-то пошло не так и тренировку сгенерировать не удалось. Подойди к тренеру и попроси его помочь или попробуй снова"
    UNKNOWN_COMMAND = "У каждого бота бывают сбои. Извини, я не понял тебя"
    REPEAT_INPUT = "Кажется, ты ввёл неправильные данные. Попробуй снова"


INITIAL_INFLUENCE_RATIOS = {
    't': 1,
    'wl': 1,
}


async def main_menu_keyboard(message: Message, msg_text: str) -> None:
    await message.answer(
        msg_text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="составить тренировку"),
                ],
                [
                    KeyboardButton(text="показать расписание"),  # TODO: logic
                    # KeyboardButton(text="записаться на занятия"),  # TODO: logic
                ],
                # [
                #     KeyboardButton(text="изменить данные анкеты"),
                # ]
            ],
            resize_keyboard=True,
        )
    )


async def not_authorized_keyboard(message: Message) -> None:
    await message.answer(
        '''Чтобы мы продолжили работу, нужно авторизоваться в системе _innosport+_. Пожалуйста, зайди в профиль на сайте.''',
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="авторизоваться на сайте", url="https://innosport.batalov.me/"),
                ]
            ]
        )
    )
    ans = await message.answer('.', reply_markup=ReplyKeyboardRemove())
    await ans.delete()


def get_user_string(message: Message):
    return f'{message.from_user.full_name} (@{message.from_user.username}:{message.from_user.id})'


def escape_to_markdownv2(text: str):
    #  To be escaped: '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
    return re.sub(r'([_*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)


def escape_to_markdown(text: str):
    #  To be escaped: ''_', '*', '`', '[', ']'
    return re.sub(r'([_*\[\]`])', r'\\\1', text)


async def get_cur_state_name(state: FSMContext) -> str:
    return (await state.get_state()).split(':')[-1]


# Working with polls

def prepare_poll_questions(poll: list) -> dict:
    return {question['state']: question for question in poll}


def get_question_text_id(question: dict) -> tuple[str, str]:
    return question['question'], question['id']


def get_question_answers(question: dict) -> list:
    return [ans['answer'] for ans in question['answers']]


def prepare_poll_result(data: dict, poll_name: str) -> dict:
    return {
        'poll': poll_name,
        'answers': [{'question': q_id, 'answer': answer} for q_id, answer in data.items() if isinstance(q_id, int)]
    }


def get_influence_ratios(question: dict, answer: str) -> dict:
    for ans in question['answers']:
        if ans['answer'] == answer:
            return {
                't': 1 + ans['time_ratio_influence'],
                'wl': 1 + ans['working_load_ratio_influence'],
            }


def accumulate_influence_ratios(prev_ratios: dict, ratios: dict) -> dict:
    return {
        't': prev_ratios['t'] * ratios['t'],
        'wl': prev_ratios['wl'] * ratios['wl'],
    }
