"""
Сервис для управления досками задач.

Этот модуль содержит класс `BoardService`, который наследуется от `BaseService` и предоставляет методы для работы
с досками задач, определенными в модели `Boards`. Он поддерживает операции создания, поиска, обновления и удаления
досок, а также получение списка досок с количеством связанных задач.
"""

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.database import get_async_session
from taskapp.models.board import Boards
from taskapp.models.task import Tasks
from taskapp.services.base import BaseService


class BoardService(BaseService):
    model = Boards

    async def get_boards_with_tasks_count(self, user_id: int):
        query = (
            select(
                self.model,
                func.count(Tasks.id).label("tasks_count")
            )
            .outerjoin(Tasks, Tasks.board_id == self.model.id)
            .where(self.model.user_id == user_id)
            .group_by(self.model.id)
        )
        result = await self.session.execute(query)
        boards_with_counts = []
        for board, tasks_count in result:
            board.tasks_count = tasks_count
            boards_with_counts.append(board)
        return boards_with_counts


async def get_board_service(session: AsyncSession = Depends(get_async_session)):
    return BoardService(session)
