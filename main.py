from loaders import bot, user
from telebot.types import CallbackQuery, Message
from handlers import HighpriceHandler, PriceHandler


handler = None


@bot.message_handler(content_types=["text"])
def get_text_message(message: Message):
    global handler

    if message.text and (
        message.text.lower() == "привет" or message.text == "/hello-world"
    ):
        bot.send_message(message.from_user.id, "Привет, чем я могу помочь?")
    elif message.text == "/lowprice":
        handler = PriceHandler()
        handler.initialize_handler(message)
    elif message.text == "/highprice":
        handler = HighpriceHandler()
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
