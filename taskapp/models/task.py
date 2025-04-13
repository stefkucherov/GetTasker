"""
Модуль описания модели задачи.
Используется SQLAlchemy для описания структуры таблицы tasks в БД.
"""

from sqlalchemy import Integer, Column, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from taskapp.database import Base


class Tasks(Base):
    """
    Класс Tasks описывает модель задачи.

    Атрибуты:
        id (int): Уникальный идентификатор задачи.
        user_id (int): Идентификатор пользователя, создавшего задачу.
        board_id (int): Идентификатор доски, к которой привязана задача.
        task_name (str): Название задачи.
        task_description (str): Описание задачи.
        status (str): Статус задачи ("Запланировано", "В работе", "Готово").
        created_at (DateTime): Дата и время создания задачи.
        due_date (DateTime): Дата выполнения задачи (срок).
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String, nullable=False)
    task_description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default="Запланировано")
    email = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=True)
