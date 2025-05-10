import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta, UTC
from taskapp.models.task import Tasks
from taskapp.models.board import Boards
from taskapp.models.user import Users
from taskapp.exceptions import UnauthorizedException


@pytest.mark.asyncio
async def test_get_all_tasks_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """Тестирование получения всех задач текущего пользователя."""
    response = await authenticated_ac.get("/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert isinstance(tasks, list)
    assert any(task["id"] == test_task.id for task in tasks)
    assert tasks[0]["task_name"] == test_task.task_name
    assert tasks[0]["board_id"] == test_task.board_id


@pytest.mark.asyncio
async def test_get_tasks_with_board_filter(authenticated_ac: AsyncClient, test_task: Tasks, test_board: Boards):
    """Тестирование фильтрации задач по board_id."""
    response = await authenticated_ac.get(f"/tasks/?board_id={test_board.id}")
    assert response.status_code == 200
    tasks = response.json()
    assert all(task["board_id"] == test_board.id for task in tasks)
    assert any(task["id"] == test_task.id for task in tasks)


@pytest.mark.asyncio
async def test_get_tasks_with_status_filter(authenticated_ac: AsyncClient, test_task: Tasks):
    """Тестирование фильтрации задач по статусу."""
    response = await authenticated_ac.get("/tasks/?status_filter=Запланировано")
    assert response.status_code == 200
    tasks = response.json()
    assert all(task["status"] == "Запланировано" for task in tasks)
    assert any(task["id"] == test_task.id for task in tasks)


@pytest.mark.asyncio
async def test_get_task_by_id_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """Тестирование получения задачи по ID."""
    response = await authenticated_ac.get(f"/tasks/{test_task.id}")
    assert response.status_code == 200
    task = response.json()
    assert task["id"] == test_task.id
    assert task["task_name"] == test_task.task_name
    assert task["status"] == test_task.status


@pytest.mark.asyncio
async def test_get_task_not_found(authenticated_ac: AsyncClient):
    """Тестирование получения несуществующей задачи."""
    response = await authenticated_ac.get("/tasks/999999")
    assert response.status_code == 404
    assert "не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_task_success(authenticated_ac: AsyncClient, test_board: Boards):
    """Тестирование создания новой задачи."""
    payload = {
        "task_name": "New Task",
        "task_description": "Test task description",
        "status": "В работе",
        "due_date": (datetime.now(UTC) + timedelta(days=2)).isoformat(),
        "board_id": test_board.id
    }
    response = await authenticated_ac.post("/tasks/", json=payload)
    assert response.status_code == 201
    task = response.json()
    assert task["task_name"] == payload["task_name"]
    assert task["status"] == payload["status"]
    assert task["board_id"] == payload["board_id"]
    assert task["due_date"] == payload["due_date"]


@pytest.mark.asyncio
async def test_create_task_invalid_board(authenticated_ac: AsyncClient):
    """Тестирование создания задачи с несуществующей доской."""
    payload = {
        "task_name": "Invalid Task",
        "task_description": "Invalid board test",
        "status": "Запланировано",
        "due_date": (datetime.now(UTC) + timedelta(days=1)).isoformat(),
        "board_id": 999999
    }
    response = await authenticated_ac.post("/tasks/", json=payload)
    assert response.status_code == 404
    assert "доска не найдена" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_task_success(authenticated_ac: AsyncClient, test_task: Tasks, test_board: Boards):
    """Тестирование полного обновления задачи."""
    update_data = {
        "task_name": "Updated Task",
        "task_description": "Updated description",
        "status": "Готово",
        "due_date": (datetime.now(UTC) + timedelta(days=5)).isoformat(),
        "board_id": test_board.id
    }
    response = await authenticated_ac.put(f"/tasks/{test_task.id}", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["task_name"] == update_data["task_name"]
    assert updated_task["status"] == update_data["status"]
    assert updated_task["due_date"] == update_data["due_date"]


@pytest.mark.asyncio
async def test_update_task_status_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """Тестирование обновления только статуса задачи."""
    status_data = {"status": "Готово"}
    response = await authenticated_ac.patch(f"/tasks/{test_task.id}/status", json=status_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task["status"] == "Готово"
    assert updated_task["id"] == test_task.id


@pytest.mark.asyncio
async def test_update_task_status_invalid(authenticated_ac: AsyncClient, test_task: Tasks):
    """Тестирование обновления задачи с недопустимым статусом."""
    invalid_data = {"status": "Недопустимый"}
    response = await authenticated_ac.patch(f"/tasks/{test_task.id}/status", json=invalid_data)
    assert response.status_code == 400
    assert "допустимые значения" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_delete_task_success(authenticated_ac: AsyncClient, test_task: Tasks):
    """Тестирование удаления задачи."""
    response = await authenticated_ac.delete(f"/tasks/{test_task.id}")
    assert response.status_code == 204
    check_response = await authenticated_ac.get(f"/tasks/{test_task.id}")
    assert check_response.status_code == 404


@pytest.mark.asyncio
async def test_task_unauthorized_access(ac: AsyncClient, test_task: Tasks):
    """Тестирование доступа к задачам без авторизации."""
    response = await ac.get(f"/tasks/{test_task.id}")
    assert response.status_code == 401
    assert response.json()["detail"] == UnauthorizedException.detail
