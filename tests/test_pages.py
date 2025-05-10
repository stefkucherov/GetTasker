import pytest
from httpx import AsyncClient
from taskapp.models.board import Boards
from taskapp.models.user import Users
from taskapp.exceptions import UnauthorizedException


@pytest.mark.asyncio
async def test_get_login_page(ac: AsyncClient):
    """Тестирование доступа к странице входа."""
    response = await ac.get("/pages/login")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "auth.html" in response.text or "Вход" in response.text


@pytest.mark.asyncio
async def test_get_register_page(ac: AsyncClient):
    """Тестирование доступа к странице регистрации."""
    response = await ac.get("/pages/register")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "regs.html" in response.text or "Регистрация" in response.text


@pytest.mark.asyncio
async def test_get_index_page_unauthorized(ac: AsyncClient):
    """Тестирование редиректа неавторизованного пользователя с главной страницы на страницу входа."""
    response = await ac.get("/pages/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/pages/login" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_get_index_page_authorized(authenticated_ac: AsyncClient):
    """Тестирование редиректа авторизованного пользователя с главной страницы на страницу досок."""
    response = await authenticated_ac.get("/pages/", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/pages/boards" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_get_boards_page_authorized(authenticated_ac: AsyncClient, test_user: Users):
    """Тестирование доступа к странице списка досок для авторизованного пользователя."""
    response = await authenticated_ac.get("/pages/boards")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "taskboard.html" in response.text or "Доски" in response.text
    assert test_user.email in response.text


@pytest.mark.asyncio
async def test_get_boards_page_unauthorized(ac: AsyncClient):
    """Тестирование редиректа неавторизованного пользователя со страницы досок на страницу входа."""
    response = await ac.get("/pages/boards", follow_redirects=False)
    assert response.status_code in (302, 307)
    assert "/pages/login" in response.headers.get("location", "")


@pytest.mark.asyncio
async def test_get_board_details_page_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Тестирование доступа к странице деталей доски для авторизованного пользователя."""
    response = await authenticated_ac.get(f"/pages/boards/{test_board.id}")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "taskboard.html" in response.text
    assert test_board.name in response.text


@pytest.mark.asyncio
async def test_get_board_details_page_not_found(authenticated_ac: AsyncClient):
    """Тестирование доступа к странице несуществующей доски."""
    response = await authenticated_ac.get("/pages/boards/999999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_board_details_page_unauthorized(ac: AsyncClient, test_board: Boards):
    """Тестирование доступа к странице деталей доски без авторизации."""
    response = await ac.get(f"/pages/boards/{test_board.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == UnauthorizedException.detail
