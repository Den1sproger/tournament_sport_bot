from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import (Database,
                      get_prompt_view_nickname)



class _ProfileStatesGroup(StatesGroup):
    get_nickname = State()
    get_start_nickname = State()


class Questions:
    # variables for the tournament's questions
    questions_day = []
    current_question_index_day: int
    questions_week = []
    current_question_index_week: int
    questions_month = []
    current_question_index_month: int


# decorator of checking user in the users database 
def check_user(func):
    async def wrapper(data: types.Message | types.CallbackQuery,
                      *args, **kwargs):
        try:
            message = data.message
        except Exception:
            message = data
        db = Database()
        nickname = db.get_data_list(
            get_prompt_view_nickname(str(message.chat.id))
        )
        if not nickname:
            await message.answer("❌❌У вас нет доступа к этой операции")
            return
        nickname = nickname[0]['nickname']

        return await func(data, db, nickname)
    return wrapper