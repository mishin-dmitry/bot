from typing import Union
from loaders import bot
from telebot.types import CallbackQuery, Message
from handlers.bestdeal import Bestdeal
from handlers.highprice import Highprice
from handlers.lowprice import Lowprice
from handlers.history import History
from user import User
from users import Users


handler: Union[Lowprice, Highprice, Bestdeal, History, None] = None


@bot.message_handler(content_types=["text"])
def get_text_message(message: Message) -> None:
    """Handle messages from user

    Args:
        message (Message): Message object sent from bot
    """

    user: Union[None, User] = None

    if Users.has_user(message.from_user.id) is False:
        user = User()
        Users.add_user(message.from_user.id, user)

    if message.text and (
        message.text.lower() in ["привет", "/start", "/hello-world"]
    ):
        bot.send_message(message.from_user.id, "Привет, чем я могу помочь?")
    elif message.text in [
        "/lowprice",
        "/highprice",
        "/bestdeal",
        "/history",
        "/help",
    ]:
        user = Users.get_user(message.from_user.id)
        user.clear_data()

        global handler

        if message.text == "/lowprice":
            handler = Lowprice(user)
        elif message.text == "/highprice":
            handler = Highprice(user)
        elif message.text == "/history":
            handler = History()
        elif message.text == "/bestdeal":
            handler = Bestdeal(user)
        else:
            bot.send_message(
                message.from_user.id,
                "1. /lowprice - поиск список отелей по возрастанию цены\n2."
                " /highprice - поиск  отелей по убыванию цены\n3. /bestdeal -"
                " поиск отелей по соотношению цены и удаленности от центра\n4."
                " /history - выведет историю запросов",
            )
            return

        handler.initialize_handler(message)
    else:
        bot.send_message(
            message.from_user.id, "Я тебя не понимаю. Напиши /help."
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: CallbackQuery) -> None:
    """Handle user keyboard value

    Args:
        call (CallbackQuery): CallbackQuery send from bot
    """

    user = Users.get_user(call.from_user.id)
    user.city = call.data

    if handler is not None:
        handler.continue_chain(call)


if __name__ == "__main__":
    bot.infinity_polling()
