import pytest
from httpx import AsyncClient
from taskapp.models.user import Users
from taskapp.exceptions import UserAlreadyExistsException, UnauthorizedException


@pytest.mark.asyncio
async def test_register_user_success(ac: AsyncClient):
    """Тестирование успешной регистрации нового пользователя."""
    payload = {
        "username": "NewUser",
        "email": "newuser@example.com",
        "password": "testpassword123"
    }
    response = await ac.post("/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Пользователь успешно зарегистрирован"}


@pytest.mark.asyncio
async def test_register_duplicate_email(ac: AsyncClient, test_user: Users):
    """Тестирование регистрации с уже существующим email."""
    payload = {
        "username": "DuplicateUser",
        "email": test_user.email,
        "password": "anypassword"
    }
    response = await ac.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == UserAlreadyExistsException.detail


@pytest.mark.asyncio
async def test_login_user_success(ac: AsyncClient, test_user: Users):
    """Тестирование успешного логина."""
    payload = {
        "email": test_user.email,
        "password": "testpassword"
    }
    response = await ac.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "booking_access_token" in response.headers.get("set-cookie", "")


@pytest.mark.asyncio
async def test_login_invalid_credentials(ac: AsyncClient, test_user: Users):
    """Тестирование логина с неверным паролем."""
    payload = {
        "email": test_user.email,
        "password": "wrongpassword"
    }
    response = await ac.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == UnauthorizedException.detail


@pytest.mark.asyncio
async def test_login_nonexistent_user(ac: AsyncClient):
    """Тестирование логина с несуществующим пользователем."""
    payload = {
        "email": "nonexistent@example.com",
        "password": "irrelevant"
    }
    response = await ac.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == UnauthorizedException.detail


@pytest.mark.asyncio
async def test_get_current_user_success(authenticated_ac: AsyncClient, test_user: Users):
    """Тестирование получения данных текущего пользователя."""
    response = await authenticated_ac.get("/auth/me")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == test_user.username
    assert user_data["email"] == test_user.email
    assert user_data["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(ac: AsyncClient):
    """Тестирование получения данных пользователя без авторизации."""
    response = await ac.get("/auth/me")
    assert response.status_code == 401
    assert "токен" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_logout_success(authenticated_ac: AsyncClient):
    """Тестирование успешного логаута."""
    response = await authenticated_ac.post("/auth/logout")
    assert response.status_code == 200
    assert response.json() == {"message": "Logged out"}
    assert "booking_access_token" in response.headers.get("set-cookie", "")
    assert "expires=Thu, 01 Jan 1970" in response.headers.get("set-cookie", "")
