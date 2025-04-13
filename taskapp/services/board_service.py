"""
Сервис для работы с досками.
Наследуется от BaseService и указывает модель Boards.
"""

from sqlalchemy import select, func
from taskapp.services.base import BaseService
from taskapp.models.board import Boards
from taskapp.models.task import Tasks
from taskapp.database import async_session_maker


class BoardService(BaseService):
    """
    Сервис для операций с досками задач.
    Атрибут model указывает на SQLAlchemy-модель Boards.
    """
    model = Boards

    @classmethod
    async def get_boards_with_tasks_count(cls, user_id: int):
        """
        Получить все доски пользователя с количеством задач для каждой доски.

        Args:
            user_id: Идентификатор пользователя

        Returns:
            Список досок с подсчетом задач
        """
        async with async_session_maker() as session:
            query = (
                select(
                    cls.model,
                    func.count(Tasks.id).label("tasks_count")
                )
                .outerjoin(Tasks, Tasks.board_id == cls.model.id)
                .where(cls.model.user_id == user_id)
                .group_by(cls.model.id)
            )
            result = await session.execute(query)
            boards_with_counts = []

            for board, tasks_count in result:
                board.tasks_count = tasks_count
                boards_with_counts.append(board)

            return boards_with_counts
