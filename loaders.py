import sqlite3 as sq
import telebot

from typing import Union
from os import getenv
from dotenv import load_dotenv


load_dotenv()

TOKEN = getenv("BOT_TOKEN")
bot: telebot.TeleBot = telebot.TeleBot(TOKEN)

cur: Union[None, sq.Cursor] = None

with sq.connect(
    "hotels.db", check_same_thread=False, isolation_level=None
) as con:
    cur = con.cursor()

    # cur.execute(
    #     """CREATE TABLE IF NOT EXISTS users
    #     (user_id INTEGER, UNIQUE(user_id))"""
    # )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS requests(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            command TEXT NOT NULL,
            date_time TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )"""
    )

    cur.execute(
        """CREATE TABLE IF NOT EXISTS hotels(
            request_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            photos TEXT,
            FOREIGN KEY (request_id) REFERENCES requests (id)
        )"""
    )
