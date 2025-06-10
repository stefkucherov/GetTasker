"""
Сервис для управления пользователями.
Расширяет базовый CRUD-функционал и добавляет обновление профиля.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.database import get_async_session
from taskapp.models.user import Users
from taskapp.services.base import BaseService


class UserService(BaseService):
    model = Users

    async def update_profile(self, user_id: int, new_username: str | None):
        """
        Обновить профиль пользователя.
        """
        user = await self.find_by_id(user_id)
        if not user:
            return None

        if new_username:
            user.username = new_username
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        return user


async def get_user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(session)
