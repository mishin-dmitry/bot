from typing import Union
from loaders import bot, user
from telebot.types import CallbackQuery, Message
from handlers import BestdealHandler, HighpriceHandler, Handler


handler: Union[Handler, HighpriceHandler, BestdealHandler, None] = None


@bot.message_handler(content_types=["text"])
def get_text_message(message: Message):
    if message.text and (
        message.text.lower() == "привет" or message.text == "/hello-world"
    ):
        bot.send_message(message.from_user.id, "Привет, чем я могу помочь?")
    if message.text in ["/lowprice", "/highprice", "/bestdeal"]:
        user.clear_data()

        global handler

        if message.text == "/lowprice":
            handler = Handler()
        elif message.text == "/highprice":
            handler = HighpriceHandler()
        elif message.text == "/bestdeal":
            handler = BestdealHandler()

        handler.initialize_handler(message)
    else:
        bot.send_message(
            message.from_user.id, "Я тебя не понимаю. Напиши /help."
        )


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: CallbackQuery):
    user.city = call.data

    if handler is not None:
        handler.continue_chain(call)


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
