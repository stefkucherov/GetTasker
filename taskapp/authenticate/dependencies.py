from datetime import timedelta, datetime, UTC

from fastapi import Depends, Request, status
from jose import jwt, JWTError
from taskapp.config import settings
from taskapp.services.user_service import UserService
from taskapp.exceptions import (
    TokenAbsentException,
    TokenExpiredException,
    IncorrectTokenFormatException,
    UnauthorizedException,
)


def get_token(request: Request):
    token = request.cookies.get('booking_access_token')
    if not token:
        raise TokenAbsentException
    return token


async def get_current_user(token: str = Depends(get_token)):
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

    user = await UserService.find_by_id(int(user_id))
    if not user:
        raise UnauthorizedException
    return user
