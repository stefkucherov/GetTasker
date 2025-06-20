import pytest
from httpx import AsyncClient

from taskapp.models.board import Boards


@pytest.mark.asyncio
async def test_get_all_boards_success(authenticated_ac: AsyncClient, test_board: Boards):
    """
    Проверяет успешное получение всех досок текущего пользователя.
    Ожидается статус 200 и наличие созданной тестовой доски в ответе.
    """
    response = await authenticated_ac.get("/boards/")
    assert response.status_code == 200
    boards = response.json()
    assert isinstance(boards, list), "Response should be a list of boards"
    assert any(board["id"] == test_board.id for board in boards), "Created test board not found in response"


@pytest.mark.asyncio
async def test_get_board_by_id_success(authenticated_ac: AsyncClient, test_board: Boards):
    """
    Проверяет успешное получение доски по её ID.
    Ожидается, что данные совпадают с тестовой доской.
    """
    response = await authenticated_ac.get(f"/boards/{test_board.id}")
    assert response.status_code == 200
    board = response.json()
    assert board["id"] == test_board.id
    assert board["name"] == test_board.name


@pytest.mark.asyncio
async def test_get_board_not_found(authenticated_ac: AsyncClient):
    """
    Проверяет, что запрос несуществующей доски возвращает 404.
    """
    response = await authenticated_ac.get("/boards/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() or "не найден" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_board_success(authenticated_ac: AsyncClient):
    """
    Проверяет успешное создание новой доски.
    После создания доска удаляется (чистка).
    """
    payload = {"name": "New Test Board"}
    response = await authenticated_ac.post("/boards/", json=payload)
    assert response.status_code == 201
    board = response.json()
    assert board["name"] == payload["name"]
    assert "id" in board

    delete_response = await authenticated_ac.delete(f"/boards/{board['id']}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_update_board_success(authenticated_ac: AsyncClient, test_board: Boards):
    """
    Проверяет успешное обновление имени доски.
    """
    update_data = {"name": "Updated Board Name"}
    response = await authenticated_ac.put(f"/boards/{test_board.id}", json=update_data)
    assert response.status_code == 200
    updated_board = response.json()
    assert updated_board["name"] == update_data["name"]
    assert updated_board["id"] == test_board.id


@pytest.mark.asyncio
async def test_update_board_not_found(authenticated_ac: AsyncClient):
    """
    Проверяет, что попытка обновить несуществующую доску возвращает 404.
    """
    response = await authenticated_ac.put("/boards/999999", json={"name": "x"})
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() or "не найден" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_board_success(authenticated_ac: AsyncClient, db_session):
    """
    Проверяет успешное удаление доски.
    Создаёт доску, удаляет её и убеждается, что она больше недоступна.
    """
    new_board_response = await authenticated_ac.post("/boards/", json={"name": "Board to Delete"})
    assert new_board_response.status_code == 201
    board_id = new_board_response.json()["id"]

    # Now delete it
    response = await authenticated_ac.delete(f"/boards/{board_id}")
    assert response.status_code == 204

    # Verify it's gone
    get_response = await authenticated_ac.get(f"/boards/{board_id}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_board_not_found(authenticated_ac: AsyncClient):
    """
    Проверяет, что удаление несуществующей доски возвращает 404.
    """
    response = await authenticated_ac.delete("/boards/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower() or "не найден" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_board_unauthorized_access(ac: AsyncClient, test_board: Boards):
    """
    Проверяет, что доступ к доске без авторизации возвращает 401.
    """
    response = await ac.get(f"/boards/{test_board.id}")
    assert response.status_code == 401
    assert "токен истек" in response.json()["detail"].lower() or "не авторизован" in response.json()["detail"].lower()
