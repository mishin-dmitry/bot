import telebot

from utils.constants import TOKEN


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(content_types=["text"])
def get_text_message(message):
    if message.text.lower() == "привет" or message.text == "/hello-world":
        bot.send_message(message.from_user.id, "Привет, чем я могу помочь?")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
