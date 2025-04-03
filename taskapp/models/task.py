"""
Модуль описания модели задачи.
Используется SQLAlchemy для описания структуры таблицы tasks в БД.
"""

from sqlalchemy import Integer, Column, String, ForeignKey
from taskapp.database import Base


class Tasks(Base):
    """
    Класс Tasks описывает модель задачи.

    Атрибуты:
        id (int): Уникальный идентификатор задачи.
        task_name (str): Название задачи.
        task_description (str): Описание задачи.
        status (str): Статус задачи (например, "новая", "в процессе", "завершена").
        email (str): Электронная почта пользователя, к которому привязана задача.
        hashed_password (str): Хэшированный пароль (в данном случае хранится для примера,
                                но обычно пароль не должен дублироваться в задаче).
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_name = Column(String, nullable=False)
    task_description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    email = Column(String, nullable=False)

