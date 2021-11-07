from typing import Dict
from user import User


class Users:
    users: Dict[int, User] = dict()

    @classmethod
    def get_user(cls, id: int) -> User:
        return cls.users[id]

    @classmethod
    def add_user(cls, id: int, user: User):
        cls.users[id] = user

    @classmethod
    def has_user(cls, id: int) -> bool:
        return True if id in cls.users.keys() else False
