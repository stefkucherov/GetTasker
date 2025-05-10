import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from taskapp.main import app as fastapi_app
from taskapp.database import Base
from taskapp.models.user import Users
from taskapp.authenticate.auth import get_password_hash, create_access_token
import uuid

# Параметры базы данных
DB_HOST = "localhost"
DB_PORT = "5432"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_NAME = "gettasker_testbase"

# Формируем URL подключения
DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Database engine fixture for the test database
@pytest_asyncio.fixture(scope="session")
async def db_engine():
    engine = create_async_engine(DB_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# Database session fixture with transaction rollback
@pytest_asyncio.fixture(scope="function")
async def db_session(db_engine):
    async_session = async_sessionmaker(
        bind=db_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()  # Откатываем изменения после теста


# AsyncClient fixture using ASGITransport
@pytest_asyncio.fixture(scope="function")
async def ac():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


# Authenticated AsyncClient fixture with cookie-based login
@pytest_asyncio.fixture(scope="function")
async def authenticated_ac(test_user, db_session):
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/pages/login",
            data={"email": test_user.email, "password": "testpassword"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        assert response.status_code == 303
        yield client


# Test user creation
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession):
    unique_suffix = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_suffix}"
    email = f"testuser_{unique_suffix}@example.com"
    hashed_password = get_password_hash("testpassword")

    user = Users(
        email=email,
        username=username,
        hashed_password=hashed_password
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    yield user

    await db_session.delete(user)
    await db_session.commit()


# Bearer-token header generation
@pytest_asyncio.fixture(scope="function")
async def auth_headers(test_user, db_session):
    token = create_access_token({"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
