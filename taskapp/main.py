"""
Точка входа в приложение FastAPI.
Создаёт экземпляр приложения, подключает роутеры и мидлвари.
"""

import os
import redis
import redis.exceptions
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from taskapp.config import settings, logger
from pages.router import router as page_router
from taskapp.routers.boards import router as board_router
from taskapp.routers.tasks import router as task_router
from taskapp.routers.users import router as user_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if not os.getenv("TESTING"):
        try:
            redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
            FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        except redis.exceptions.RedisError:
            logger.warning(
                "Redis не запущен или недоступен. Кеширование отключено",
                exc_info=True
            )
    yield


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
