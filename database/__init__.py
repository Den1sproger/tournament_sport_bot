from .db_work import Database



TOURNAMENT_TYPES = ['SLOW', 'STANDART', 'FAST']
PROMPT_VIEW_USERS = "SELECT chat_id, nickname FROM users;"
PROMPT_VIEW_CURRENT_CHAT_iDS = "SELECT chat_id FROM current_questions;"


def get_prompt_view_games(tourn_type: str = None,
                          tourn_name: str = None) -> str:
    if tourn_type:
        return "SELECT game_key, sport, begin_time, first_team, first_coeff, second_team," \
            f"second_coeff, draw_coeff, url FROM games WHERE game_status=1 AND tourn_type='{tourn_type}';"
    if tourn_name:
        return "SELECT game_key, sport, begin_time, first_team, first_coeff, second_team," \
            f"second_coeff, draw_coeff, url FROM games WHERE game_status=1 AND '{tourn_name.upper()}' LIKE concat('%', tourn_type, '%');"


def get_prompt_view_rating(tournament: str) -> str:
    return f"SELECT nickname, scores FROM participants WHERE tournament='{tournament}' ORDER BY scores DESC;"


def get_prompt_add_user(username: str,
                        chat_id: str) -> str:
    return f"INSERT INTO users (username, chat_id, all_scores)" \
           f"VALUES ('{username}', '{chat_id}', 0);"


def get_prompt_register_participant(nickname: str,
                                    tournament: str) -> str:
    return f"INSERT INTO participants (nickname, tournament, scores) VALUES ('{nickname}', '{tournament}', 0);" 


def get_prompt_update_nickname(chat_id: str,
                               new_nick: str,
                               old_nick: str = None) -> list[str]:
    prompts = [f"UPDATE users SET nickname='{new_nick}' WHERE chat_id='{chat_id}';"]
    if old_nick:
        prompts.append(f"UPDATE participants SET nickname='{new_nick}' WHERE nickname='{old_nick}';")
    return prompts


def get_prompt_view_nickname(chat_id: str) -> str:
    return f"SELECT nickname FROM users WHERE chat_id='{chat_id}';"


def get_prompt_view_current_info(chat_id: str) -> str:
    return f"SELECT current_index, current_tournament FROM current_questions WHERE chat_id='{chat_id}';"


def get_prompt_increase_current_index(chat_id: str) -> str:
    return f"UPDATE current_questions SET current_index=current_index+1 WHERE chat_id='{chat_id}';"


def get_prompt_decrease_current_index(chat_id: str)-> str:
    return f"UPDATE current_questions SET current_index=current_index-1 WHERE chat_id='{chat_id}';"


def get_prompt_update_current_info(chat_id: str,
                                   new_tourn: str) -> str:
    return f"UPDATE current_questions SET current_tournament='{new_tourn}', current_index=0  WHERE chat_id='{chat_id}';"


def get_prompt_update_current_index(chat_id: str,
                                    new_index: int) -> str:
    return f"UPDATE current_questions SET current_index={new_index} WHERE chat_id='{chat_id}';"


def get_prompt_add_current_info(chat_id: str,
                                tournament: str) -> str:
    return f"INSERT INTO current_questions (chat_id, current_index, current_tournament) VALUES ('{chat_id}', 0, '{tournament}');"


def get_prompt_delete_current_info(chat_id: str) -> str:
    return f"DELETE FROM current_questions WHERE chat_id='{chat_id}';"


def get_prompt_add_answer(chat_id: str,
                          tournament: str,
                          answer: int,
                          game_key: str) -> str:
    return f"INSERT INTO answers (chat_id, game_key, tournament, answer) VALUES ('{chat_id}', '{game_key}', '{tournament}', {answer});"


def get_prompt_view_answer(chat_id: str,
                           tournament: str,
                           game_key: str) -> str:
    return f"SELECT answer FROM answers WHERE chat_id='{chat_id}' AND game_key='{game_key}' AND tournament='{tournament}';"


def get_prompt_update_answer(chat_id: str,
                             tournament: str,
                             game_key: str,
                             new_answer: int) -> str:
    return f"UPDATE answers SET answer={new_answer} WHERE chat_id='{chat_id}' AND game_key='{game_key}' AND tournament='{tournament}';"


def get_prompt_view_user_tournaments(nickname: str) -> str:
    return f"SELECT tournament FROM participants WHERE nickname='{nickname}';"



__all__ = [
    'Database',
    'TOURNAMENT_TYPES',
    'PROMPT_VIEW_USERS',
    'PROMPT_VIEW_CURRENT_CHAT_iDS',
    'get_prompt_view_current_info',
    'get_prompt_update_current_index',
    'get_prompt_update_current_info',
    'get_prompt_increase_current_index',
    'get_prompt_decrease_current_index',
    'get_prompt_add_current_info',
    'get_prompt_delete_current_info',
    'get_prompt_view_games',
    'get_prompt_view_rating',
    'get_prompt_add_user',
    'get_prompt_register_participant',
    'get_prompt_update_nickname',
    'get_prompt_view_nickname',
    'get_prompt_add_answer',
    'get_prompt_view_answer',
    'get_prompt_update_answer',
    'get_prompt_view_user_tournaments',
]