"""
Базовый сервис для работы с моделями SQLAlchemy.

Этот модуль содержит класс `BaseService`, который предоставляет общие методы для взаимодействия с базой данных,
такие как поиск записей, создание, обновление и удаление. Он используется как основа для специализированных
сервисов, таких как `UserService`, `BoardService` и `TaskService`, чтобы избежать дублирования кода.

Класс `BaseService` является абстрактным и требует, чтобы дочерние классы определили атрибут `model` — модель
SQLAlchemy, с которой они работают. Все методы асинхронные, что соответствует использованию `AsyncSession`.
"""

from typing import TypeVar, Generic, Type, Optional, Any, Sequence

from sqlalchemy import select, update, delete, and_, Row, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

ModelType = TypeVar("ModelType", bound=DeclarativeBase)


class BaseService(Generic[ModelType]):
    """
    Базовый сервис с типизацией и CRUD-операциями.
    Все наследники должны определить `model`, указывая SQLAlchemy-модель.
    """
    model: Type[ModelType]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def find_by_id(self, model_id: int) -> Optional[ModelType]:
        stmt = select(self.model).where(self.model.id == model_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def find_one_or_none(self, **kwargs) -> Optional[ModelType]:
        stmt = select(self.model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_all(self, **filter_by) -> Sequence[Row[Any] | RowMapping | Any]:
        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_id_and_email_by_id(self, model_id: int) -> Optional[tuple[int, str]]:
        stmt = select(self.model.id, self.model.email).where(self.model.id == model_id)
        result = await self.session.execute(stmt)
        return result.first()

    async def add_some(self, **data) -> ModelType:
        obj = self.model(**data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

    async def update_some(self, model_id: int, user_id: int, **data) -> Optional[ModelType]:
        stmt = (
            update(self.model)
            .where(and_(self.model.id == model_id, self.model.user_id == user_id))
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )
        await self.session.execute(stmt)
        await self.session.commit()

        return await self.find_by_id(model_id)

    async def delete_some(self, model_id: int, user_id: int) -> Optional[ModelType]:
        obj = await self.find_one_or_none(id=model_id, user_id=user_id)
        if not obj:
            return None

        stmt = delete(self.model).where(
            and_(self.model.id == model_id, self.model.user_id == user_id)
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return obj
