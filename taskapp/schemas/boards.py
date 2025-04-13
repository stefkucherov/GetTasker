"""
Модуль схем для досок.
Используются Pydantic-модели для валидации входных и выходных данных при работе с досками.
"""

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from taskapp.schemas.tasks import TaskOut


class BoardBase(BaseModel):
    """
    Базовая схема доски.
    Содержит общие поля, используемые при создании и обновлении досок.
    """
    name: str = Field(..., description="Название доски")


class BoardCreate(BoardBase):
    """
    Схема для создания доски.
    Наследуется от BoardBase и может быть расширена дополнительными полями.
    """
    pass


class BoardUpdate(BaseModel):
    """
    Схема для обновления доски.
    Поля опциональны, так как может обновляться только часть данных.
    """
    name: Optional[str] = Field(None, description="Новое название доски")


class BoardOut(BoardBase):
    """
    Схема для вывода данных доски.
    Включает идентификатор доски и дату создания.
    """
    id: int
    created_at: datetime
    tasks_count: Optional[int] = Field(None, description="Количество активных задач")

    class Config:
        from_attributes = True


class BoardWithTasks(BoardOut):
    """
    Расширенная схема для вывода доски вместе со списком задач.
    """
    tasks: List[TaskOut] = []

    class Config:
        from_attributes = True