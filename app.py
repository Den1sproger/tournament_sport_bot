import logging

from aiogram import executor
from telegram_bot import dp
from telegram_bot.handlers.start import *
from telegram_bot.handlers.inline_menu import *
from telegram_bot.handlers.default_commands import *

# LOG_FILENAME = "/home/tournament/py_log.log"
# logging.basicConfig(level=logging.INFO, filename=LOG_FILENAME, filemode="w")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)