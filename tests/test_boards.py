import pytest
from httpx import AsyncClient
from taskapp.models.board import Boards
from taskapp.models.user import Users
from taskapp.exceptions import UnauthorizedException


@pytest.mark.asyncio
async def test_get_all_boards_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Тестирование получения всех досок текущего пользователя."""
    response = await authenticated_ac.get("/boards/")
    assert response.status_code == 200
    boards = response.json()
    assert isinstance(boards, list)
    assert any(board["id"] == test_board.id for board in boards)
    assert any(board["name"] == test_board.name for board in boards)


@pytest.mark.asyncio
async def test_get_board_by_id_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Тестирование получения доски по ID."""
    response = await authenticated_ac.get(f"/boards/{test_board.id}")
    assert response.status_code == 200
    board = response.json()
    assert board["id"] == test_board.id
    assert board["name"] == test_board.name
    assert "created_at" in board
    assert board["tasks_count"] is not None


@pytest.mark.asyncio
async def test_get_board_not_found(authenticated_ac: AsyncClient):
    """Тестирование получения несуществующей доски."""
    response = await authenticated_ac.get("/boards/999999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_board_success(authenticated_ac: AsyncClient):
    """Тестирование создания новой доски."""
    payload = {"name": "New Test Board"}
    response = await authenticated_ac.post("/boards/", json=payload)
    assert response.status_code == 201
    board = response.json()
    assert board["name"] == payload["name"]
    assert "id" in board
    assert "created_at" in board
    assert board["tasks_count"] == 0


@pytest.mark.asyncio
async def test_update_board_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Тестирование обновления доски."""
    update_data = {"name": "Updated Board Name"}
    response = await authenticated_ac.put(f"/boards/{test_board.id}", json=update_data)
    assert response.status_code == 200
    updated_board = response.json()
    assert updated_board["id"] == test_board.id
    assert updated_board["name"] == update_data["name"]


@pytest.mark.asyncio
async def test_update_board_not_found(authenticated_ac: AsyncClient):
    """Тестирование обновления несуществующей доски."""
    update_data = {"name": "Nonexistent Board"}
    response = await authenticated_ac.put("/boards/999999", json=update_data)
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_board_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Тестирование удаления доски."""
    response = await authenticated_ac.delete(f"/boards/{test_board.id}")
    assert response.status_code == 204
    check_response = await authenticated_ac.get(f"/boards/{test_board.id}")
    assert check_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_board_not_found(authenticated_ac: AsyncClient):
    """Тестирование удаления несуществующей доски."""
    response = await authenticated_ac.delete("/boards/999999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_board_unauthorized_access(ac: AsyncClient, test_board: Boards):
    """Тестирование доступа к доскам без авторизации."""
    response = await ac.get(f"/boards/{test_board.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == UnauthorizedException.detail
