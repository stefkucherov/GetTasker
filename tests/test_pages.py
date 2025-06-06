import pytest
from httpx import AsyncClient

from taskapp.models.board import Boards


@pytest.mark.asyncio
async def test_get_login_page(ac: AsyncClient):
    response = await ac.get("/pages/login")
    assert response.status_code == 200
    assert "<form" in response.text.lower()


@pytest.mark.asyncio
async def test_get_register_page(ac: AsyncClient):
    response = await ac.get("/pages/register")
    assert response.status_code == 200
    assert "<form" in response.text.lower()


@pytest.mark.asyncio
async def test_login_post_success(ac: AsyncClient, test_user):
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
    assert "booking_access_token" in response.cookies


@pytest.mark.asyncio
async def test_login_post_invalid_credentials(ac: AsyncClient, test_user):
    payload = {
        "email": test_user.email,
        "password": "wrongpassword"
    }
    response = await ac.post(
        "/pages/login",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    assert "неверная" in response.text.lower() or "invalid" in response.text.lower()


@pytest.mark.asyncio
async def test_register_post_success(ac: AsyncClient):
    payload = {
        "username": "RegisterPageUser",
        "email": "registerpage@example.com",
        "password": "testpassword"
    }
    response = await ac.post(
        "/pages/register",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    assert response.status_code in (302, 303)
    assert "/pages/login" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_get_index_page_redirect_when_unauthorized(ac: AsyncClient):
    response = await ac.get("/pages/", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/pages/login" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_get_index_page_authorized(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/pages/", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/pages/boards" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_get_boards_page_authorized(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/pages/boards")
    assert response.status_code == 200
    assert "boards" in response.text.lower()


@pytest.mark.asyncio
async def test_get_board_details_page_success(authenticated_ac: AsyncClient, test_board: Boards):
    response = await authenticated_ac.get(f"/pages/boards/{test_board.id}")
    assert response.status_code == 200
    assert str(test_board.name).lower() in response.text.lower()


@pytest.mark.asyncio
async def test_get_board_details_page_not_found(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/pages/boards/999999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_board_page_success(authenticated_ac: AsyncClient):
    payload = {
        "name": "Board Created from Page"
    }
    response = await authenticated_ac.post(
        "/pages/boards",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    assert response.status_code in (302, 303)
    assert "/pages/boards" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_create_task_page_success(authenticated_ac: AsyncClient, test_board: Boards):
    payload = {
        "task_name": "Task from Page",
        "task_description": "Created in test",
        "due_date": "2025-06-05",
        "task_status": "Запланировано"
    }
    response = await authenticated_ac.post(
        f"/pages/boards/{test_board.id}/tasks",
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        follow_redirects=False
    )
    assert response.status_code in (302, 303)
    assert f"/pages/boards/{test_board.id}" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_logout_page(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/pages/logout", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/pages/login" in response.headers.get("location", "")
    cookie = response.headers.get("set-cookie", "")
    assert "booking_access_token=" in cookie
    assert "Max-Age=0" in cookie
    assert "Path=/" in cookie
    assert "HttpOnly" in cookie
