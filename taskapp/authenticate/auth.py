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
from taskapp.services.user_service import UserService

pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")  # Используем argon2


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
    return encoded_jwt


async def authenticate_user(email: EmailStr, password: str):
    user = await UserService.find_one_or_none(email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
