"""
Инициализация базы данных.
Создаёт асинхронный движок и сессию SQLAlchemy для взаимодействия с БД.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from taskapp.config import settings


engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass
