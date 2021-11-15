from abc import ABC, abstractmethod
from telebot.types import CallbackQuery, Message


class AbsHandler(ABC):
    """Abstract class Handler, defined two method should be implemented
       in subclasses

    Raises:
        NotImplementedError: if initialize_handler method doesn't implemented
    """

    @abstractmethod
    def initialize_handler(self, message: Message) -> None:
        """Start user/bot communication chain

        Args:
            message (Message): Message object sent from bot

        Raises:
            NotImplementedError: if method doesn't implemented
        """
        raise NotImplementedError("method should be implemented")

    def continue_chain(self, call: CallbackQuery) -> None:
        """Continue chain after user chose option from keyboard

        Args:
            call (CallbackQuery): CallbackQuery send from bot
        """
        return
