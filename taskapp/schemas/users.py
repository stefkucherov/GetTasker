"""
Модуль схем для пользователей.
Используются Pydantic-модели для валидации входных и выходных данных при работе с пользователями.
"""

from pydantic import BaseModel, EmailStr, Field


class SUserRegister(BaseModel):
    """
    Схема для регистрации пользователя.

    Атрибуты:
        username (str): Имя пользователя.
        email (EmailStr): Электронная почта пользователя.
        password (str): Пароль пользователя (входной, не хэшированный).
    """
    username: str = Field(..., description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта пользователя")
    password: str = Field(..., description="Пароль пользователя")


class SUserOut(BaseModel):
    """
    Схема для вывода данных пользователя.

    Атрибуты:
        username (str): Имя пользователя.
        email (EmailStr): Электронная почта пользователя.
    """
    username: str = Field(..., description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта пользователя")

    class Config:
        from_attributes = True
