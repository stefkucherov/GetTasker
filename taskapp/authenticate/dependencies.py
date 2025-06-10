"""
Зависимости и вспомогательные функции для проверки авторизации:
- Получение токена из cookie
- Декодирование и валидация JWT
- Получение текущего пользователя по токену
- Унифицированная проверка владения объектом (verify_ownership)
"""

from datetime import timedelta, datetime, UTC
from typing import Any

from fastapi import Depends, Request, HTTPException
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from taskapp.config import settings
from taskapp.database import get_async_session
from taskapp.exceptions import (
    TokenExpiredException,
    IncorrectTokenFormatException,
    UnauthorizedException,
)
from taskapp.services.user_service import UserService


def get_token(request: Request) -> str:
    """
    Извлекает токен из cookie запроса.

    Raises:
        TokenExpiredException: если токен отсутствует.
    """
    token = request.cookies.get('booking_access_token')
    if not token:
        raise TokenExpiredException
    return token


async def get_current_user(
        token: str = Depends(get_token),
        session: AsyncSession = Depends(get_async_session)
):
    """
    Извлекает пользователя из токена и проверяет его валидность.

    Raises:
        IncorrectTokenFormatException: если JWT некорректный.
        TokenExpiredException: если токен просрочен.
        UnauthorizedException: если пользователь не найден.

    Returns:
        Users: текущий пользователь
    """
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

    service = UserService(session)
    user = await service.find_by_id(int(user_id))
    if not user:
        raise UnauthorizedException

    return user


async def verify_ownership(
        service: Any,
        model_id: int,
        user_id: int,
        detail: str = "Ресурс не найден"
):
    """
    Унифицированная проверка владения сущностью (task, board и т.п.).

    Args:
        service (Any): сервис (например, TaskService, BoardService)
        model_id (int): ID объекта
        user_id (int): ID текущего пользователя
        detail (str): сообщение об ошибке при отсутствии объекта

    Raises:
        HTTPException: 404, если объект не найден или не принадлежит пользователю
    """
    item = await service.find_one_or_none(id=model_id, user_id=user_id)
    if not item:
        raise HTTPException(status_code=404, detail=detail)
    return item
