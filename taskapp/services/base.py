from taskapp.database import async_session_maker
from sqlalchemy import select, insert, delete, update, and_
from sqlalchemy.orm import load_only


class BaseService:
    model = None

    @classmethod
    async def find_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = select(cls.model).where(cls.model.id == model_id)
            result = await session.execute(query)
            return (
                result.scalars().first()
            )

    @classmethod
    async def find_one_or_none(cls, **kwargs):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**kwargs)
            result = await session.execute(query)
            return (
                result.scalar_one_or_none()
            )

    @classmethod
    async def get_all(cls, **filter_by):
        async with async_session_maker() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return (
                result.scalars().all()
            )

    @classmethod
    async def get_id_and_email_by_id(cls, model_id: int):
        async with async_session_maker() as session:
            query = (
                select(cls.model.id, cls.model.email)
                .where(cls.model.id == model_id)
            )
            result = await session.execute(query)
            return result.first()

    @classmethod
    async def add_some(cls, **data):
        async with async_session_maker() as session:
            obj = cls.model(**data)
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    @classmethod
    async def update_some(cls, model_id: int, user_id: int, **data):
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
        async with async_session_maker() as session:
            # Сначала выбираем объект, чтобы вернуть его после удаления
            select_query = select(cls.model).where(
                and_(cls.model.id == model_id, cls.model.user_id == user_id)
            )
            result = await session.execute(select_query)
            obj = result.scalars().first()
            if not obj:
                return None
            # Удаляем запись
            query = delete(cls.model).where(
                and_(cls.model.id == model_id, cls.model.user_id == user_id)
            )
            await session.execute(query)
            await session.commit()
            return obj
