"""
Конфигурация приложения.
Загружает настройки проекта: база данных, переменные окружения и другие параметры.
"""

from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DATABASE_URL: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def get_database_url(cls, values: dict):
        if not all(k in values for k in ("DB_HOST", "DB_PORT", "DB_USER", "DB_PASS", "DB_NAME")):
            raise ValueError("Не все переменные окружения загружены!")

        values["DATABASE_URL"] = (
            f"postgresql+asyncpg://{values['DB_USER']}:{values['DB_PASS']}@"
            f"{values['DB_HOST']}:{values['DB_PORT']}/{values['DB_NAME']}"
        )
        return values

    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

print(settings.DB_HOST)
print(settings.DATABASE_URL)
