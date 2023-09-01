from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_scores_by_coeff(coeff: str) -> int:
    # get the quantity of scores by coefficient
    if not coeff:
        return 0
    coefficient = float(coeff.replace(',', '.'))
    if coefficient < 1.26:
        return 3
    
    count = 126
    switch = 2
    score = 5

    while score < 30:
        interval = [i / 100 for i in range(count, count + 50)]
        if coefficient in interval:
            return score
        count += 50

        if switch == 1:
            score += 2
            switch = 2
        else:
            score += 1
            switch = 1
    else:
        if coefficient >= 9.76:
            return 30


def get_question_ikb(quantity: int,
                     current_question_index: int,
                     coeffs: list[str],
                     answer: int = None) -> InlineKeyboardMarkup:
    # keyboard for the one question
    team_1 = f'П1-{get_scores_by_coeff(coeffs[0])}'
    team_2 = f'П2-{get_scores_by_coeff(coeffs[1])}'
    draw = f'X-{get_scores_by_coeff(coeffs[-1])}'

    if not answer: pass
    elif answer == 1: team_1 = f"👉{team_1}👈"
    elif answer == 2: team_2 = f"👉{team_2}👈"
    else: draw = f"👉{draw}👈"

    if len(coeffs) == 3:
        inline_keyboard = [
            [
                InlineKeyboardButton(team_1, callback_data='first_team'),
                InlineKeyboardButton(draw, callback_data='draw'),
                InlineKeyboardButton(team_2, callback_data='second_team')
            ]
        ]
    else:
        inline_keyboard = [
            [
                InlineKeyboardButton(team_1, callback_data='first_team'),
                InlineKeyboardButton(team_2, callback_data='second_team')
            ]
        ]
    inline_keyboard.append([
            InlineKeyboardButton('<', callback_data='previous_question'),
            InlineKeyboardButton(f'{current_question_index + 1}/{quantity}', callback_data='0'),
            InlineKeyboardButton('>', callback_data='next_question')
    ])
    inline_keyboard.append(
        [InlineKeyboardButton('Назад', callback_data='back_to_my_tournaments')]
    )

    ikb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return ikb



def get_tournaments_kb(*tournaments) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for item in tournaments:
        inline_keyboard.append(
            [
                InlineKeyboardButton(f'Турнир {item}', callback_data=f'tourn_{item}'),
                InlineKeyboardButton(f'Таблица лидеров {item}', callback_data=f'leader_{item}')
            ]
        )

    ikb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return ikb
