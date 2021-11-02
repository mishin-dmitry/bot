from abc import ABC, abstractmethod
from api import Api
from requests.exceptions import RequestException
from typing import Any, Dict, List, Union
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


class AbsHandler(ABC):
    @abstractmethod
    def initialize_handler(self, message: Message) -> None:
        raise NotImplementedError("method should be implemented")

    @abstractmethod
    def continue_chain(self, call: CallbackQuery) -> None:
        raise NotImplementedError("method should be implemented")


class Handler(AbsHandler):
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

    def _get_int_float_value(
        self, message: Message, method=int, boundary: Union[int, None] = None
    ) -> int:
        value = 0

        try:
            value = method((message.text or "").replace(",", "."))

            if value <= 0:
                bot.send_message(
                    message.from_user.id,
                    "Значение должно быть больше 0",
                )

                return 0

            if boundary is not None and value > boundary:
                bot.send_message(
                    message.from_user.id,
                    f"Максимальное количеств - {boundary}",
                )

                return 0

        except ValueError:
            bot.send_message(message.from_user.id, "Введите значение цифрами")

            return 0

        return value

    def __get_hotels_count(self, message: Message) -> None:
        user.hotels_count = self._get_int_float_value(
            message, boundary=user.MAX_HOTELS_COUNT
        )

        if user.hotels_count == 0:
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
                self._start_collect_data(message)

            else:
                bot.send_message(
                    message.from_user.id,
                    "Что-то не понятно. Напишите да или нет",
                )
                bot.register_next_step_handler(
                    message, self.__get_photo_access
                )

    def __get_photo_count(self, message: Message) -> None:
        user.photo_count = self._get_int_float_value(
            message, boundary=user.MAX_PHOTO_COUNT
        )

        if user.photo_count == 0:
            bot.register_next_step_handler(message, self.__get_photo_count)

            return

        self._start_collect_data(message)

    def _start_collect_data(self, message: Message) -> None:
        bot.send_message(message.from_user.id, "Ожидайте, собираю информацию")

        try:
            self._collect_data(message)
        except RequestException:
            bot.send_message(
                message.from_user.id, "Что-то пошло не так, попробуйте заново"
            )

    def _collect_data(self, message: Message) -> None:
        hotels: List[Hotel] = self._get_hotel_suggestions()

        self._send_info_to_user(message, hotels)

    def _send_info_to_user(
        self, message: Message, hotels: List[Hotel]
    ) -> None:
        if not len(hotels):
            bot.send_message(
                message.from_user.id,
                "В вашем городе нет подходящих отелей",
            )

            return

        for hotel in hotels:
            photos: List[str] = []

            if user.should_show_photo is True:
                photos = self.__get_hotel_photos(hotel.id)

            text: str = hotel.name

            if hotel.address:
                text += f"\n{hotel.address}"

            if hotel.distance != 0:
                text += f"\nРасположение от центра - {hotel.distance}км."

            text += (
                f"\nСтоимость - {hotel.str_price.replace('RUB', 'рублей')}."
            )

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

    def _get_hotel_suggestions(
        self, page_size: Union[int, None] = user.hotels_count
    ) -> List[Hotel]:
        querystring = {
            "destinationId": user.city,
            "pageNumber": "1",
            "adults1": "1",
            "locale": "ru_RU",
            "sortOrder": user.sort_order,
            "currency": "RUB",
        }

        if page_size is not None:
            querystring["pageSize"] = str(page_size)

        response = self.__api.send_request("/properties/list", querystring)

        if response["searchResults"]["totalCount"] == 0:
            return []

        result = response["searchResults"]["results"]

        return list(map(self.__extract_info_about_hotel, result))

    def __extract_info_about_hotel(self, hotel: Dict[str, Any]) -> Hotel:
        distance_list: List[str] = [
            info["distance"]
            for info in hotel["landmarks"]
            if info["label"] == "Центр города"
        ]

        distance: str = "0"

        if len(distance):
            distance = distance_list[0]

        price_str: str = (
            hotel.get("ratePlan", {}).get("price", {}).get("current", "")
        )

        price: float = (
            hotel.get("ratePlan", {}).get("price", {}).get("exactCurrent", 0)
        )

        return Hotel(
            hotel["id"],
            hotel["address"].get("streetAddress", ""),
            float(distance.replace("км", "").replace(",", ".")),
            price_str,
            price,
            hotel["name"],
        )


class HighpriceHandler(Handler):
    def __init__(self) -> None:
        super().__init__()

        user.sort_order = "PRICE_HIGHEST_FIRST"


class BestdealHandler(Handler):
    def __init__(self) -> None:
        super().__init__()

        user.sort_order = "PRICE"

    def _start_collect_data(self, message: Message) -> None:
        bot.send_message(
            message.from_user.id,
            "Введите цену в рублях, от которой начинаем смотреть",
        )
        bot.register_next_step_handler(message, self.__get_min_price)

    def __get_min_price(self, message: Message) -> None:
        min: int = self._get_int_float_value(message, float)

        if min == 0:
            bot.register_next_step_handler(message, self.__get_min_price)

            return

        user.add_price(min)

        bot.send_message(
            message.from_user.id,
            "Введите цену до которой смотрим",
        )
        bot.register_next_step_handler(message, self.__get_max_price)

    def __get_max_price(self, message: Message) -> None:
        max: int = self._get_int_float_value(message, float)

        if max == 0:
            bot.register_next_step_handler(message, self.__get_max_price)

            return

        if max <= user.price_range[0]:
            bot.send_message(
                message.from_user.id,
                "Верхний придел должен быть больше нижнего",
            )
            bot.register_next_step_handler(message, self.__get_max_price)

            return

        user.add_price(max)

        bot.send_message(
            message.from_user.id,
            "Введите минимальное расстояние от центра в км",
        )
        bot.register_next_step_handler(message, self.__get_min_distance)

    def __get_min_distance(self, message: Message) -> None:
        min: int = self._get_int_float_value(message, float)

        if min == 0:
            bot.register_next_step_handler(message, self.__get_min_distance)

            return

        user.add_distance(min)

        bot.send_message(
            message.from_user.id,
            "Введите максимальное расстояние от центра в км",
        )
        bot.register_next_step_handler(message, self.__get_max_distance)

    def __get_max_distance(self, message: Message) -> None:
        max: int = self._get_int_float_value(message, float)

        if max == 0:
            bot.register_next_step_handler(message, self.__get_max_distance)

            return

        if max <= user.distance_range[0]:
            bot.send_message(
                message.from_user.id,
                "Верхний придел должен быть больше нижнего",
            )
            bot.register_next_step_handler(message, self.__get_max_distance)

            return

        user.add_distance(max)

        bot.send_message(message.from_user.id, "Ожидайте собираю информацию")

        self._collect_data(message)

    def __find_appropriate_hotels(self, hotels: List[Hotel]) -> List[Hotel]:
        result = []

        price_min, price_max = user.price_range
        distance_min, distance_max = user.distance_range

        print(
            "price_min",
            price_min,
            "price_max",
            price_max,
            "distance_min",
            distance_min,
            "distance_max",
            distance_max,
        )

        for hotel in hotels:
            print("hotel.price", hotel.price)
            print("hotel.distance", hotel.distance)
            if hotel.price > price_max or hotel.price < price_min:
                continue

            if hotel.distance > distance_max or hotel.distance < distance_min:
                continue

            price_ration = 100 * (hotel.price - price_min) / hotel.price
            print("price_ration", price_ration)
            distance_ratio = (
                100 * (hotel.distance - distance_min) / hotel.distance
            )
            print("distance_ratio", distance_ratio)

            ratio = price_ration + distance_ratio

            if len(result) < user.hotels_count:
                result.append({"hotel": hotel, "ratio": ratio})
            else:
                for i, i_hotel in enumerate(result):
                    if i_hotel["ratio"] > ratio:
                        result[i] = {"hotel": hotel, "ratio": ratio}

                        break

        return list(map(lambda x: x["hotel"], result))

    def _collect_data(self, message: Message) -> None:
        hotels = self._get_hotel_suggestions(None)
        hotels = self.__find_appropriate_hotels(hotels)

        self._send_info_to_user(message, hotels)
