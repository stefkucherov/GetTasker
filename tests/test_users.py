import pytest
from httpx import AsyncClient

from taskapp.models.user import Users


@pytest.mark.asyncio
async def test_register_user_success(ac: AsyncClient):
    """
    Проверяет успешную регистрацию нового пользователя через HTML-форму.
    Ожидается редирект на страницу логина.
    """
    payload = {
        "username": "NewUser",
        "email": "newuser_unique@example.com",
        "password": "testpassword"
    }
    response = await ac.post(
        "/pages/register",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/pages/login"


@pytest.mark.asyncio
async def test_register_duplicate_email(ac: AsyncClient, test_user: Users):
    """
    Проверяет регистрацию с уже существующей почтой.
    Ожидается ошибка 400 и сообщение о дубликате.
    """
    payload = {
        "username": "AnotherUser",
        "email": test_user.email,
        "password": "testpassword"
    }
    response = await ac.post(
        "/pages/register",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    assert response.status_code == 400
    assert "уже существует" in response.text.lower()


@pytest.mark.asyncio
async def test_login_user_success(ac: AsyncClient, test_user: Users):
    """
    Проверяет успешную авторизацию с корректными данными.
    Ожидается редирект и установка cookie.
    """
    payload = {
        "email": test_user.email,
        "password": "testpassword"
    }
    response = await ac.post(
        "/pages/login",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    assert response.status_code in (302, 303)
    assert response.headers["location"] == "/pages/boards"
    assert "booking_access_token" in response.cookies


@pytest.mark.asyncio
async def test_get_current_user_success(authenticated_ac: AsyncClient, test_user: Users):
    """
    Проверяет, что авторизованный пользователь может получить свои данные через /auth/me.
    """
    response = await authenticated_ac.get("/auth/me")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == test_user.email
    assert user_data["username"] == test_user.username


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(ac: AsyncClient):
    """
    Проверяет, что неавторизованный запрос к /auth/me возвращает 401.
    """
    response = await ac.get("/auth/me")
    assert response.status_code == 401
    assert "токен истек" in response.json()["detail"].lower() or "не авторизован" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_user_profile(authenticated_ac: AsyncClient, test_user: Users):
    """
    Проверяет успешное обновление профиля пользователя (username).
    """
    new_username = f"updated_username_{test_user.id}"
    update_data = {"username": new_username}

    response = await authenticated_ac.patch("/auth/profile", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == new_username
    assert updated_user["email"] == test_user.email
