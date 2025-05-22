from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from taskapp.services.base import BaseService
from taskapp.models.task import Tasks
from taskapp.database import get_async_session


class TaskService(BaseService):
    model = Tasks


async def get_task_service(session: AsyncSession = Depends(get_async_session)):
    return TaskService(session)
