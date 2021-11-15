import json

from handlers.abs_handler import AbsHandler
from typing import Any, List, Tuple
from loaders import bot, cur
from telebot.types import InputMediaPhoto, Message


class History(AbsHandler):
    """Class handle /history command

    Args:
        AbsHandler ([type]): Abstract handler
    """

    def __get_hotel_info_by_request_id(self, id: int) -> List[Tuple]:
        """Return hotel description and photos

        Args:
            id (int): request id from db

        Returns:
            List[Tuple]: List of hotels description and photos
        """
        if cur:
            cur.execute(
                f"""SELECT description, photos FROM hotels
                    WHERE request_id = {id}
                """
            )

            return cur.fetchall()

        return []

    def initialize_handler(self, message: Message) -> None:
        if cur:
            cur.execute(
                f"""SELECT id, command, date_time FROM requests
                    WHERE user_id = {message.from_user.id}
                """
            )

            result = cur.fetchall()

            if not len(result):
                bot.send_message(
                    message.from_user.id, "История запросов пуста"
                )
            else:
                for i, item in enumerate(result):
                    rest_data = self.__get_hotel_info_by_request_id(item[0])
                    data = list(item)
                    data.append(rest_data)
                    result[i] = data

                self.__send_data_to_user(result, message)

    def __send_data_to_user(self, data: List[Any], message: Message) -> None:
        """Send history info to user

        Args:
            data (List[Any]): List of histories
            message (Message): Message object sent from bot
        """
        for item in data:
            _, command, date_time, hotels = item

            command_and_date = (
                f"""Команда запроса - {command}.\nДата запроса - {date_time}"""
            )

            bot.send_message(message.from_user.id, command_and_date)

            if not len(hotels):
                bot.send_message(
                    message.from_user.id, "Подходящих отелей не было найдено"
                )

            for hotel in hotels:
                description, str_photos = hotel

                if str_photos is None:
                    bot.send_message(message.from_user.id, description)
                else:
                    photos = json.loads(str_photos)

                    bot.send_media_group(
                        message.from_user.id,
                        [
                            InputMediaPhoto(photo, caption=description)
                            if i == 0
                            else InputMediaPhoto(photo)
                            for i, photo in enumerate(photos)
                        ],
                    )
