"""
Сервис для работы с пользователями.
Наследуется от BaseService и указывает модель Users.
"""

from taskapp.services.base import BaseService
from taskapp.models.user import Users


class UserService(BaseService):
    """
    Сервис для операций с пользователями.
    Атрибут model указывает на SQLAlchemy-модель Users.
    """
    model = Users
