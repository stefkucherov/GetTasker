"""
Точка входа в приложение FastAPI.
Создаёт экземпляр приложения, подключает роутеры и мидлвари.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
import os
from typing import Callable  # Добавлено для аннотации типа мидлвара

from taskapp.routers.users import router as user_router
from taskapp.routers.tasks import router as task_router
from taskapp.routers.boards import router as board_router
from pages.router import router as page_router

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:  # Заменили app на _ и убрали предупреждение
    if not os.getenv("TESTING"):  # Пропускаем Redis в тестах
        try:
            redis = aioredis.from_url("redis://localhost", decode_responses=True)
            FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        except Exception as e:
            print(f"Redis не запущен или недоступен. Кеширование отключено: {e}")
    yield


# Инициализация FastAPI-приложения с учетом lifecycle
app = FastAPI(lifespan=lifespan)

# Подключение CORS с явной аннотацией типа
app.add_middleware(
    CORSMiddleware,  # type: ignore[arg-type]  # Подавляем предупреждение о типе
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение всех маршрутов
app.include_router(user_router)
app.include_router(task_router)
app.include_router(board_router)
app.include_router(page_router)
