"""
Модуль модели пользователя.
Определяет структуру таблицы users в базе данных через SQLAlchemy.
"""

from sqlalchemy import Integer, Column, String
from taskapp.database import Base


class Users(Base):
    """
    Модель пользователя.

    Атрибуты:
        id (int): Уникальный идентификатор пользователя.
        email (str): Электронная почта пользователя.
        hashed_password (str): Хэшированный пароль.
        username (str): Отображаемое имя пользователя (логин).
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    username = Column(String, unique=True, nullable=True)
