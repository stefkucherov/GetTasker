from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from taskapp.services.base import BaseService
from taskapp.models.user import Users
from taskapp.database import get_async_session


class UserService(BaseService):
    model = Users


async def get_user_service(session: AsyncSession = Depends(get_async_session)):
    return UserService(session)
