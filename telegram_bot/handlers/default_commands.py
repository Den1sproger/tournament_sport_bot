from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, Text
from .config import _ProfileStatesGroup, check_user
from ..bot_config import dp
from ..keyboards import get_tournaments_kb
from database import (Database,
                      PROMPT_VIEW_USERS,
                      get_prompt_update_nickname,
                      get_prompt_view_user_tournaments)
from googlesheets import Users, Rating



# writing the internal nickname
@dp.message_handler(Text(equals='👨‍💼Ввести ник'))
@dp.message_handler(Command('nickname'))
@check_user
async def write_nickname(message: types.Message, *args) -> None:
    await _ProfileStatesGroup.get_nickname.set()
    await message.answer(
        'Введите ваш псевдоним, он будет использоваться далее во всех турнирах'
    )


# get the internal nickname
@dp.message_handler(state=_ProfileStatesGroup.get_nickname)
async def get_nickname(message: types.Message, state: FSMContext) -> None:
    nickname = message.text
    user_chat_id = str(message.chat.id)

    db = Database()
    all_users = db.get_data_list(PROMPT_VIEW_USERS)

    nicknames = {}
    for user in all_users:
        nicknames[user['chat_id']] = user['nickname']

    if nickname in list(nicknames.values()):
        await message.answer(
            '❌❌Такой псевдоним уже занят, напишите другой'
        )
        await state.finish()
        return
    
    try: old_nick = nicknames[user_chat_id]
    except KeyError: old_nick = None

    u = Users()             # update the nickname in users table 
    u.update_nickname(new_nick=nickname, chat_id=user_chat_id)     
    if old_nick:
        p = Rating()        # update the nickname in users table
        p.update_nickname(new_nick=nickname, old_nick=old_nick)

    prompts = get_prompt_update_nickname(    # update the nickname in the databases
        user_chat_id, new_nick=nickname, old_nick=old_nick
    )
    db.action(*prompts)

    await state.finish()
    await message.answer("✅Псевдоним записан")



# open the tournament games with the coefficients
@dp.message_handler(Text(equals='⚽️🏀🎾 Текущие турниры'))
@dp.message_handler(Command('current_tournaments'))
@check_user
async def current_tournaments(message: types.Message,
                              db: Database,
                              nickname: str) -> None:
    participants = [i['nickname'] for i in db.get_data_list(PROMPT_VIEW_USERS)]
    
    if nickname not in participants:
        await message.answer('У вас отсутсвует псевдоним, введите его')
        return
    
    msg_text = f'📋Список турниров, в которых Вы зарегистрированы\n📌Ваш ник: {nickname}\n⬇️Выберите турнир⬇️'
    data_ts = db.get_data_list(
        get_prompt_view_user_tournaments(nickname)
    )
    user_tournaments = [i['tournament'] for i in data_ts]
    await message.answer(
        text=msg_text, reply_markup=get_tournaments_kb(*user_tournaments)
    )