from datetime import datetime
from loaders import bot, cur
from typing import List
from telebot.types import Message
from user import User
from handlers.lowprice import Lowprice
from hotel import Hotel


class Bestdeal(Lowprice):
    """Class to Handle /bestdeal command

    Args:
        Handler ([type]): Class which handle /lowprice command
    """

    def __init__(self, user: User) -> None:
        super().__init__(user)

        self._user.sort_order = "PRICE"
        self._command = "/bestdeal"

    def _start_collect_data(self, message: Message) -> None:
        bot.send_message(
            message.from_user.id,
            "Введите цену в рублях, от которой начинаем смотреть",
        )
        bot.register_next_step_handler(message, self.__get_min_price)

    def __get_min_price(self, message: Message) -> None:
        """Get min price for hotel suggestions

        Args:
            message (Message): Message object sent from bot
        """
        min: int = self._get_int_float_value(message, float)

        if min == 0:
            bot.register_next_step_handler(message, self.__get_min_price)

            return

        self._user.add_price(min)

        bot.send_message(
            message.from_user.id,
            "Введите цену до которой смотрим",
        )
        bot.register_next_step_handler(message, self.__get_max_price)

    def __get_max_price(self, message: Message) -> None:
        """Get max price for hotel suggestions

        Args:
            message (Message): Message object sent from bot
        """
        max: int = self._get_int_float_value(message, float)

        if max == 0:
            bot.register_next_step_handler(message, self.__get_max_price)

            return

        if max <= self._user.price_range[0]:
            bot.send_message(
                message.from_user.id,
                "Верхний придел должен быть больше нижнего",
            )
            bot.register_next_step_handler(message, self.__get_max_price)

            return

        self._user.add_price(max)

        bot.send_message(
            message.from_user.id,
            "Введите минимальное расстояние от центра в км",
        )
        bot.register_next_step_handler(message, self.__get_min_distance)

    def __get_min_distance(self, message: Message) -> None:
        """Get min distance for hotel suggestions

        Args:
            message (Message): Message object sent from bot
        """
        min: int = self._get_int_float_value(message, float)

        if min == 0:
            bot.register_next_step_handler(message, self.__get_min_distance)

            return

        self._user.add_distance(min)

        bot.send_message(
            message.from_user.id,
            "Введите максимальное расстояние от центра в км",
        )
        bot.register_next_step_handler(message, self.__get_max_distance)

    def __get_max_distance(self, message: Message) -> None:
        """Get max price for hotel suggestions

        Args:
            message (Message): Message object sent from bot
        """
        max: int = self._get_int_float_value(message, float)

        if max == 0:
            bot.register_next_step_handler(message, self.__get_max_distance)

            return

        if max <= self._user.distance_range[0]:
            bot.send_message(
                message.from_user.id,
                "Верхний придел должен быть больше нижнего",
            )
            bot.register_next_step_handler(message, self.__get_max_distance)

            return

        self._user.add_distance(max)

        bot.send_message(message.from_user.id, "Ожидайте собираю информацию")

        self._collect_data(message)

    def __find_appropriate_hotels(self, hotels: List[Hotel]) -> List[Hotel]:
        """Find hotels appropriate user conditions

        Args:
            hotels (List[Hotel]): All hotels available in user destination

        Returns:
            List[Hotel]: List of appropriate hotels
        """
        result = []

        price_min, price_max = self._user.price_range
        distance_min, distance_max = self._user.distance_range

        for hotel in hotels:
            if hotel.price > price_max or hotel.price < price_min:
                continue

            if hotel.distance > distance_max or hotel.distance < distance_min:
                continue

            price_ration = 100 * (hotel.price - price_min) / hotel.price
            distance_ratio = (
                100 * (hotel.distance - distance_min) / hotel.distance
            )

            ratio = price_ration + distance_ratio

            if len(result) < self._user.hotels_count:
                result.append({"hotel": hotel, "ratio": ratio})
            else:
                for i, i_hotel in enumerate(result):
                    if i_hotel["ratio"] > ratio:
                        result[i] = {"hotel": hotel, "ratio": ratio}

                        break

        return list(map(lambda x: x["hotel"], result))

    def _collect_data(self, message: Message) -> None:
        hotels = self._get_hotel_suggestions()
        hotels = self.__find_appropriate_hotels(hotels)

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
