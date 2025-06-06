"""
Кастомные исключения проекта.
Определяет ошибки, которые используются в бизнес-логике (например, дублирование, доступ).
"""

from fastapi import HTTPException, status

UserAlreadyExistsException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Данный пользователь уже существует"
)

TokenExpiredException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен Истек"
)

TokenAbsentException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Токен Истек"
)

IncorrectTokenFormatException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неверный формат токена"
)

UnauthorizedException = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Неавторизованный доступ"
)

RoomCannotBeBookedException = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Конфликт состояния ресурса"
)
