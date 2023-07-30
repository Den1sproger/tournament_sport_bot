from aiogram import types
from .config import check_user
from ..bot_config import dp
from ..keyboards import get_question_ikb, get_tournaments_kb
from database import (Database,
                      TOURNAMENT_TYPES,
                      get_prompt_view_games,
                      get_prompt_view_rating,
                      get_prompt_view_nickname,
                      get_prompt_view_user_tournaments,
                      get_prompt_add_answer,
                      get_prompt_view_answer,
                      get_prompt_update_answer)



# variables for the tournament's questions

questions = []
current_question_index: int
current_tournament: str



def get_update_msg(current_game: dict,
                   answer: int = None) -> types.InlineKeyboardMarkup and str:
    # update the text and inline keyboards of the tournament message     
    coeff_1 = current_game['first_coeff']
    coeff_2 = current_game['second_coeff']
    draw_coeff = current_game['draw_coeff']
    coeffs_txt = ''
    if draw_coeff == None:
        coeffs = [coeff_1, coeff_2]
        coeffs_txt = f'П1-{coeff_1}  П2-{coeff_2}'
    else:
        coeffs = [coeff_1, coeff_2, draw_coeff]
        coeffs_txt = f'П1-{coeff_1}  X-{draw_coeff}  П2-{coeff_2}'

    msg_text = f'{current_tournament}\n' \
        f'{current_game["sport"]}\n' \
        f'МАТЧ:\n{current_game["first_team"]} - {current_game["second_team"]}\n' \
        f'НАЧАЛО: {current_game["begin_time"]}\n' \
        f'КОЭФФИЦИЕНТЫ: {coeffs_txt}\n\n' \
        f'ССЫЛКА: {current_game["url"]}\n' \
        'Ниже представлены баллы, которые вы можете получить при угадывании'
    
    return get_question_ikb(
        quantity=len(questions),
        current_question_number=current_question_index + 1,
        coeffs=coeffs, answer=answer
    ), msg_text


async def update_questions_data(callback: types.CallbackQuery) -> None:
    if questions:
        db = Database()
        answer = db.get_data_list(
            get_prompt_view_answer(
                chat_id=str(callback.message.chat.id),
                tournament=current_tournament,
                game_key=questions[current_question_index]['game_key']
            )
        )
        if answer:
            answer = answer[0]['answer']
        else:
            answer = None
            
        current_game = questions[current_question_index]
        reply_markup, msg_text = get_update_msg(current_game, answer=answer)
        
        await callback.message.edit_text(msg_text)
        await callback.message.edit_reply_markup(reply_markup=reply_markup)
    else:
        await callback.message.edit_text('В данный момент игры отсутсвуют')

    

@dp.callback_query_handler(lambda callback: callback.data.startswith('tourn_'))
async def current_tournament(callback: types.CallbackQuery) -> None:
    tournament = callback.data.replace('tourn_', '')
    global current_tournament
    current_tournament = tournament

    tourn_type: str
    for type_ in TOURNAMENT_TYPES:
        if type_ in callback.data.upper():
            tourn_type = type_
            break

    db = Database()
    games = db.get_data_list(get_prompt_view_games(tourn_type))

    if games:
        global questions, current_question_index
        questions = games
        current_question_index = 0

        await update_questions_data(callback)
    else:
        await callback.answer('В данный момент игры отсутсвуют')


@dp.callback_query_handler(lambda callback: callback.data == 'next_question')
async def next_question(callback: types.CallbackQuery) -> None:
    global questions, current_question_index
    current_question_index += 1
    if (current_question_index + 1) > len(questions):
        current_question_index = 0

    await update_questions_data(callback)


@dp.callback_query_handler(lambda callback: callback.data == 'previous_question')
async def previous_question(callback: types.CallbackQuery) -> None:
    global questions, current_question_index
    current_question_index -= 1
    if current_question_index + 1 < 1:
        current_question_index = len(questions) - 1

    await update_questions_data(callback)


async def answer(answer: int,
                 callback: types.CallbackQuery) -> None:
    current_game = questions[current_question_index]
    reply_markup, _ = get_update_msg(
        current_game, answer=answer
    )
    db = Database()
    old_answer = db.get_data_list(
        get_prompt_view_answer(
            chat_id=str(callback.message.chat.id),
            tournament=current_tournament,
            game_key=questions[current_question_index]['game_key']
        )
    )
    prompt = ''
    if old_answer:
        if old_answer[0]['answer'] == answer:
            return
        prompt = get_prompt_update_answer(
            chat_id=str(callback.message.chat.id),
            tournament=current_tournament,
            game_key=current_game['game_key'],
            new_answer=answer
        )
    else:
        prompt = get_prompt_add_answer(
            chat_id=str(callback.message.chat.id),
            tournament=current_tournament,
            game_key=current_game['game_key'],
            answer=answer
        )
    db.action(prompt)
    
    await callback.message.edit_reply_markup(reply_markup=reply_markup)


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



@dp.callback_query_handler(lambda callback: callback.data == 'back_to_my_tournaments')
async def back_to_tourns(callback: types.CallbackQuery) -> None:
    global current_question_index, current_tournament, questions
    current_tournament = None
    current_question_index = 0
    questions = []
    
    user_chat_id = str(callback.message.chat.id)
    db = Database()

    nickname = db.get_data_list(
        get_prompt_view_nickname(user_chat_id)
    )[0]['nickname']
    msg_text = f'Список турниров, в которых Вы зарегистрированы\nВаш никнейм: {nickname}\nВыберите турнир'

    data_ts = db.get_data_list(
        get_prompt_view_user_tournaments(user_chat_id)
    )
    user_tournaments = [i['tournament'] for i in data_ts]

    await callback.message.edit_text(msg_text)
    await callback.message.edit_reply_markup(
        reply_markup=get_tournaments_kb(*user_tournaments)
    )