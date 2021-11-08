class Hotel:
    """Info about hotel"""

    def __init__(
        self,
        id: str,
        address: str,
        distance: float,
        str_price: str,
        price: float,
        name: str,
    ) -> None:
        self.__id: str = id
        self.__address: str = address
        self.__distance: float = distance
        self.__str_price: str = str_price
        self.__name: str = name
        self.__price: float = price

    @property
    def id(self) -> str:
        return self.__id

    @property
    def address(self) -> str:
        return self.__address

    @property
    def distance(self) -> float:
        return self.__distance

    @property
    def str_price(self) -> str:
        return self.__str_price

    @property
    def price(self) -> float:
        return self.__price

    @property
    def name(self) -> str:
        return self.__name
