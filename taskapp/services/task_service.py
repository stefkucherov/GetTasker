"""
Сервис для работы с задачами.
Наследуется от BaseService и указывает модель Tasks.
"""

from taskapp.services.base import BaseService
from taskapp.models.task import Tasks


class TaskService(BaseService):
    """
    Сервис для операций с задачами.
    Атрибут model указывает на SQLAlchemy-модель Tasks.
    """
    model = Tasks
