class Hotel:
    def __init__(
        self, id: str, address: str, distance: str, price: str, name: str
    ) -> None:
        self.__id: str = id
        self.__address: str = address
        self.__distance: str = distance
        self.__price: str = price
        self.__name: str = name

    @property
    def id(self):
        return self.__id

    @property
    def address(self):
        return self.__address

    @property
    def distance(self):
        return self.__distance

    @property
    def price(self):
        return self.__price

    @property
    def name(self):
        return self.__name
