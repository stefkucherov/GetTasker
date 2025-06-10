"""
Инициализация базы данных.
Создаёт асинхронный движок и сессию SQLAlchemy для взаимодействия с БД.
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from taskapp.config import settings
from taskapp.config import logger

try:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
except Exception:
    logger.critical("Ошибка при создании движка БД", exc_info=True)
    raise

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False

)


async def get_async_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session


class Base(DeclarativeBase):
    pass
