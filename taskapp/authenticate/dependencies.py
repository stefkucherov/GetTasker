"""
Зависимости и вспомогательные функции для проверки авторизации:
- Получение токена из cookie
- Декодирование и валидация JWT
- Получение текущего пользователя по токену
"""

from datetime import timedelta, datetime, UTC

from fastapi import Depends, Request
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.config import settings
from taskapp.database import get_async_session
from taskapp.exceptions import (
    TokenAbsentException,
    TokenExpiredException,
    IncorrectTokenFormatException,
    UnauthorizedException,
)
from taskapp.services.user_service import UserService


def get_token(request: Request):
    token = request.cookies.get('booking_access_token')
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(
        token: str = Depends(get_token),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
    except JWTError:
        raise IncorrectTokenFormatException

    expire: str = payload.get("exp")
    if (not expire) or (int(expire) < int((datetime.now(UTC) + timedelta(minutes=1)).timestamp())):
        raise TokenExpiredException

    user_id: str = payload.get("sub")
    if not user_id:
        raise UnauthorizedException

    service = UserService(session)  # создаём экземпляр сервиса
    user = await service.find_by_id(int(user_id))
    if not user:
        raise UnauthorizedException

    return user
