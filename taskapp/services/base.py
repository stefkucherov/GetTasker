"""
Базовый сервис для работы с моделями SQLAlchemy.

Этот модуль содержит класс `BaseService`, который предоставляет общие методы для взаимодействия с базой данных,
такие как поиск записей, создание, обновление и удаление. Он используется как основа для специализированных
сервисов, таких как `UserService`, `BoardService` и `TaskService`, чтобы избежать дублирования кода.

Класс `BaseService` является абстрактным и требует, чтобы дочерние классы определили атрибут `model` — модель
SQLAlchemy, с которой они работают. Все методы асинхронные, что соответствует использованию `AsyncSession`.
"""
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """
    Абстрактный класс сервиса.
    Предполагается, что дочерние классы укажут `model` (модель SQLAlchemy).
    """
    model = None

    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса с обязательной сессией.
        """
        self.session = session

    async def find_by_id(self, model_id: int):
        """
        Найти объект по ID.
        """
        query = select(self.model).where(self.model.id == model_id)
        result = await self.session.execute(query)
        return result.scalars().first()

    async def find_one_or_none(self, **kwargs):
        """
        Найти одну запись по фильтру.
        """
        query = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self, **filter_by):
        """
        Получить все записи с возможной фильтрацией.
        """
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_id_and_email_by_id(self, model_id: int):
        """
        Получить id и email пользователя по ID.
        """
        query = select(self.model.id, self.model.email).where(self.model.id == model_id)
        result = await self.session.execute(query)
        return result.first()

    async def add_some(self, **data):
        """
        Добавить новую запись в базу.
        """
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update_some(self, model_id: int, user_id: int, **data):
        """
        Обновить запись по id и user_id.
        """
        query = update(self.model).where(
            and_(self.model.id == model_id, self.model.user_id == user_id)
        ).values(**data)
        await self.session.execute(query)
        await self.session.commit()

        select_query = select(self.model).where(
            and_(self.model.id == model_id, self.model.user_id == user_id)
        )
        result = await self.session.execute(select_query)
        return result.scalars().first()

    async def delete_some(self, model_id: int, user_id: int):
        """
        Удалить запись по id и user_id.
        """
        select_query = select(self.model).where(
            and_(self.model.id == model_id, self.model.user_id == user_id)
        )
        result = await self.session.execute(select_query)
        obj = result.scalars().first()
        if not obj:
            return None

        query = delete(self.model).where(
            and_(self.model.id == model_id, self.model.user_id == user_id)
        )
        await self.session.execute(query)
        await self.session.commit()
        return obj
