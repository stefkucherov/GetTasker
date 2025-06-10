"""
Модуль схем для задач.
Используются Pydantic-модели для валидации входных и выходных данных при работе с задачами.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """
    Перечисление допустимых статусов задач.
    Используется для строгой типизации и валидации статуса.
    """
    PLANNED = "Запланировано"
    IN_PROGRESS = "В работе"
    DONE = "Готово"


class TaskBase(BaseModel):
    """
    Базовая схема задачи.
    Содержит общие поля, используемые при создании и обновлении задач.
    """
    task_name: str = Field(..., description="Название задачи")
    task_description: Optional[str] = Field(None, description="Описание задачи")
    status: TaskStatus = Field(default=TaskStatus.PLANNED, description="Статус задачи")
    due_date: Optional[datetime] = Field(None, description="Срок выполнения задачи")


class TaskCreate(TaskBase):
    """
    Схема для создания задачи.
    Наследуется от TaskBase и включает board_id.
    """
    board_id: int = Field(..., description="ID доски, к которой относится задача")


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи.
    Все поля опциональны, так как может обновляться только часть данных.
    """
    task_name: Optional[str] = Field(None, description="Новое название задачи")
    task_description: Optional[str] = Field(None, description="Новое описание задачи")
    status: Optional[TaskStatus] = Field(None, description="Новый статус задачи")
    due_date: Optional[datetime] = Field(None, description="Новый срок выполнения")
    board_id: Optional[int] = Field(None, description="Новый ID доски")


class TaskStatusUpdate(BaseModel):
    """
    Схема для обновления только статуса задачи.
    """
    status: TaskStatus = Field(..., description="Новый статус задачи")


class TaskOut(TaskBase):
    """
    Схема для вывода данных задачи.
    Включает идентификатор задачи и связанные метаданные.
    """
    id: int
    board_id: int
    created_at: datetime
    due_date: Optional[datetime] = None

    class Config:
        from_attributes = True
