from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.types.bot_command_scope import BotCommandScopeChat
from .config import _ProfileStatesGroup
from ..bot_config import dp, bot
from ..keyboards import main_kb
from googlesheets import Users, Comparison
from database import (Database,
                      get_prompt_add_user,
                      get_prompt_update_nickname,
                      PROMPT_VIEW_USERS)
from ..bot_config import default_commands


WELCOME = """
👋 Привет, проходите турниры и набирайте баллы

📍Придумайте Ник, который будет отображаться в турнирах
📍В разделе "Текущие турниры" просмотрите доступные Вам турниры
📍О начале турниров Вы будете оповещены 

Введите свой Ник⬇️⬇️⬇️
"""

HELP_TEXT = """
/start - запустить бота
/help - помощь
/nickname - изменить псевдоним
/current_tournaments - текущие турниры
"""


@dp.message_handler(Command('start'))
async def start(message: types.Message) -> None:
    user_chat_id = str(message.chat.id)
    username = message.from_user.username
    if not username:
        username = message.from_user.full_name

    comparsion = Comparison()
    user_tournaments = comparsion.get_user_tournaments(user_chat_id)

    if user_tournaments:
        db = Database()
        users = [i['chat_id'] for i in db.get_data_list(PROMPT_VIEW_USERS)]

        if user_chat_id not in users:
            db.action(          # add user to the users database
                get_prompt_add_user(
                    username=username, chat_id=user_chat_id
                )
            )
            await _ProfileStatesGroup.get_start_nickname.set()
            await message.answer(WELCOME)
            return
        
    await message.answer(
        text="👋 Привет, проходите турниры и набирайте баллы",
        reply_markup=main_kb
    )
    await bot.set_my_commands(
        default_commands, scope=BotCommandScopeChat(message.chat.id) 
    )
        

@dp.message_handler(state=_ProfileStatesGroup.get_start_nickname)
async def get_start_nickname(message: types.Message,
                             state: FSMContext) -> None:
    nickname = message.text
    user_chat_id = str(message.chat.id)
    username = message.from_user.username
    if not username:
        username = message.from_user.full_name

    db = Database()
    all_users = db.get_data_list(PROMPT_VIEW_USERS)

    nicknames = [i['nickname'] for i in all_users]

    if nickname in nicknames:
        await message.answer(
            '❌❌Такой псевдоним уже занят, напишите другой'
        )
        return
    
    u = Users()         # add user to the users table 
    u.add_user(
        chat_id=user_chat_id, username=username, nickname=nickname
    )
    
    prompt = get_prompt_update_nickname(chat_id=user_chat_id,
                                        new_nick=nickname)
    db.action(*prompt)
    
    await state.finish()
    await message.answer(
        text="✅ Ник принят",
        reply_markup=main_kb
    )
    await bot.set_my_commands(
        default_commands, scope=BotCommandScopeChat(message.chat.id) 
    )



@dp.message_handler(Text(equals='🆘Помощь'))
@dp.message_handler(Command('help'))
async def help(message: types.Message) -> None:
    await message.answer(HELP_TEXT)