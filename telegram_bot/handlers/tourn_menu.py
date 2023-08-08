from aiogram import types
from .config import check_user
from ..bot_config import dp
from ..keyboards import get_question_ikb, get_tournaments_kb
from database import (Database,
                      TOURNAMENT_TYPES,
                      PROMPT_VIEW_CURRENT_CHAT_iDS,
                      get_prompt_add_current_info,
                      get_prompt_increase_current_index,
                      get_prompt_decrease_current_index,
                      get_prompt_view_current_info,
                      get_prompt_update_current_info,
                      get_prompt_delete_current_info,
                      get_prompt_update_current_index,
                      get_prompt_view_games,
                      get_prompt_view_rating,
                      get_prompt_view_nickname,
                      get_prompt_view_user_tournaments,
                      get_prompt_add_answer,
                      get_prompt_view_answer,
                      get_prompt_update_answer)



# variables for the tournament's questions

questions = {
    'FAST': [],
    'STANDART': [],
    'SLOW': []
}
fast_questions = []
stan_questions = []
slow_questions = []



def get_type_by_tourn_name(tourn_name: str) -> str:
    tourn_type: str
    for type_ in TOURNAMENT_TYPES:
        if type_ in tourn_name.upper():
            tourn_type = type_
            break
    return tourn_type


def get_current_data(db: Database, chat_id: str) -> dict:
    data = db.get_data_list(
        get_prompt_view_current_info(chat_id)
    )[0]

    current_index = data.get('current_index')

    current_tournament = data.get('current_tournament')
    tourn_type = get_type_by_tourn_name(current_tournament)

    games_number = len(questions[tourn_type])
    if current_index < 0:
        current_index = games_number - 1
        db.action(get_prompt_update_current_index(chat_id, current_index))
    elif current_index >= games_number:
        current_index = 0
        db.action(get_prompt_update_current_index(chat_id, current_index))

    current_game = questions[tourn_type][current_index]

    return {'index': current_index,
            'tournament': current_tournament,
            'type': tourn_type}, current_game


# update the text and inline keyboards of the tournament message     
def get_update_msg(game: dict,
                   tournament: str,
                   index: int,
                   type_: str,
                   answer: int = None) -> types.InlineKeyboardMarkup and str:    
    coeff_1 = game['first_coeff']
    coeff_2 = game['second_coeff']
    draw_coeff = game['draw_coeff']
    coeffs_txt = ''
    if draw_coeff == None:
        coeffs = [coeff_1, coeff_2]
        coeffs_txt = f'П1-{coeff_1}  П2-{coeff_2}'
    else:
        coeffs = [coeff_1, coeff_2, draw_coeff]
        coeffs_txt = f'П1-{coeff_1}  X-{draw_coeff}  П2-{coeff_2}'

    msg_text = f'{tournament}\n' \
        f'{game["sport"]}\n\n' \
        f'МАТЧ: {game["first_team"]} - {game["second_team"]}\n' \
        f'НАЧАЛО: {game["begin_time"]}\n' \
        f'КОЭФФИЦИЕНТЫ: {coeffs_txt}\n\n' \
        f'ОБЗОР МАТЧА:\n{game["url"]}'
    
    return get_question_ikb(
        quantity=len(questions[type_]),
        current_question_index=index,
        coeffs=coeffs, answer=answer
    ), msg_text


# update data of questions for the message
async def update_questions_data(callback: types.CallbackQuery) -> None:
    user_chat_id = str(callback.message.chat.id)
    db = Database()
    data, current_game = get_current_data(db, user_chat_id)

    answer = db.get_data_list(
        get_prompt_view_answer(
            chat_id=user_chat_id, tournament=data['tournament'],
            game_key=current_game['game_key']
        )
    )
    if answer:
        answer = answer[0]['answer']
    else:
        answer = None
        
    reply_markup, msg_text = get_update_msg(
        game=current_game, answer=answer, index=data['index'],
        tournament=data['tournament'], type_=data['type']
    )
    
    await callback.message.edit_text(msg_text)
    await callback.message.edit_reply_markup(reply_markup=reply_markup)

    
async def answer(answer: int,
                 callback: types.CallbackQuery) -> None:
    user_chat_id = str(callback.message.chat.id)
    db = Database()

    data, current_game = get_current_data(db, user_chat_id)

    game_key = current_game['game_key']
    index = data['index']
    tournament = data['tournament']
    type_= data['type']

    reply_markup, _ = get_update_msg(
        game=current_game, answer=answer, index=index,
        tournament=tournament, type_= type_
    )

    old_answer = db.get_data_list(
        get_prompt_view_answer(
            chat_id=user_chat_id,
            tournament=tournament, game_key=game_key
        )
    )
    prompt = ''
    if old_answer:
        if old_answer[0]['answer'] == answer:
            return
        prompt = get_prompt_update_answer(
            chat_id=user_chat_id, tournament=tournament,
            game_key=game_key, new_answer=answer
        )
    else:
        prompt = get_prompt_add_answer(
            chat_id=user_chat_id, tournament=tournament,
            game_key=game_key, answer=answer
        )
    db.action(prompt)
    
    await callback.message.edit_reply_markup(reply_markup=reply_markup)



# select the tournament
@dp.callback_query_handler(lambda callback: callback.data.startswith('tourn_'))
async def current_tournament(callback: types.CallbackQuery) -> None:
    tournament = callback.data.replace('tourn_', '')
    tourn_type = get_type_by_tourn_name(tournament)
    
    db = Database()
    games = db.get_data_list(get_prompt_view_games(tourn_type))

    global questions

    if games:
        if games != questions[tourn_type]:
            questions[tourn_type] = games

        user_chat_id = str(callback.message.chat.id)
        chat_ids = [i['chat_id'] for i in db.get_data_list(PROMPT_VIEW_CURRENT_CHAT_iDS)]
        if user_chat_id not in chat_ids:
            db.action(
                get_prompt_add_current_info(user_chat_id, tournament)
            )
        else:
            db.action(
                get_prompt_update_current_info(user_chat_id, tournament)
            )
        await update_questions_data(callback)

    else:
        await callback.answer('В данный момент турнир недоступен')



# next question
@dp.callback_query_handler(lambda callback: callback.data == 'next_question')
async def next_question(callback: types.CallbackQuery) -> None:
    user_chat_id = str(callback.message.chat.id)
    db = Database()
    db.action(get_prompt_increase_current_index(user_chat_id))

    await update_questions_data(callback)


# previous question
@dp.callback_query_handler(lambda callback: callback.data == 'previous_question')
async def previous_question(callback: types.CallbackQuery) -> None:
    user_chat_id = str(callback.message.chat.id)
    db = Database()
    db.action(get_prompt_decrease_current_index(user_chat_id))

    await update_questions_data(callback)



@dp.callback_query_handler(lambda callback: callback.data == 'first_team')
async def first_team(callback: types.CallbackQuery) -> None:
    await answer(answer=1, callback=callback)


@dp.callback_query_handler(lambda callback: callback.data == 'second_team')
async def second_team(callback: types.CallbackQuery) -> None:
    await answer(answer=2, callback=callback)


@dp.callback_query_handler(lambda callback: callback.data == 'draw')
async def draw(callback: types.CallbackQuery) -> None:
    await answer(answer=3, callback=callback)



# get the fisrt 10 participants sorted by scores
@dp.callback_query_handler(lambda callback: callback.data.startswith('leader_'))
@check_user
async def get_leaderboard(callback: types.CallbackQuery,
                          db: Database,
                          nickname: str) -> None:
    tournament_name = callback.data.replace('leader_', '')

    db = Database()
    games = db.get_data_list(get_prompt_view_games(tourn_name=tournament_name))

    if games:
        rating = db.get_data_list(get_prompt_view_rating(tournament_name))
        msg_text = f'🏆Таблица лидеров {tournament_name}:\n'

        own_number = 0
        own_score = 0
        count = 0
        for participant in rating:
            count += 1
            if count <= 10:
                msg_text += f'{count}. {participant["nickname"]}: {participant["scores"]}\n'
            if participant["nickname"] == nickname:
                own_number = count
                own_score = participant["scores"]
                if count >= 10: break

        # user's position
        msg_text += f'\nВаша позиция в списке: {own_number} из {len(rating)}' \
                    f'\n{own_number}. {nickname}: {own_score}'
        await callback.message.answer(msg_text)
    else:
        await callback.answer('В данный момент таблица лидеров недоступна')


# come back to the menu of users tournaments
@dp.callback_query_handler(lambda callback: callback.data == 'back_to_my_tournaments')
async def back_to_tourns(callback: types.CallbackQuery) -> None:
    user_chat_id = str(callback.message.chat.id)
    db = Database()

    db.action(
        get_prompt_delete_current_info(user_chat_id)
    )

    nickname = db.get_data_list(
        get_prompt_view_nickname(user_chat_id)
    )[0]['nickname']
    msg_text = f'Список турниров, в которых Вы зарегистрированы\nВаш никнейм: {nickname}\nВыберите турнир'

    data_ts = db.get_data_list(
        get_prompt_view_user_tournaments(nickname)
    )
    user_tournaments = [i['tournament'] for i in data_ts]

    await callback.message.edit_text(msg_text)
    await callback.message.edit_reply_markup(
        reply_markup=get_tournaments_kb(*user_tournaments)
    )