from typing import Union
from loaders import bot
from telebot.types import CallbackQuery, Message
from handlers import BestdealHandler, HighpriceHandler, Handler, History
from user import User
from users import Users


handler: Union[
    Handler, HighpriceHandler, BestdealHandler, History, None
] = None


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
    elif message.text in ["/lowprice", "/highprice", "/bestdeal", "/history"]:
        user = Users.get_user(message.from_user.id)
        user.clear_data()

        global handler

        if message.text == "/lowprice":
            handler = Handler(user)
        elif message.text == "/highprice":
            handler = HighpriceHandler(user)
        elif message.text == "/history":
            handler = History()
        else:
            handler = BestdealHandler(user)

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
