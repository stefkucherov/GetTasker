"""
Точка входа в приложение FastAPI.
Создаёт экземпляр приложения, подключает роутеры и мидлвари.
"""

from re import search

from fastapi import FastAPI, Query, Depends
from datetime import date
from typing import Optional, List

from pydantic import BaseModel
from starlette.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.templating import Jinja2Templates

from taskapp.routers.users import router as user_router
from taskapp.routers.tasks import router as task_router
from taskapp.routers.boards import router as board_router
from pages.router import router as page_router

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

app = FastAPI()

# CORS для разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Статические файлы (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(task_router)

app.include_router(page_router)

app.include_router(board_router)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    redis = aioredis.from_url("redis://localhost")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
