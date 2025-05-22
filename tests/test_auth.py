import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.asyncio
async def test_register_user_success(ac: AsyncClient):
    response = await ac.post(
        "/auth/register",
        data={"username": "newuser", "email": "new@example.com", "password": "pass123"},
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/auth/login"


@pytest.mark.asyncio
async def test_login_user_success(ac: AsyncClient, test_user):
    response = await ac.post(
        "/auth/login",
        data={"email": test_user.email, "password": "string"},
        follow_redirects=False
    )
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/pages/boards"
    assert "booking_access_token" in response.cookies


@pytest.mark.asyncio
async def test_get_current_user_success(authenticated_ac: AsyncClient, test_user):
    response = await authenticated_ac.get("/auth/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email


@pytest.mark.asyncio
async def test_logout_success(authenticated_ac: AsyncClient):
    response = await authenticated_ac.post("/auth/logout", follow_redirects=False)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/auth/login"
    assert "booking_access_token" not in response.cookies


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(ac: AsyncClient):
    response = await ac.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "токен истек" in response.json()["detail"].lower() or "не авторизован" in response.json()["detail"].lower()


@pytest.fixture
async def authenticated_ac(ac: AsyncClient, test_user):
    response = await ac.post(
        "/auth/login",
        data={"email": test_user.email, "password": "string"},
        follow_redirects=False
    )
    token = response.cookies.get("booking_access_token")
    ac.cookies.set("booking_access_token", token)
    return ac

