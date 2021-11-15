from handlers.lowprice import Lowprice
from user import User


class Highprice(Lowprice):
    """Class to handle /highprice command

    Args:
        Handler ([type]): Class which handle /lowprice command
    """

    def __init__(self, user: User) -> None:
        super().__init__(user)

        self._user.sort_order = "PRICE_HIGHEST_FIRST"
        self._command = "/highprice"
