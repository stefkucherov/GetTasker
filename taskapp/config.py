"""
Конфигурация приложения.
Загружает настройки проекта: база данных, переменные окружения и другие параметры.
"""

import logging
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
    REDIS_URL: str = "redis://localhost:6379"

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

    SECRET_KEY: str = "G8Yt@xZ3vK!e7p9rW2sDfQ0uL$MnA6JhVbzXoPc"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

logger = logging.getLogger("gettasker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
)
logger.addHandler(handler)
