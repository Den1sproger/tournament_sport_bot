from .db_work import Database



TOURNAMENT_TYPES = ['SLOW', 'STANDART', 'FAST']
PROMPT_VIEW_USERS = "SELECT chat_id, nickname FROM users;"


def get_prompt_view_games(tourn_type: str) -> str:
    return "SELECT game_key, sport, begin_time, first_team, first_coeff, second_team," \
        f"second_coeff, draw_coeff, url FROM games WHERE game_status=1 AND tourn_type='{tourn_type}';"


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


def get_prompt_view_user_tournaments(chat_id: str) -> str:
    return f"SELECT tournament FROM users_tournaments WHERE chat_id='{chat_id}';"


def get_prompt_add_user_tournament(chat_id: str,
                                   tournament: str) -> str:
    return f"INSERT INTO users_tournaments (chat_id, tournament) VALUES ('{chat_id}', '{tournament}');"


def get_prompt_delete_user_tournaments(chat_id: str) -> str:
    return f"DELETE FROM users_tournaments WHERE chat_id='{chat_id}';"


__all__ = [
    'Database',
    'TOURNAMENT_TYPES',
    'PROMPT_VIEW_USERS',
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
    'get_prompt_add_user_tournament',
    'get_prompt_delete_user_tournaments'
]