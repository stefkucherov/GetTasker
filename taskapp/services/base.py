"""
Базовый сервис для работы с моделями SQLAlchemy.
Обеспечивает универсальные методы получения, добавления, обновления и удаления данных.
"""

from taskapp.database import async_session_maker
from sqlalchemy import select, insert, delete, update, and_
from sqlalchemy.orm import load_only


class BaseService:
    """
    Абстрактный класс сервиса.
    Предполагается, что дочерние классы укажут `model` (модель SQLAlchemy).
    """
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        """
        Найти объект по ID.

        Args:
            model_id: Идентификатор записи

        Returns:
            Объект модели или None
        """
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == model_id)
            result = await session.execute(query)
            return result.scalars().first()

    @classmethod
    async def find_one_or_none(cls, **kwargs):
        """
        Найти одну запись по фильтру.

        Args:
            **kwargs: Поля фильтрации (например, email=...)

        Returns:
            Один объект модели или None
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, **filter_by):
        """
        Получить все записи с возможной фильтрацией.

        Args:
            **filter_by: Условия фильтрации (например, user_id=...)

        Returns:
            Список объектов модели
        """
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def get_id_and_email_by_id(cls, model_id: int):
        """
        Получить id и email пользователя по ID.

        Args:
            model_id: Идентификатор пользователя

        Returns:
            Кортеж (id, email) или None
        """
        async with async_session_maker() as session:
            query = (
                select(cls.model.id, cls.model.email)
                .where(cls.model.id == model_id)
            )
            result = await session.execute(query)
            return result.first()

    @classmethod
    async def add_some(cls, **data):
        """
        Добавить новую запись в базу.

        Args:
            **data: Данные для создания объекта

        Returns:
            Созданный объект модели
        """
        async with async_session_maker() as session:
            obj = cls.model(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def update_some(cls, model_id: int, user_id: int, **data):
        """
        Обновить запись по id и user_id.

        Args:
            model_id: Идентификатор записи
            user_id: Идентификатор пользователя (владелец)
            **data: Данные для обновления

        Returns:
            Обновлённый объект или None
        """
        async with async_session_maker() as session:
            query = update(cls.model).where(
                and_(cls.model.id == model_id, cls.model.user_id == user_id)
            ).values(**data)
            await session.execute(query)
            await session.commit()

            select_query = select(cls.model).where(
                and_(cls.model.id == model_id, cls.model.user_id == user_id)
            )
            result = await session.execute(select_query)
            return result.scalars().first()

    @classmethod
    async def delete_some(cls, model_id: int, user_id: int):
        """
        Удалить запись по id и user_id.

        Args:
            model_id: Идентификатор записи
            user_id: Идентификатор пользователя (владелец)

        Returns:
            Удалённый объект или None
        """
        async with async_session_maker() as session:
            # Сначала получаем объект, чтобы вернуть после удаления
            select_query = select(cls.model).where(
                and_(cls.model.id == model_id, cls.model.user_id == user_id)
            )
            result = await session.execute(select_query)
            obj = result.scalars().first()
            if not obj:
                return None

            query = delete(cls.model).where(
                and_(cls.model.id == model_id, cls.model.user_id == user_id)
            )
            await session.execute(query)
            await session.commit()
            return obj

