from typing import List


class User:
    MAX_HOTELS_COUNT: int = 5
    MAX_PHOTO_COUNT: int = 5

    def __init__(self) -> None:
        self.__city: str = ""
        self.__hotels_count: int = 0
        self.__should_show_photo: bool = False
        self.__photo_count: int = 0
        self.__sort_order: str = "PRICE"
        self.__price_range: List[int] = []
        self.__distance_range: List[int] = []

    @property
    def city(self) -> str:
        return self.__city

    @city.setter
    def city(self, value: str) -> None:
        self.__city = value

    @property
    def hotels_count(self) -> int:
        return self.__hotels_count

    @hotels_count.setter
    def hotels_count(self, value: int) -> None:
        self.__hotels_count = value

    @property
    def should_show_photo(self) -> bool:
        return self.__should_show_photo

    @should_show_photo.setter
    def should_show_photo(self, value: bool) -> None:
        self.__should_show_photo = value

    @property
    def photo_count(self) -> int:
        return self.__photo_count

    @photo_count.setter
    def photo_count(self, value: int) -> None:
        self.__photo_count = value

    @property
    def sort_order(self) -> str:
        return self.__sort_order

    @sort_order.setter
    def sort_order(self, value: str) -> None:
        self.__sort_order = value

    @property
    def price_range(self) -> List[int]:
        return self.__price_range

    def add_price(self, value: int) -> None:
        self.__price_range.append(value)

    @property
    def distance_range(self) -> List[int]:
        return self.__distance_range

    def add_distance(self, value: int) -> None:
        self.__distance_range.append(value)

    def clear_data(self) -> None:
        self.__city: str = ""
        self.__hotels_count: int = 0
        self.__should_show_photo: bool = False
        self.__photo_count: int = 0
        self.__sort_order: str = "PRICE"
        self.__price_range: List[int] = []
        self.__distance_range: List[int] = []
