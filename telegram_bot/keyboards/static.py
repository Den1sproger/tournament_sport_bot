from aiogram.types import (ReplyKeyboardMarkup,
                           KeyboardButton)


main_kb = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[
        [KeyboardButton('🏀🏐Текущие турниры'), KeyboardButton('👨‍💼Ввести ник')],
        [KeyboardButton('⛔️Стоп'), KeyboardButton('Мои турниры')],
        [KeyboardButton('🆘Помощь')]
    ]
)
