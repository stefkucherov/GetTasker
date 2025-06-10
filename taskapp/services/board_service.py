"""
Сервис для управления пользователями в системе.

Этот модуль содержит класс `UserService`, который наследуется от `BaseService` и предоставляет методы для работы
с пользователями, определенными в модели `Users`. Он поддерживает операции поиска, создания, обновления и удаления
пользователей, а также аутентификацию через email.
"""

from typing import List

from fastapi import Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.database import get_async_session
from taskapp.models.board import Boards
from taskapp.models.task import Tasks
from taskapp.services.base import BaseService


class BoardService(BaseService[Boards]):
    model = Boards

    async def get_boards_with_tasks_count(self, user_id: int) -> List[Boards]:
        """
        Вернуть список досок пользователя вместе с count связанных задач.
        """
        stmt = (
            select(self.model, func.count(Tasks.id).label("tasks_count"))
            .outerjoin(Tasks, Tasks.board_id == self.model.id)
            .where(self.model.user_id == user_id)
            .group_by(self.model.id)
        )
        result = await self.session.execute(stmt)

        boards: List[Boards] = []
        for board, count in result:
            board.tasks_count = count
            boards.append(board)
        return boards


async def get_board_service(session: AsyncSession = Depends(get_async_session)) -> BoardService:
    """
    Зависимость FastAPI для BoardService.
    """
    return BoardService(session)
