"""
Модуль описания модели доски.
Используется SQLAlchemy для описания структуры таблицы boards в БД.
"""

from sqlalchemy import Integer, Column, String, ForeignKey, DateTime
from sqlalchemy.sql import func

from taskapp.database import Base


class Boards(Base):
    """
    Класс Boards описывает модель доски задач.

    Атрибуты:
        id (int): Уникальный идентификатор доски.
        user_id (int): Идентификатор пользователя, владельца доски.
        name (str): Название доски.
        created_at (DateTime): Дата и время создания доски.
    """
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
