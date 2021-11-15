import json

from api import Api
from datetime import datetime
from loaders import bot, cur
from requests.exceptions import RequestException
from typing import Any, Dict, List, Union
from user import User
from telebot.types import (
    InputMediaPhoto,
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from handlers.abs_handler import AbsHandler
from hotel import Hotel


class Lowprice(AbsHandler):
    """Class for handle /lowprice request"""

    def __init__(self, user: User) -> None:
        self.__api = Api()
        self._user = user
        self._user.sort_order = "PRICE"
        self._command = "/lowprice"

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
        """Find similar cities with user entered city

        Args:
            source (str): user entered destination

        Returns:
            List[Dict[str, str]]: List of destination's data,
                similar to source destination
        """
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
        """Send available destinations to user with keyboard

        Args:
            message (Message): Message object sent from bot
        """
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
        """Get and parse user int/float value until it will correct

        Args:
            message (Message): Message object sent from bot
            method ([type], optional): [description]. Defaults to int.
                Available int or float,
                method, using to parse string in int or float.
            boundary (Union[int, None], optional): [description].
                Defaults to None. Max value for user input

        Returns:
            int: float or int user input
        """
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
        """Get hotels count from user

        Args:
            message (Message): Message object sent from bot
        """

        self._user.hotels_count = self._get_int_float_value(
            message, boundary=self._user.MAX_HOTELS_COUNT
        )

        if self._user.hotels_count == 0:
            bot.register_next_step_handler(message, self.__get_hotels_count)

            return

        bot.send_message(
            message.from_user.id,
            "Нужно ли показывать фотографии отелей?",
        )
        bot.register_next_step_handler(message, self.__get_photo_access)

    def __get_photo_access(self, message: Message) -> None:
        """Should bot show photo or not

        Args:
            message (Message): Message object sent from bot
        """
        if message.text:
            if message.text.lower() == "да":
                self._user.should_show_photo = True
                bot.send_message(
                    message.from_user.id, "Сколько фотографий показывать?"
                )
                bot.register_next_step_handler(message, self.__get_photo_count)
            elif message.text.lower() == "нет":
                self._user.should_show_photo = False
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
        """Get hotels photo count

        Args:
            message (Message): Message object sent from bot
        """
        self._user.photo_count = self._get_int_float_value(
            message, boundary=self._user.MAX_PHOTO_COUNT
        )

        if self._user.photo_count == 0:
            bot.register_next_step_handler(message, self.__get_photo_count)

            return

        self._start_collect_data(message)

    def _start_collect_data(self, message: Message) -> None:
        """Start collect data from api

        Args:
            message (Message): Message object sent from bot
        """
        bot.send_message(message.from_user.id, "Ожидайте, собираю информацию")

        try:
            self._collect_data(message)
        except RequestException:
            bot.send_message(
                message.from_user.id, "Что-то пошло не так, попробуйте заново"
            )

    def _collect_data(self, message: Message) -> None:
        """Get hotels from api and added request info into db

        Args:
            message (Message): Message object sent from bot
        """

        hotels: List[Hotel] = self._get_hotel_suggestions(
            self._user.hotels_count
        )
        now = datetime.now()
        datetime_string = now.strftime("%d/%m/%Y %H:%M:%S")

        if cur:
            cur.execute(
                f"""INSERT INTO requests
                (user_id, command, date_time)
                VALUES(
                    {message.from_user.id},
                    '{self._command}',
                    '{datetime_string}'
                )"""
            )

            cur.execute(
                f"""SELECT id FROM requests
                WHERE user_id == {message.from_user.id}
                AND date_time == '{datetime_string}'"""
            )

            request_id = cur.fetchone()[0]

            self._send_info_to_user(message, hotels, request_id)

    def _send_info_to_user(
        self, message: Message, hotels: List[Hotel], request_id: int
    ) -> None:
        """Send info to user

        Args:
            message (Message): Message object sent from bot
            hotels (List[Hotel]): found hotels
            request_id (int): request id from db
        """
        if not len(hotels):
            bot.send_message(
                message.from_user.id,
                "В вашем городе нет подходящих отелей",
            )

            return

        for hotel in hotels:
            photos: List[str] = []

            if self._user.should_show_photo is True:
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
                images_str = json.dumps(photos)

                if cur:
                    cur.execute(
                        f"""INSERT INTO hotels (request_id, description, photos)
                        VALUES({request_id}, '{text}', '{images_str}')"""
                    )

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
                if cur:
                    cur.execute(
                        f"""INSERT INTO hotels (request_id, description)
                        VALUES({request_id}, '{text}')"""
                    )

                bot.send_message(message.from_user.id, text)

    def __get_hotel_photos(self, id: str) -> List[str]:
        """Get hotel photos

        Args:
            id (str): hotel id

        Returns:
            List[str]: list of images urls
        """
        raw_data = self.__api.send_request(
            "/properties/get-hotel-photos", {"id": id}
        )
        photos = raw_data.get("hotelImages", [])

        if not len(photos):
            return photos

        chunk_length: int = (
            len(photos)
            if self._user.photo_count >= len(photos)
            else self._user.photo_count
        )

        return list(
            map(
                lambda photo: photo["baseUrl"].replace("{size}", "z"),
                photos[:chunk_length],
            )
        )

    def _get_hotel_suggestions(
        self, page_size: Union[int, None] = None
    ) -> List[Hotel]:
        """Get hotels suggestions from api

        Args:
            page_size (Union[int, None], optional): [description].
                Defaults to None.
                Count of return hotels

        Returns:
            List[Hotel]: list of found hotels
        """
        querystring = {
            "destinationId": self._user.city,
            "pageNumber": "1",
            "adults1": "1",
            "locale": "ru_RU",
            "sortOrder": self._user.sort_order,
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
        """Extract needed info about hotel from api response

        Args:
            hotel (Dict[str, Any]): Info about hotel from api

        Returns:
            Hotel: needed info about hotel
        """
        distance_list: List[str] = [
            info["distance"]
            for info in hotel["landmarks"]
            if info["label"] == "Центр города"
        ]

        distance: str = "0"

        if len(distance_list):
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
