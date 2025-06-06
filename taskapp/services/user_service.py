"""
Сервис для управления пользователями в системе.

Этот модуль содержит класс `UserService`, который наследуется от `BaseService` и предоставляет методы для работы
с пользователями, определенными в модели `Users`. Он поддерживает операции поиска, создания, обновления и удаления
пользователей, а также аутентификацию через email.

Пример использования:
    user_service = UserService(session)
    user = await user_service.find_one_or_none(email="user@example.com")
    await user_service.add_some(username="newuser", email="new@example.com", hashed_password="hashedpass")
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.database import get_async_session
from taskapp.models.user import Users
from taskapp.services.base import BaseService


class UserService(BaseService):
    model = Users


async def get_user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(session)
