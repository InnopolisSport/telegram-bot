import re

from aiogram.fsm.context import FSMContext
from aiogram.types import Message


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
    return {'poll': poll_name, 'answers': [{q_id: answer} for q_id, answer in data.items() if q_id != 'q']}
