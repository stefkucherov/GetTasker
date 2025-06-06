import uuid

import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from taskapp.authenticate.auth import get_password_hash
from taskapp.database import Base
from taskapp.main import app as fastapi_app
from taskapp.models.board import Boards
from taskapp.models.task import Tasks
from taskapp.models.user import Users

DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/gettasker_testbase"


@pytest_asyncio.fixture(scope="function")
async def db_engine():
    engine = create_async_engine(DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    async_session = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session


# 👇 Подмена зависимости get_async_session в FastAPI
@pytest_asyncio.fixture(scope="function", autouse=True)
async def override_get_db(db_session):
    from taskapp.authenticate.dependencies import get_async_session

    async def _override():
        yield db_session

    fastapi_app.dependency_overrides[get_async_session] = _override
    yield
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def ac():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def authenticated_ac(ac, test_user):
    response = await ac.post(
        "/pages/login",
        data={"email": test_user.email, "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code in (302, 303)
    token = response.cookies.get("booking_access_token")
    assert token is not None
    ac.cookies.set("booking_access_token", token)
    yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    unique_suffix = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_suffix}"
    email = f"testuser_{unique_suffix}@example.com"
    hashed_password = get_password_hash("testpassword")

    user = Users(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    await db_session.delete(user)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_board(test_user, db_session: AsyncSession):
    board = Boards(name="Test Board", user_id=test_user.id)
    db_session.add(board)
    await db_session.commit()
    await db_session.refresh(board)
    yield board
    await db_session.delete(board)
    await db_session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_task(test_user, test_board, db_session: AsyncSession):
    task = Tasks(
        user_id=test_user.id,
        board_id=test_board.id,
        task_name="Test Task",
        task_description="Description",
        status="Запланировано",
        email=test_user.email
    )
    db_session.add(task)
    await db_session.commit()
    await db_session.refresh(task)
    yield task
    await db_session.delete(task)
    await db_session.commit()
