import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(authenticated_ac: AsyncClient):
    """
    Проверяет, что при авторизации зарегистрированный пользователь перенаправляется на страницу /pages/boards.
    """
    response = await authenticated_ac.get("/pages/boards")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_register_user_json(ac: AsyncClient):
    """
    Проверяет JSON-регистрацию нового пользователя.
    Убедимся, что ответ 200 и сообщение успешное.
    """
    response = await ac.post(
        "/auth/register",
        json={"username": "test_user", "email": "test_user@example.com", "password": "securepass"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Пользователь успешно зарегистрирован"


@pytest.mark.asyncio
async def test_register_existing_user(ac: AsyncClient, test_user):
    """
    Проверяет попытку регистрации пользователя с уже существующим email.
    Ожидается ошибка 409.
    """
    response = await ac.post(
        "/auth/register",
        json={
            "username": test_user.username,
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "user already exists"


@pytest.mark.asyncio
async def test_login_user_json(ac: AsyncClient, test_user):
    """
    Проверяет успешную авторизацию пользователя по email/password через JSON.
    Ожидается возврат токена.
    """
    response = await ac.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_password(ac: AsyncClient, test_user):
    """
    Проверяет попытку логина с неверным паролем.
    Ожидается ошибка 401.
    """
    response = await ac.post(
        "/auth/login",
        json={
            "email": test_user.email,
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "invalid credentials"
