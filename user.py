from typing import List


class User:
    """Info about user answers from chat"""

    MAX_HOTELS_COUNT: int = 5
    MAX_PHOTO_COUNT: int = 5

    def __init__(self) -> None:
        self.__city: str = ""
        self.__hotels_count: int = 0
        self.__should_show_photo: bool = False
        self.__photo_count: int = 0
        self.__sort_order: str = "PRICE"
        self.__price_range: List[float] = []
        self.__distance_range: List[float] = []

    @classmethod
    def max_photo_count(cls) -> int:
        """Max photo count which bot send to user

        Returns:
            int: max photo count
        """
        return cls.MAX_PHOTO_COUNT

    @classmethod
    def max_hotel_count(cls) -> int:
        """Max hotels count which bot send to user

        Returns:
            int: max hotels count
        """
        return cls.MAX_HOTELS_COUNT

    @property
    def city(self) -> str:
        """Return user destination

        Returns:
            str: destination
        """
        return self.__city

    @city.setter
    def city(self, value: str) -> None:
        """Assign destination

        Args:
            value (str): destinatin
        """
        self.__city = value

    @property
    def hotels_count(self) -> int:
        """Return user hotels count

        Returns:
            int: hotels count
        """
        return self.__hotels_count

    @hotels_count.setter
    def hotels_count(self, value: int) -> None:
        """Assign hotels count

        Args:
            value (int): count
        """
        self.__hotels_count = value

    @property
    def should_show_photo(self) -> bool:
        """Return should show photo or not

        Returns:
            bool: should show photo or not
        """
        return self.__should_show_photo

    @should_show_photo.setter
    def should_show_photo(self, value: bool) -> None:
        """Assign should show hotel's photo or not

        Args:
            value (bool): should show photo of hotels or not
        """
        self.__should_show_photo = value

    @property
    def photo_count(self) -> int:
        """Return user photo count

        Returns:
            int: photo count
        """
        return self.__photo_count

    @photo_count.setter
    def photo_count(self, value: int) -> None:
        """Assign photo count

        Args:
            value (int): photo count
        """
        self.__photo_count = value

    @property
    def sort_order(self) -> str:
        """Return user sort order

        Returns:
            str: sort order
        """
        return self.__sort_order

    @sort_order.setter
    def sort_order(self, value: str) -> None:
        """Assign sort order

        Args:
            value (str): sort order
        """
        self.__sort_order = value

    @property
    def price_range(self) -> List[float]:
        """Return max and min user price

        Returns:
            List[float]: Max and min price
        """

        return self.__price_range

    def add_price(self, value: float) -> None:
        """Add price to range

        Args:
            value (float): max or min price value
        """
        self.__price_range.append(value)

    @property
    def distance_range(self) -> List[float]:
        """Return max and min user distance

        Returns:
            List[float]: Max and min distance
        """
        return self.__distance_range

    def add_distance(self, value: float) -> None:
        """Add distance to range

        Args:
            value (float): max or min distance value
        """
        self.__distance_range.append(value)

    def clear_data(self) -> None:
        """Reset all answers to initial values"""
        self.__city = ""
        self.__hotels_count = 0
        self.__should_show_photo = False
        self.__photo_count = 0
        self.__sort_order = "PRICE"
        self.__price_range = []
        self.__distance_range = []
