from aiogram import types
from aiogram.dispatcher.filters import Command, Text
from aiogram.dispatcher import FSMContext
from aiogram.types.bot_command_scope import BotCommandScopeChat
from .config import _ProfileStatesGroup
from ..bot_config import dp, bot
from ..keyboards import main_kb
from googlesheets import Users, Comparison, Rating
from database import (Database,
                      get_prompt_add_user,
                      get_prompt_update_nickname,
                      get_prompt_register_participant,
                      get_prompt_view_user_tournaments,
                      get_prompt_delete_user_tournaments,
                      get_prompt_add_user_tournament,
                      PROMPT_VIEW_USERS)
from ..bot_config import default_commands


WELCOME = """
👋👋👋Привет, здесь ты можешь участвовать в турнирах
📍За участие тебе будут начисляться баллы
📍Для начала введите псевдоним, который дальше будет использоваться в турнирах
📍Если что, вы всегда сможете заменить псевдоним

Ваш псевдоним⬇️⬇️⬇️
"""

HELP_TEXT = """
/start - запустить бота
/help - помощь
/nickname - изменить псевдоним
/current_tournaments - текущие турниры
/my_tournaments - мои турниры
/stop - прервать диалог
"""


@dp.message_handler(Command('start'))
async def start(message: types.Message) -> None:
    user_chat_id = str(message.chat.id)
    username = message.from_user.username
    if not username:
        username = message.from_user.full_name

    comparsion = Comparison()
    user_tournaments = comparsion.get_user_tournaments(user_chat_id)
    user_tournaments.sort()

    db = Database()
    data_ts = db.get_data_list(
        get_prompt_view_user_tournaments(user_chat_id)
    )
    last_tournaments = [i['tournament'] for i in data_ts]
    last_tournaments.sort()

    if user_tournaments and user_tournaments != last_tournaments:
        users = [i['chat_id'] for i in db.get_data_list(PROMPT_VIEW_USERS)]
        db.action(
            get_prompt_delete_user_tournaments(user_chat_id)
        )
        for item in user_tournaments:
            db.action(
                get_prompt_add_user_tournament(user_chat_id, item)
            )

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
        "Привет, здесь ты можешь участвовать в турнирах, за что тебе будут начисляться баллы",
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

    nicknames = {}
    for user in all_users:
        nicknames[user['chat_id']] = user['nickname']

    if nickname in list(nicknames.values()):
        await message.answer(
            '❌❌Такой псевдоним уже занят, напишите другой'
        )
        return
    
    u = Users()         # add user to the users table 
    u.add_user(
        chat_id=user_chat_id, username=username, nickname=nickname
    )
    
    comparsion = Comparison()
    user_tournaments = comparsion.get_user_tournaments(user_chat_id)

    r = Rating()        # add user to the rating table
    r.register_participant(nickname=nickname,
                           tournaments=user_tournaments)

    prompts = []
    for tourn in user_tournaments:
        prompts.append(get_prompt_register_participant(nickname, tourn)) 

    db = Database()
    db.action(*prompts)             # add user to the table with rating
    
    prompt = get_prompt_update_nickname(chat_id=user_chat_id,
                                        new_nick=nickname)
    db.action(*prompt)
    
    await state.finish()
    await message.answer(
        text="✅Псевдоним записан, вы можете участвовать в турнирах",
        reply_markup=main_kb
    )
    await bot.set_my_commands(
        default_commands, scope=BotCommandScopeChat(message.chat.id) 
    )



@dp.message_handler(Text(equals='🆘Помощь'))
@dp.message_handler(Command('help'))
async def help(message: types.Message) -> None:
    await message.answer(HELP_TEXT)