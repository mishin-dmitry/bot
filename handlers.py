from api import Api
from requests.exceptions import RequestException
from typing import Any, Dict, List
from loaders import bot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
    Message,
)
from loaders import user
from hotel import Hotel


class PriceHandler:
    MAX_HOTELS_COUNT: int = 5
    MAX_PHOTO_COUNT: int = 5

    def __init__(self) -> None:
        self.__api = Api()
        user.sort_order = "PRICE"

    def initialize_handler(self, message: Message) -> None:
        bot.send_message(
            message.from_user.id, "Введите город в котором смотрим отели"
        )
        bot.register_next_step_handler(message, self.__get_city)

    def continue_chain(self, call: CallbackQuery) -> None:
        bot.send_message(
            call.message.chat.id,
            "Введите количество отелей, которые необходимо вывести в"
            " результате",
        )
        bot.register_next_step_handler(call.message, self.__get_hotels_count)

    def __get_city_suggestion(self, source: str) -> List[Dict[str, str]]:
        querystring = {"query": source, "locale": "ru_RU"}

        response = self.__api.send_request("/locations/search", querystring)

        if response["moresuggestions"] == 0:
            return []

        city_group: Dict[str, Any] = response.get("suggestions", [])[0]
        entities: List[Dict[str, Any]] = city_group.get("entities", [])

        return list(
            map(
                lambda x: {
                    "id": x["destinationId"],
                    "name": x["caption"]
                    .replace("<span class='highlighted'>", "")
                    .replace("</span>", ""),
                },
                entities,
            )
        )

    def __get_city(self, message: Message) -> None:
        suggestions = self.__get_city_suggestion(message.text or "")
        keyboard = InlineKeyboardMarkup()

        for suggestion in suggestions:
            key = InlineKeyboardButton(
                text=suggestion["name"], callback_data=suggestion["id"]
            )
            keyboard.add(key)

        question = "Уточните адрес:"

        bot.send_message(
            message.from_user.id, text=question, reply_markup=keyboard
        )

    def __get_hotels_count(self, message: Message) -> None:
        try:
            user.hotels_count = int(message.text or "")

            if user.hotels_count > self.MAX_HOTELS_COUNT:
                bot.send_message(
                    message.from_user.id,
                    f"Максимальное количеств отелей - {self.MAX_HOTELS_COUNT}",
                )
                bot.register_next_step_handler(
                    message, self.__get_hotels_count
                )

                return

        except ValueError:
            bot.send_message(message.from_user.id, "Введите значение цифрами")
            bot.register_next_step_handler(message, self.__get_hotels_count)

            return

        bot.send_message(
            message.from_user.id,
            "Нужно ли показывать фотографии отелей?",
        )
        bot.register_next_step_handler(message, self.__get_photo_access)

    def __get_photo_access(self, message: Message) -> None:
        if message.text:
            if message.text.lower() == "да":
                user.should_show_photo = True
                bot.send_message(
                    message.from_user.id, "Сколько фотографий показывать?"
                )
                bot.register_next_step_handler(message, self.__get_photo_count)
            elif message.text.lower() == "нет":
                user.should_show_photo = False
                bot.send_message(
                    message.from_user.id, "Ожидайте, собираю информацию"
                )
                self.__collect_data(message)

            else:
                bot.send_message(
                    message.from_user.id,
                    "Что-то не понятно. Напишите да или нет",
                )
                bot.register_next_step_handler(
                    message, self.__get_photo_access
                )

    def __get_photo_count(self, message: Message) -> None:
        try:
            user.photo_count = int(message.text or "")

            if user.photo_count > self.MAX_PHOTO_COUNT:
                bot.send_message(
                    message.from_user.id,
                    "Максимальное количеств фотографий -"
                    f" {self.MAX_PHOTO_COUNT}",
                )
                bot.register_next_step_handler(message, self.__get_photo_count)

                return
        except Exception:
            bot.send_message(message.from_user.id, "Введите значение цифрами")
            bot.register_next_step_handler(message, self.__get_photo_count)

            return

        bot.send_message(message.from_user.id, "Ожидайте, собираю информацию")

        try:
            self.__collect_data(message)
        except RequestException:
            bot.send_message(
                message.from_user.id, "Что-то пошло не так, попробуйте заново"
            )

    def __collect_data(self, message: Message) -> None:
        hotels: List[Hotel] = self.__get_hotel_suggestions()

        self.__send_info_to_user(message, hotels)

    def __send_info_to_user(
        self, message: Message, hotels: List[Hotel]
    ) -> None:
        if not len(hotels):
            bot.send_message(
                message.from_user.id,
                "В вашем городе нет отелей",
            )

            return

        for hotel in hotels:
            photos: List[str] = []

            if user.should_show_photo is True:
                photos = self.__get_hotel_photos(hotel.id)

            text: str = hotel.name

            if hotel.address:
                text += f"\n{hotel.address}"

            text += f"\nРасположение от центра - {hotel.distance}."
            text += f"\nСтоимость - {hotel.price.replace('RUB', 'рублей')}."

            if len(photos):
                bot.send_media_group(
                    message.from_user.id,
                    [
                        InputMediaPhoto(photo, caption=text)
                        if i == 0
                        else InputMediaPhoto(photo)
                        for i, photo in enumerate(photos)
                    ],
                )
            else:
                bot.send_message(message.from_user.id, text)

    def __get_hotel_photos(self, id: str) -> List[str]:
        raw_data = self.__api.send_request(
            "/properties/get-hotel-photos", {"id": id}
        )
        photos = raw_data.get("hotelImages", [])

        if not len(photos):
            return photos

        chunk_length: int = (
            len(photos)
            if user.photo_count >= len(photos)
            else user.photo_count
        )

        return list(
            map(
                lambda photo: photo["baseUrl"].replace("{size}", "z"),
                photos[:chunk_length],
            )
        )

    def __get_hotel_suggestions(self) -> List[Hotel]:
        querystring = {
            "destinationId": user.city,
            "pageNumber": "1",
            "pageSize": user.hotels_count,
            "adults1": "1",
            "locale": "ru_RU",
            "sortOrder": user.sort_order,
            "currency": "RUB",
        }

        response = self.__api.send_request("/properties/list", querystring)

        if response["searchResults"]["totalCount"] == 0:
            return []

        result = response["searchResults"]["results"]

        return list(map(self.__extract_info_about_hotel, result))

    def __extract_info_about_hotel(self, hotel: Dict[str, Any]) -> Hotel:
        distance: str = [
            info["distance"]
            for info in hotel["landmarks"]
            if info["label"] == "Центр города"
        ][0]

        return Hotel(
            hotel["id"],
            hotel["address"].get("streetAddress", ""),
            distance,
            hotel["ratePlan"]["price"]["current"],
            hotel["name"],
        )


class HighpriceHandler(PriceHandler):
    def __init__(self) -> None:
        super().__init__()
        user.sort_order = "PRICE_HIGHEST_FIRST"
