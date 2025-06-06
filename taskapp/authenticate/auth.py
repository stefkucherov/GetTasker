"""
Утилиты для аутентификации:
- Хеширование и проверка пароля
- Генерация JWT-токена
- Асинхронная аутентификация пользователя по email и паролю
"""

from datetime import datetime, timedelta, UTC

from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr

from taskapp.config import settings
from taskapp.database import get_async_session
from taskapp.services.user_service import UserService

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)


async def authenticate_user(email: EmailStr, password: str):
    """
    Аутентифицирует пользователя по email и паролю.

    :param email: Email пользователя
    :param password: Пароль в открытом виде
    :return: Пользователь или None
    """
    async with get_async_session() as session:
        user_service = UserService(session)
        user = await user_service.find_one_or_none(email=email)

    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
