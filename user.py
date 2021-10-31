class User:
    def __init__(self) -> None:
        self.__city: str = ""
        self.__hotels_count: int = 0
        self.__should_show_photo: bool = False
        self.__photo_count: int = 0
        self.__sort_order: str = "PRICE"

    @property
    def city(self):
        return self.__city

    @city.setter
    def city(self, value: str):
        self.__city = value

    @property
    def hotels_count(self):
        return self.__hotels_count

    @hotels_count.setter
    def hotels_count(self, value: int):
        self.__hotels_count = value

    @property
    def should_show_photo(self):
        return self.__should_show_photo

    @should_show_photo.setter
    def should_show_photo(self, value: bool):
        self.__should_show_photo = value

    @property
    def photo_count(self):
        return self.__photo_count

    @photo_count.setter
    def photo_count(self, value: int):
        self.__photo_count = value

    @property
    def sort_order(self):
        return self.__sort_order

    @sort_order.setter
    def sort_order(self, value: str):
        self.__sort_order = value
