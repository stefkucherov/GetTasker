"""
Сервис для управления задачами в системе.

Этот модуль содержит класс `TaskService`, который наследуется от `BaseService` и предоставляет методы для работы
с задачами, определенными в модели `Tasks`. Он поддерживает операции поиска, создания, обновления и удаления задач,
а также фильтрацию по различным параметрам, таким как `board_id`.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.database import get_async_session
from taskapp.models.task import Tasks
from taskapp.services.base import BaseService


class TaskService(BaseService[Tasks]):
    model = Tasks


async def get_task_service(session: AsyncSession = Depends(get_async_session)) -> TaskService:
    """
    Зависимость FastAPI для TaskService.
    """
    return TaskService(session)
