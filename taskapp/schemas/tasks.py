"""
Модуль схем для задач.
Используются Pydantic-модели для валидации входных и выходных данных при работе с задачами.
"""

from pydantic import BaseModel, Field
from typing import Optional


class TaskBase(BaseModel):
    """
    Базовая схема задачи.
    Содержит общие поля, используемые при создании и обновлении задач.
    """
    task_name: str = Field(..., description="Название задачи")
    task_description: str = Field(..., description="Описание задачи")
    status: str = Field(..., description='Статус задачи ("новая", "в процессе", "завершена")')


class TaskCreate(TaskBase):
    """
    Схема для создания задачи.
    Наследуется от TaskBase и может быть расширена дополнительными полями.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи.
    Все поля опциональны, так как может обновляться только часть данных.
    """
    task_name: Optional[str] = Field(None, description="Новое название задачи")
    task_description: Optional[str] = Field(None, description="Новое описание задачи")
    status: Optional[str] = Field(None, description='Новый статус задачи')


class TaskOut(TaskBase):
    """
    Схема для вывода данных задачи.
    Может включать идентификатор задачи.
    """
    id: int

    class Config:
        from_attributes = True
