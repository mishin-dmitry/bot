from typing import Dict
from user import User


class Users:
    """Dict with users from telegram"""

    users: Dict[int, User] = dict()

    @classmethod
    def get_user(cls, id: int) -> User:
        """Get user class from users dict

        Args:
            id (int): user id from char

        Returns:
            User: user class
        """
        return cls.users[id]

    @classmethod
    def add_user(cls, id: int, user: User):
        """Add user to dict

        Args:
            id (int): user id from chat
            user (User): user class
        """
        cls.users[id] = user

    @classmethod
    def has_user(cls, id: int) -> bool:
        """Check if user exists in dict

        Args:
            id (int): user id from chat

        Returns:
            bool: True if user exist otherwise False
        """
        return True if id in cls.users.keys() else False
