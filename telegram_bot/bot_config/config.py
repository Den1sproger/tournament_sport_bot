import os

from aiogram.types import BotCommand
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

TOKEN = os.getenv('TOURNAMENT_TOKEN')
ADMIN = int(os.getenv('ADMIN'))
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


default_commands = [
    BotCommand('start', 'Запустить бота'),
    BotCommand('help', 'Помощь'),
    BotCommand('nickname', 'Ввести ник'),
    BotCommand('current_tournaments', 'Текущие турниры')
]
