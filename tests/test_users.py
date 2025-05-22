import pytest
from httpx import AsyncClient
from taskapp.models.user import Users


@pytest.mark.asyncio
async def test_register_user_success(ac: AsyncClient):
    """Test successfully registering a new user."""
    payload = {
        "username": "NewUser",
        "email": "newuser_unique@example.com",
        "password": "testpassword"
    }
    response = await ac.post("/auth/register", json=payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Пользователь успешно зарегистрирован"


@pytest.mark.asyncio
async def test_register_duplicate_email(ac: AsyncClient, test_user: Users):
    """Test registration with duplicate email fails."""
    payload = {
        "username": "DifferentName",
        "email": test_user.email,
        "password": "somepassword"
    }
    response = await ac.post("/auth/register", json=payload)
    assert response.status_code == 409
    assert "уже существует" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_user_success(ac: AsyncClient, test_user: Users):
    """Test successfully logging in a user."""
    payload = {
        "email": test_user.email,
        "password": "testpassword"
    }
    response = await ac.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"]


@pytest.mark.asyncio
async def test_login_invalid_credentials(ac: AsyncClient, test_user: Users):
    """Test login with invalid credentials fails."""
    payload = {
        "email": test_user.email,
        "password": "wrong_password"
    }
    response = await ac.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "unauthorized" in response.json()["detail"].lower() or "неверный" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_user(ac: AsyncClient):
    """Test login with non-existent user fails."""
    payload = {
        "email": "nonexistent_user@example.com",
        "password": "doesntmatter"
    }
    response = await ac.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "unauthorized" in response.json()["detail"].lower() or "не найден" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_current_user_success(authenticated_ac: AsyncClient, test_user: Users):
    """Test successfully retrieving current user data."""
    response = await authenticated_ac.get("/auth/me")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == test_user.email
    assert user_data["username"] == test_user.username
    assert user_data["id"] == test_user.id


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(ac: AsyncClient):
    """Test that unauthorized access to current user data fails."""
    response = await ac.get("/auth/me")
    assert response.status_code == 401
    assert "токен истек" in response.json()["detail"].lower() or "не авторизован" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_user_profile(authenticated_ac: AsyncClient, test_user: Users):
    """Test successfully updating user profile."""
    new_username = f"updated_username_{test_user.id}"

    update_data = {
        "username": new_username
    }

    response = await authenticated_ac.patch("/auth/profile", json=update_data)
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["username"] == new_username
    assert updated_user["email"] == test_user.email