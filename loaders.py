import telebot

from os import getenv
from dotenv import load_dotenv
from user import User

load_dotenv()

TOKEN = getenv("BOT_TOKEN")

bot = telebot.TeleBot(TOKEN)
user = User()
